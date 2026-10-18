import { mergeRecords, ClassBProfile } from './SyncMerge';
import { postText } from '../utils/http';
import { sha256 } from '../utils/sha256';
import { EventLog } from './EventLog';
import { ALPEvent } from './EventTypes';
import { replay } from './AssessmentEngine';

// Paste the deployed Google Apps Script web-app URL here (ends in /exec).
export const SYNC_ENDPOINT = 'https://script.google.com/macros/s/AKfycbxwVDcBy1wzT_JRK4Vff9UWjWli7BwS5w-8p2WrbUhtoaRANyIhMnr5S7q31-WLr78I7Q/exec';

export interface SyncResult {
  ok: boolean;
  message: string;
  changed: boolean;
  avatar?: string;
  tombstoned?: boolean;
}

export interface FamilyKid {
  kid: string;
  name: string;
  avatar: string;
  tombstoned?: boolean;
  deleted_ms?: number;
}

function cleanKid(n: string | null | undefined): string {
  return (n || 'default_player').toLowerCase().trim();
}

function k(kid: string, suffix: string): string {
  return 'alp_' + kid + '_' + suffix;
}

function int(v: string | null): number {
  var n = parseInt(v || '0', 10);
  return isNaN(n) ? 0 : n;
}

function parseObj(v: string | null): any {
  try {
    var o = v ? JSON.parse(v) : {};
    return o && typeof o === 'object' ? o : {};
  } catch (e) {
    return {};
  }
}

export class SyncEngine {
  private static inFlight = false;
  private static lastRunAt = 0;

  public static getFamilyCode(): string {
    return (localStorage.getItem('alp_family_code') || '').trim().toLowerCase();
  }

  public static setFamilyCode(code: string): void {
    localStorage.setItem('alp_family_code', code.trim().toLowerCase());
  }

  public static endpointConfigured(): boolean {
    return SYNC_ENDPOINT.indexOf('PASTE_') !== 0;
  }

  public static isConfigured(): boolean {
    return SyncEngine.endpointConfigured() && SyncEngine.getFamilyCode().length >= 8;
  }

  public static shouldAutoSync(): boolean {
    return SyncEngine.isConfigured() && !SyncEngine.inFlight && Date.now() - SyncEngine.lastRunAt > 20000;
  }

  public static notConfiguredMessage(): string {
    if (!SyncEngine.endpointConfigured()) return "Sync isn't set up yet.";
    return "Sync isn't set up yet.";
  }

  /** Call BEFORE clearing a child's local progress so a reset wins over older server data. */
  public static bumpEpoch(displayName: string): void {
    var kid = cleanKid(displayName);
    var nextEpoch = int(localStorage.getItem(k(kid, 'sync_epoch'))) + 1;
    localStorage.setItem(k(kid, 'sync_epoch'), String(nextEpoch));
    localStorage.setItem(k(kid, 'sync_updated'), String(Date.now()));
  }

  /** Class B profile only. Does NOT hold or sync derived per-skill states. */
  private static buildLocal(kid: string, name: string, avatar: string): ClassBProfile {
    var syncedAvatar = localStorage.getItem(k(kid, 'synced_avatar'));
    var updated = int(localStorage.getItem(k(kid, 'sync_updated')));
    if (avatar && avatar !== syncedAvatar) updated = Date.now();
    return {
      v: 1,
      name: name,
      avatar: avatar,
      epoch: int(localStorage.getItem(k(kid, 'sync_epoch'))),
      nodes: int(localStorage.getItem(k(kid, 'nodes_completed'))),
      stars: int(localStorage.getItem(k(kid, 'stars'))),
      domain_counts: parseObj(localStorage.getItem(k(kid, 'domain_counts'))),
      quest: {
        date: localStorage.getItem(k(kid, 'daily_quest_date')) || '',
        count: int(localStorage.getItem(k(kid, 'daily_quest_count')))
      },
      updated: updated
    };
  }

