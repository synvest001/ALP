import { mergeRecords } from './SyncMerge';
import { postText } from '../utils/http';

// Paste the deployed Google Apps Script web-app URL here (ends in /exec).
export const SYNC_ENDPOINT = 'PASTE_APPS_SCRIPT_URL_HERE';

export interface SyncResult { ok: boolean; message: string; changed: boolean; avatar?: string; }
export interface FamilyKid { kid: string; name: string; avatar: string; }

function cleanKid(n: string | null | undefined): string { return (n || 'default_player').toLowerCase().trim(); }
function k(kid: string, suffix: string): string { return 'alp_' + kid + '_' + suffix; }
function int(v: string | null): number { const n = parseInt(v || '0', 10); return isNaN(n) ? 0 : n; }
function parseObj(v: string | null): any {
  try { const o = v ? JSON.parse(v) : {}; return o && typeof o === 'object' ? o : {}; } catch (e) { return {}; }
}

export class SyncEngine {
  private static inFlight = false;
  private static lastRunAt = 0;

  public static getFamilyCode(): string { return (localStorage.getItem('alp_family_code') || '').trim().toLowerCase(); }
  public static setFamilyCode(code: string): void { localStorage.setItem('alp_family_code', code.trim().toLowerCase()); }
  public static endpointConfigured(): boolean { return SYNC_ENDPOINT.indexOf('PASTE_') !== 0; }
  public static isConfigured(): boolean { return SyncEngine.endpointConfigured() && SyncEngine.getFamilyCode().length >= 6; }
  public static shouldAutoSync(): boolean {
    return SyncEngine.isConfigured() && !SyncEngine.inFlight && Date.now() - SyncEngine.lastRunAt > 20000;
  }
  public static notConfiguredMessage(): string {
    if (!SyncEngine.endpointConfigured()) return 'Sync is not set up yet.';
    return 'Enter a family code in Account first.';
  }

  /** Call BEFORE clearing a child's local progress so a reset wins over older server data. */
  public static bumpEpoch(displayName: string): void {
    const kid = cleanKid(displayName);
    localStorage.setItem(k(kid, 'sync_epoch'), String(int(localStorage.getItem(k(kid, 'sync_epoch'))) + 1));
    localStorage.setItem(k(kid, 'sync_updated'), String(Date.now()));
  }

  private static buildLocal(kid: string, name: string, avatar: string): any {
    const syncedAvatar = localStorage.getItem(k(kid, 'synced_avatar'));
    let updated = int(localStorage.getItem(k(kid, 'sync_updated')));
    if (avatar && avatar !== syncedAvatar) updated = Date.now();
    return {
      v: 1, name: name, avatar: avatar,
      epoch: int(localStorage.getItem(k(kid, 'sync_epoch'))),
      nodes: int(localStorage.getItem(k(kid, 'nodes_completed'))),
      stars: int(localStorage.getItem(k(kid, 'stars'))),
      domain_counts: parseObj(localStorage.getItem(k(kid, 'domain_counts'))),
      quest: { date: localStorage.getItem(k(kid, 'daily_quest_date')) || '', count: int(localStorage.getItem(k(kid, 'daily_quest_count'))) },
      states: parseObj(localStorage.getItem(k(kid, 'assessment_states'))),
      updated: updated
    };
  }

  private static applyRecord(kid: string, rec: any, makeGlobalMirror: boolean): void {
    const nodes = String(rec.nodes || 0), stars = String(rec.stars || 0);
    const dc = JSON.stringify(rec.domain_counts || {});
    localStorage.setItem(k(kid, 'nodes_completed'), nodes);
    localStorage.setItem(k(kid, 'stars'), stars);
    localStorage.setItem(k(kid, 'domain_counts'), dc);
    if (makeGlobalMirror) {
      localStorage.setItem('alp_nodes_completed', nodes);
      localStorage.setItem('alp_stars', stars);
      localStorage.setItem('alp_domain_counts', dc);
    }
    localStorage.setItem(k(kid, 'assessment_states'), JSON.stringify(rec.states || {}));
    if (rec.quest && rec.quest.date) {
      localStorage.setItem(k(kid, 'daily_quest_date'), rec.quest.date);
      localStorage.setItem(k(kid, 'daily_quest_count'), String(rec.quest.count || 0));
    }
    localStorage.setItem(k(kid, 'sync_epoch'), String(rec.epoch || 0));
    localStorage.setItem(k(kid, 'synced_avatar'), rec.avatar || '');
    localStorage.setItem(k(kid, 'sync_updated'), String(rec.updated || 0));
  }

