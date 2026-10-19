import { ALPEvent, ALPBaseEvent } from './EventTypes';
import { SubskillState } from './AssessmentEngine';

var CHUNK_SIZE_LIMIT = 40000; // ~40 KB in characters
var THREE_MB = 3 * 1024 * 1024;

export class EventLog {
  /** Return or generate a persistent 12-char random hex device ID. */
  public static getDeviceId(): string {
    var id = localStorage.getItem('alp_device_id');
    if (!id || id.length !== 12) {
      var hexChars = '0123456789abcdef';
      id = '';
      for (var i = 0; i < 12; i++) {
        id += hexChars.charAt(Math.floor(Math.random() * 16));
      }
      localStorage.setItem('alp_device_id', id);
    }
    return id;
  }

  /** Return the next persistent integer sequence for this device. Never reuses a seq. */
  public static nextDeviceSeq(): number {
    var raw = localStorage.getItem('alp_device_seq');
    var seq = parseInt(raw || '0', 10);
    if (isNaN(seq) || seq < 0) {
      seq = 0;
    }
    seq += 1;
    localStorage.setItem('alp_device_seq', String(seq));
    return seq;
  }

  private static cleanKid(kid: string): string {
    return (kid || 'default_player').toLowerCase().trim();
  }

  private static metaKey(kid: string): string {
    return 'alp_' + EventLog.cleanKid(kid) + '_ev_meta';
  }

  private static chunkKey(kid: string, index: number): string {
    return 'alp_' + EventLog.cleanKid(kid) + '_ev_' + index;
  }

  private static getMeta(kid: string): { count: number } {
    try {
      var raw = localStorage.getItem(EventLog.metaKey(kid));
      if (raw) {
        var parsed = JSON.parse(raw);
        if (parsed && typeof parsed.count === 'number') {
          return parsed;
        }
      }
    } catch (e) {}
    return { count: 0 };
  }

  private static saveMeta(kid: string, meta: { count: number }): void {
    localStorage.setItem(EventLog.metaKey(kid), JSON.stringify(meta));
  }

  /** Append a single event immediately to the kid's chunked log. */
  public static appendEvent(kid: string, ev: ALPEvent): void {
    var clean = EventLog.cleanKid(kid);
    var meta = EventLog.getMeta(clean);

    if (meta.count === 0) {
      // First chunk
      var initialChunk = [ev];
      localStorage.setItem(EventLog.chunkKey(clean, 0), JSON.stringify(initialChunk));
      meta.count = 1;
      EventLog.saveMeta(clean, meta);
      return;
    }

    var currentIndex = meta.count - 1;
    var currentKey = EventLog.chunkKey(clean, currentIndex);
    var chunk: ALPEvent[] = [];
    try {
      var raw = localStorage.getItem(currentKey);
      if (raw) {
        chunk = JSON.parse(raw);
      }
    } catch (e) {
      chunk = [];
    }

    // Check if adding the event fits within ~40 KB
    chunk.push(ev);
    var serialized = JSON.stringify(chunk);

    if (serialized.length > CHUNK_SIZE_LIMIT && chunk.length > 1) {
      // Current chunk is full; remove the event and start a new chunk
      chunk.pop();
      localStorage.setItem(currentKey, JSON.stringify(chunk));

      var newChunk = [ev];
      var newIndex = meta.count;
      localStorage.setItem(EventLog.chunkKey(clean, newIndex), JSON.stringify(newChunk));
      meta.count += 1;
      EventLog.saveMeta(clean, meta);
    } else {
      localStorage.setItem(currentKey, serialized);
    }
  }

  /** Read all events sequentially across chunks without holding extra buffers. */
  public static getEvents(kid: string): ALPEvent[] {
    var clean = EventLog.cleanKid(kid);
    var meta = EventLog.getMeta(clean);
    var all: ALPEvent[] = [];

    for (var i = 0; i < meta.count; i++) {
      var raw = localStorage.getItem(EventLog.chunkKey(clean, i));
      if (raw) {
        try {
          var chunk: ALPEvent[] = JSON.parse(raw);
          if (chunk && chunk.length) {
            for (var j = 0; j < chunk.length; j++) {
              all.push(chunk[j]);
            }
          }
        } catch (e) {
          console.error('[EventLog] Error reading chunk ' + i + ' for ' + clean, e);
        }
      }
    }
    return all;
  }

  /** Total number of events logged for a child. */
  public static getEventCount(kid: string): number {
    var events = EventLog.getEvents(kid);
    return events.length;
  }

  /** Calculate total bytes stored in chunk keys for this kid. */
  public static getTotalBytes(kid: string): number {
    var clean = EventLog.cleanKid(kid);
    var meta = EventLog.getMeta(clean);
    var total = 0;

    for (var i = 0; i < meta.count; i++) {
      var raw = localStorage.getItem(EventLog.chunkKey(clean, i));
      if (raw) {
        total += raw.length;
      }
    }
    return total;
  }

  /** Returns true if the kid's event log exceeds 3 MB. */
  public static isOver3MB(kid: string): boolean {
    return EventLog.getTotalBytes(kid) > THREE_MB;
  }

  /**
   * Union incoming events into the child's local log.
   * Deduplicates by event ID (ev.i) so no duplicates are stored.
   */
  public static unionEvents(kid: string, incoming: ALPEvent[]): number {
    var clean = EventLog.cleanKid(kid);
    var existing = EventLog.getEvents(clean);
    var seen: { [id: string]: boolean } = {};
    for (var i = 0; i < existing.length; i++) {
      if (existing[i] && existing[i].i) {
        seen[existing[i].i] = true;
      }
    }

    var added = 0;
    for (var j = 0; j < incoming.length; j++) {
      var ev = incoming[j];
      if (ev && ev.i && !seen[ev.i]) {
        seen[ev.i] = true;
        EventLog.appendEvent(clean, ev);
        added++;
      }
    }
    return added;
  }

  /** Delete all chunk keys and metadata for a kid. */
  public static clearKidLog(kid: string): void {
    var clean = EventLog.cleanKid(kid);
    var meta = EventLog.getMeta(clean);

    for (var i = 0; i < meta.count; i++) {
      localStorage.removeItem(EventLog.chunkKey(clean, i));
    }
    localStorage.removeItem(EventLog.metaKey(clean));
  }

  /**
   * One-time legacy baseline initialization:
   * If kid has pre-existing progress states but no events, writes a "base" event.
   */
  public static initKidLog(kid: string, currentEpoch: number, existingStates?: { [subskill_id: string]: SubskillState }): void {
    var clean = EventLog.cleanKid(kid);
    var count = EventLog.getEventCount(clean);
    if (count > 0) return;

    // Check for pre-existing states
    var states = existingStates;
    if (!states) {
      try {
        var raw = localStorage.getItem('alp_' + clean + '_assessment_states');
        if (!raw && clean === 'default_player') {
          raw = localStorage.getItem('alp_assessment_states');
        }
        if (raw) {
          states = JSON.parse(raw);
        }
      } catch (e) {}
    }

    if (states && Object.keys(states).length > 0) {
      var devId = EventLog.getDeviceId();
      var seq = EventLog.nextDeviceSeq();
      var baseEvent: ALPBaseEvent = {
        i: devId + '-' + seq,
        d: devId,
        q: seq,
        t: Date.now(),
        y: 'base',
        ep: currentEpoch,
        states: states
      };
      EventLog.appendEvent(clean, baseEvent);
    }
  }
}