  private static applyRecord(kid: string, rec: any, makeGlobalMirror: boolean): void {
    if (!rec) return;
    var nodes = String(rec.nodes || 0);
    var stars = String(rec.stars || 0);
    var dc = JSON.stringify(rec.domain_counts || {});
    localStorage.setItem(k(kid, 'nodes_completed'), nodes);
    localStorage.setItem(k(kid, 'stars'), stars);
    localStorage.setItem(k(kid, 'domain_counts'), dc);
    if (makeGlobalMirror) {
      localStorage.setItem('alp_nodes_completed', nodes);
      localStorage.setItem('alp_stars', stars);
      localStorage.setItem('alp_domain_counts', dc);
    }
    if (rec.quest && rec.quest.date) {
      localStorage.setItem(k(kid, 'daily_quest_date'), rec.quest.date);
      localStorage.setItem(k(kid, 'daily_quest_count'), String(rec.quest.count || 0));
    }
    localStorage.setItem(k(kid, 'sync_epoch'), String(rec.epoch || 0));
    localStorage.setItem(k(kid, 'synced_avatar'), rec.avatar || '');
    localStorage.setItem(k(kid, 'sync_updated'), String(rec.updated || 0));
  }

  private static post(payload: any): Promise<any> {
    return postText(SYNC_ENDPOINT, JSON.stringify(payload), 15000).then(function (text) {
      var data: any;
      try {
        data = JSON.parse(text);
      } catch (e) {
        throw new Error("Couldn't reach the server. Your progress is safe on this device.");
      }
      if (!data || data.status !== 'success') {
        throw new Error("Couldn't reach the server. Your progress is safe on this device.");
      }
      return data;
    });
  }

  /**
   * Sync child progress: push unsynced Class A events, pull other devices' events,
   * merge Class B profile, and replay the merged log to refresh cached state.
   */
  public static syncProfile(displayName: string, avatar: string): Promise<SyncResult> {
    if (!SyncEngine.isConfigured()) {
      return Promise.resolve({
        ok: false,
        message: SyncEngine.notConfiguredMessage(),
        changed: false
      });
    }

    if (SyncEngine.inFlight) {
      return Promise.resolve({
        ok: false,
        message: 'Syncing...',
        changed: false
      });
    }

    SyncEngine.inFlight = true;
    var kid = cleanKid(displayName);
    var famHash = sha256(SyncEngine.getFamilyCode());
    var localProfile = SyncEngine.buildLocal(kid, displayName, avatar);
    var isCurrent = cleanKid(localStorage.getItem('alp_current_name')) === kid;

    var clientVec = parseObj(localStorage.getItem(k(kid, 'sync_vec')));
    var allLocalEvents = EventLog.getEvents(kid);
    var unsyncedEvents: ALPEvent[] = [];

    for (var i = 0; i < allLocalEvents.length; i++) {
      var ev = allLocalEvents[i];
      var knownSeq = Number(clientVec[ev.d]) || 0;
      if (ev.q > knownSeq) {
        unsyncedEvents.push(ev);
      }
    }

    // Build map of locally existing event IDs to avoid duplicates on pull
    var localEventIds: { [id: string]: boolean } = {};
    for (var j = 0; j < allLocalEvents.length; j++) {
      localEventIds[allLocalEvents[j].i] = true;
    }

    function doSyncLoop(eventsToSend: ALPEvent[]): Promise<any> {
      var payload = {
        action: 'sync',
        fam: famHash,
        kid: kid,
        vec: clientVec,
        events: eventsToSend,
        profile: localProfile
      };

      return SyncEngine.post(payload).then(function (data) {
        if (data.tombstoned) {
          return { tombstoned: true, changed: false, profile: localProfile };
        }

        var incoming = data.events || [];
        var newEventsAdded = 0;

        for (var idx = 0; idx < incoming.length; idx++) {
          var inEv: ALPEvent = incoming[idx];
          if (!localEventIds[inEv.i]) {
            localEventIds[inEv.i] = true;
            EventLog.appendEvent(kid, inEv);
            newEventsAdded++;
          }
          if (!clientVec[inEv.d] || inEv.q > clientVec[inEv.d]) {
            clientVec[inEv.d] = inEv.q;
          }
        }

        // Incorporate server max sequence vector
        var sVec = data.serverVec || {};
        for (var dev in sVec) {
          if (Object.prototype.hasOwnProperty.call(sVec, dev)) {
            clientVec[dev] = Math.max(Number(clientVec[dev]) || 0, Number(sVec[dev]) || 0);
          }
        }

        localStorage.setItem(k(kid, 'sync_vec'), JSON.stringify(clientVec));

        if (data.profile) {
          var merged = mergeRecords(localProfile, data.profile);
          SyncEngine.applyRecord(kid, merged, isCurrent);
          localProfile = merged;
        }

        if (data.more) {
          // Loop to retrieve the remaining batches; no need to re-send pushed events
          return doSyncLoop([]).then(function (nextRes) {
            return {
              tombstoned: nextRes.tombstoned,
              changed: nextRes.changed || newEventsAdded > 0,
              profile: localProfile
            };
          });
        }

        return {
          tombstoned: false,
          changed: newEventsAdded > 0,
          profile: localProfile
        };
      });
    }

    return doSyncLoop(unsyncedEvents)
      .then(function (loopResult) {
        if (loopResult.tombstoned) {
          return {
            ok: true,
            tombstoned: true,
            message: "Saved on this device. It will sync when you're online.",
            changed: false
          } as SyncResult;
        }

        // Replay merged event log to refresh cached assessment states with explicit localNow
        var currentEpoch = int(localStorage.getItem(k(kid, 'sync_epoch')));
        var fullLog = EventLog.getEvents(kid);
        var refreshedStates = replay(fullLog, currentEpoch, Date.now());
        var serializedStates = JSON.stringify(refreshedStates);

        localStorage.setItem(k(kid, 'assessment_states'), serializedStates);
        if (isCurrent) {
          localStorage.setItem('alp_assessment_states', serializedStates);
        }

        return {
          ok: true,
          message: 'Everything is saved.',
          changed: loopResult.changed,
          avatar: loopResult.profile ? loopResult.profile.avatar : avatar
        } as SyncResult;
      })
      .catch(function () {
        // Fails silently into offline status
        return {
          ok: false,
          message: "Saved on this device. It will sync when you're online.",
          changed: false
        } as SyncResult;
      })
      .then(function (res) {
        SyncEngine.inFlight = false;
        SyncEngine.lastRunAt = Date.now();
        return res;
      });
  }