  private static post(payload: any): Promise<any> {
    return postText(SYNC_ENDPOINT, JSON.stringify(payload), 30000).then(function (text) {
      let data: any;
      try { data = JSON.parse(text); } catch (e) { throw new Error('Server reply was not JSON'); }
      if (!data || data.status !== 'success') throw new Error((data && data.message) || 'Server error');
      return data;
    });
  }

  /** Merge this child's progress with the server and store the result locally. */
  public static syncProfile(displayName: string, avatar: string): Promise<SyncResult> {
    if (!SyncEngine.isConfigured()) {
      return Promise.resolve({ ok: false, message: SyncEngine.notConfiguredMessage(), changed: false });
    }
    if (SyncEngine.inFlight) return Promise.resolve({ ok: false, message: 'Sync already running.', changed: false });
    SyncEngine.inFlight = true;
    const kid = cleanKid(displayName);
    const local = SyncEngine.buildLocal(kid, displayName, avatar);
    const before = JSON.stringify([local.nodes, local.stars, local.states, local.domain_counts, local.quest, local.epoch]);
    const isCurrent = cleanKid(localStorage.getItem('alp_current_name')) === kid;
    return SyncEngine.post({ action: 'sync', family: SyncEngine.getFamilyCode(), kid: kid, record: local })
      .then(function (data) {
        const merged = mergeRecords(local, data.record);
        SyncEngine.applyRecord(kid, merged, isCurrent);
        const after = JSON.stringify([merged.nodes, merged.stars, merged.states, merged.domain_counts, merged.quest, merged.epoch]);
        return { ok: true, message: 'Synced', changed: before !== after, avatar: merged.avatar } as SyncResult;
      })
      .catch(function (e: any) {
        return { ok: false, message: String(e && e.message ? e.message : e), changed: false } as SyncResult;
      })
      .then(function (res) { SyncEngine.inFlight = false; SyncEngine.lastRunAt = Date.now(); return res; });
  }

  /** List the children stored under this family code (for adding them on a new device). */
  public static listKids(): Promise<{ ok: boolean; message: string; kids: FamilyKid[] }> {
    if (!SyncEngine.isConfigured()) return Promise.resolve({ ok: false, message: SyncEngine.notConfiguredMessage(), kids: [] });
    return SyncEngine.post({ action: 'list', family: SyncEngine.getFamilyCode() })
      .then(function (data) { return { ok: true, message: 'OK', kids: (data.kids || []) as FamilyKid[] }; })
      .catch(function (e: any) { return { ok: false, message: String(e && e.message ? e.message : e), kids: [] as FamilyKid[] }; });
  }
}

/** Sync the currently selected child; applies a changed avatar via the ProfileSwitcher. */
export function syncCurrentPlayer(app: any): Promise<SyncResult> {
  const ps = app && app.profileSwitcher;
  const name: string | null = ps ? ps.getCurrentPlayerName() : null;
  if (!name) return Promise.resolve({ ok: false, message: 'No child selected.', changed: false });
  const avatar: string = ps.getCurrentAvatar() || 'princess';
  return SyncEngine.syncProfile(name, avatar).then(function (res) {
    if (res.ok && res.avatar && res.avatar !== avatar) { ps.changeAvatar(res.avatar); res.changed = true; }
    return res;
  });
}