  /** List the children stored under this family code (for adding them on a new device). */
  public static listKids(): Promise<{ ok: boolean; message: string; kids: FamilyKid[] }> {
    if (!SyncEngine.isConfigured()) {
      return Promise.resolve({
        ok: false,
        message: SyncEngine.notConfiguredMessage(),
        kids: []
      });
    }

    var famHash = sha256(SyncEngine.getFamilyCode());
    return SyncEngine.post({ action: 'list', fam: famHash })
      .then(function (data) {
        return {
          ok: true,
          message: 'Everything is saved.',
          kids: (data.kids || []) as FamilyKid[]
        };
      })
      .catch(function () {
        return {
          ok: false,
          message: "Saved on this device. It will sync when you're online.",
          kids: [] as FamilyKid[]
        };
      });
  }

  /** Delete kid on server and write a server tombstone. */
  public static deleteKid(kidName: string): Promise<boolean> {
    if (!SyncEngine.isConfigured()) return Promise.resolve(false);
    var famHash = sha256(SyncEngine.getFamilyCode());
    var kid = cleanKid(kidName);
    return SyncEngine.post({ action: 'delete_kid', fam: famHash, kid: kid })
      .then(function () {
        return true;
      })
      .catch(function () {
        return false;
      });
  }

  /** Export verification check from server. */
  public static exportCheck(kidName: string): Promise<{ ok: boolean; eventCount: number; checksum: string }> {
    if (!SyncEngine.isConfigured()) return Promise.resolve({ ok: false, eventCount: 0, checksum: '' });
    var famHash = sha256(SyncEngine.getFamilyCode());
    var kid = cleanKid(kidName);
    return SyncEngine.post({ action: 'export_check', fam: famHash, kid: kid })
      .then(function (data) {
        return {
          ok: true,
          eventCount: Number(data.eventCount) || 0,
          checksum: String(data.checksum || '')
        };
      })
      .catch(function () {
        return { ok: false, eventCount: 0, checksum: '' };
      });
  }
}

/** Sync the currently selected child; applies a changed avatar via the ProfileSwitcher. */
export function syncCurrentPlayer(app: any): Promise<SyncResult> {
  var ps = app && app.profileSwitcher;
  var name: string | null = ps ? ps.getCurrentPlayerName() : null;
  if (!name) return Promise.resolve({ ok: false, message: 'No child selected.', changed: false });
  var avatar: string = ps.getCurrentAvatar() || 'princess';
  return SyncEngine.syncProfile(name, avatar).then(function (res) {
    if (res.ok && res.avatar && res.avatar !== avatar) {
      ps.changeAvatar(res.avatar);
      res.changed = true;
    }
    return res;
  });
}
