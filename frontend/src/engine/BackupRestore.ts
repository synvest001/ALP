import { ALPEvent } from './EventTypes';
import { EventLog } from './EventLog';
import { SyncEngine } from './SyncEngine';
import { ClassBProfile, mergeRecords } from './SyncMerge';
import { replay } from './AssessmentEngine';
import { sha256 } from '../utils/sha256';

export interface BackupPayload {
  format: 'alp-backup';
  v: 1;
  kid: string;
  exportedUtc: string;
  eventCount: number;
  checksum: string;
  profile: ClassBProfile;
  events: ALPEvent[];
}

export interface EncryptedBackupPayload {
  format: 'alp-backup';
  v: 1;
  encrypted: true;
  salt: string;
  iv: string;
  ciphertext: string;
}

export interface RestoreResult {
  success: boolean;
  message: string;
  kid: string;
}

export interface ExportResult {
  text: string;
  encrypted: boolean;
  notice: string;
  payload: BackupPayload | EncryptedBackupPayload;
}

function getSubtleCrypto(): any {
  if (typeof window !== 'undefined' && window.crypto) {
    if (window.crypto.subtle) return window.crypto.subtle;
    if ((window.crypto as any).webkitSubtle) return (window.crypto as any).webkitSubtle;
  }
  if (typeof globalThis !== 'undefined' && (globalThis as any).crypto && (globalThis as any).crypto.subtle) {
    return (globalThis as any).crypto.subtle;
  }
  return null;
}

function bytesToHex(bytes: Uint8Array): string {
  var hex = '';
  for (var i = 0; i < bytes.length; i++) {
    var h = bytes[i].toString(16);
    if (h.length < 2) h = '0' + h;
    hex += h;
  }
  return hex;
}

function hexToBytes(hex: string): Uint8Array {
  var bytes = new Uint8Array(hex.length / 2);
  for (var i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substr(i, 2), 16);
  }
  return bytes;
}

function strToUtf8(str: string): Uint8Array {
  var utf8: number[] = [];
  for (var i = 0; i < str.length; i++) {
    var charcode = str.charCodeAt(i);
    if (charcode < 0x80) {
      utf8.push(charcode);
    } else if (charcode < 0x800) {
      utf8.push(0xc0 | (charcode >> 6), 0x80 | (charcode & 0x3f));
    } else if (charcode < 0xd800 || charcode >= 0xe000) {
      utf8.push(0xe0 | (charcode >> 12), 0x80 | ((charcode >> 6) & 0x3f), 0x80 | (charcode & 0x3f));
    } else {
      i++;
      charcode = 0x10000 + (((charcode & 0x3ff) << 10) | (str.charCodeAt(i) & 0x3ff));
      utf8.push(
        0xf0 | (charcode >> 18),
        0x80 | ((charcode >> 12) & 0x3f),
        0x80 | ((charcode >> 6) & 0x3f),
        0x80 | (charcode & 0x3f)
      );
    }
  }
  return new Uint8Array(utf8);
}

function utf8ToStr(bytes: Uint8Array): string {
  var out = '';
  var i = 0;
  while (i < bytes.length) {
    var c = bytes[i++];
    if (c < 128) {
      out += String.fromCharCode(c);
    } else if (c > 191 && c < 224) {
      var c2 = bytes[i++];
      out += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
    } else if (c > 223 && c < 240) {
      var c2 = bytes[i++];
      var c3 = bytes[i++];
      out += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
    } else {
      var c2 = bytes[i++];
      var c3 = bytes[i++];
      var c4 = bytes[i++];
      var u = (((c & 7) << 18) | ((c2 & 63) << 12) | ((c3 & 63) << 6) | (c4 & 63)) - 0x10000;
      out += String.fromCharCode(0xd800 + (u >> 10), 0xdc00 + (u & 0x3ff));
    }
  }
  return out;
}

export function isWebCryptoAvailable(): boolean {
  return getSubtleCrypto() !== null;
}

/**
 * Computes canonical SHA-256 checksum of an event array sorted by (d, q).
 * Matches server handleExportCheck algorithm exactly.
 */
export function computeBackupChecksum(events: ALPEvent[]): string {
  var sorted = (events || []).slice();
  sorted.sort(function (a, b) {
    var da = String(a.d || '');
    var db = String(b.d || '');
    if (da !== db) return da < db ? -1 : 1;
    return (a.q || 0) - (b.q || 0);
  });
  return sha256(JSON.stringify(sorted));
}

/**
 * Builds the unencrypted Class A + B backup payload.
 */
export function buildBackupPayload(kid: string, name?: string, avatar?: string): BackupPayload {
  var clean = (kid || 'default_player').toLowerCase().trim();
  var profile = SyncEngine.buildLocal(clean, name || clean, avatar || 'princess');
  var events = EventLog.getEvents(clean);
  var checksum = computeBackupChecksum(events);

  return {
    format: 'alp-backup',
    v: 1,
    kid: clean,
    exportedUtc: new Date().toISOString(),
    eventCount: events.length,
    checksum: checksum,
    profile: profile,
    events: events
  };
}

/**
 * Validates backup structure, version, and SHA-256 checksum before applying.
 */
export function validateBackupPayload(data: any): { valid: boolean; message?: string } {
  if (!data || typeof data !== 'object') {
    return { valid: false, message: 'This backup file looks damaged. Nothing was changed.' };
  }
  if (data.format !== 'alp-backup' || data.v !== 1) {
    return { valid: false, message: 'This backup file looks damaged. Nothing was changed.' };
  }
  if (!Array.isArray(data.events)) {
    return { valid: false, message: 'This backup file looks damaged. Nothing was changed.' };
  }
  if (typeof data.checksum !== 'string' || !data.checksum) {
    return { valid: false, message: 'This backup file looks damaged. Nothing was changed.' };
  }

  var expectedChecksum = computeBackupChecksum(data.events);
  if (expectedChecksum !== data.checksum) {
    return { valid: false, message: 'This backup file looks damaged. Nothing was changed.' };
  }

  return { valid: true };
}

/**
 * Encrypts a backup payload with PBKDF2 + AES-GCM via Web Crypto.
 */
export function encryptPayload(payload: BackupPayload, passphrase: string): Promise<EncryptedBackupPayload> {
  var subtle = getSubtleCrypto();
  if (!subtle) {
    return Promise.reject(new Error('Web Crypto subtle is not available'));
  }

  var pwBytes = strToUtf8(passphrase);
  var jsonStr = JSON.stringify(payload);
  var plaintextBytes = strToUtf8(jsonStr);

  var cryptoObj = (typeof window !== 'undefined' && window.crypto) || (globalThis as any).crypto;
  var salt = new Uint8Array(16);
  cryptoObj.getRandomValues(salt);
  var iv = new Uint8Array(12);
  cryptoObj.getRandomValues(iv);

  return subtle
    .importKey('raw', pwBytes, { name: 'PBKDF2' }, false, ['deriveKey'])
    .then(function (baseKey: any) {
      return subtle.deriveKey(
        {
          name: 'PBKDF2',
          salt: salt,
          iterations: 10000,
          hash: 'SHA-256'
        },
        baseKey,
        { name: 'AES-GCM', length: 256 },
        false,
        ['encrypt']
      );
    })
    .then(function (aesKey: any) {
      return subtle.encrypt({ name: 'AES-GCM', iv: iv }, aesKey, plaintextBytes);
    })
    .then(function (cipherBuffer: ArrayBuffer) {
      return {
        format: 'alp-backup',
        v: 1,
        encrypted: true,
        salt: bytesToHex(salt),
        iv: bytesToHex(iv),
        ciphertext: bytesToHex(new Uint8Array(cipherBuffer))
      } as EncryptedBackupPayload;
    });
}

/**
 * Decrypts an encrypted backup payload using PBKDF2 + AES-GCM.
 */
export function decryptPayload(encrypted: EncryptedBackupPayload, passphrase: string): Promise<BackupPayload> {
  var subtle = getSubtleCrypto();
  if (!subtle) {
    return Promise.reject(new Error('Web Crypto subtle is not available'));
  }

  var pwBytes = strToUtf8(passphrase);
  var salt = hexToBytes(encrypted.salt);
  var iv = hexToBytes(encrypted.iv);
  var ciphertext = hexToBytes(encrypted.ciphertext);

  return subtle
    .importKey('raw', pwBytes, { name: 'PBKDF2' }, false, ['deriveKey'])
    .then(function (baseKey: any) {
      return subtle.deriveKey(
        {
          name: 'PBKDF2',
          salt: salt,
          iterations: 10000,
          hash: 'SHA-256'
        },
        baseKey,
        { name: 'AES-GCM', length: 256 },
        false,
        ['decrypt']
      );
    })
    .then(function (aesKey: any) {
      return subtle.decrypt({ name: 'AES-GCM', iv: iv }, aesKey, ciphertext);
    })
    .then(function (decryptedBuffer: ArrayBuffer) {
      var decryptedStr = utf8ToStr(new Uint8Array(decryptedBuffer));
      var parsed = JSON.parse(decryptedStr);
      return parsed as BackupPayload;
    });
}

/**
 * High-level export generator. Encrypts if passphrase given and Web Crypto available;
 * otherwise exports unencrypted with notice "This file is not password-protected.".
 */
export function exportBackup(kid: string, passphrase?: string, name?: string, avatar?: string): Promise<ExportResult> {
  var payload = buildBackupPayload(kid, name, avatar);
  var pass = String(passphrase || '').trim();

  if (pass && isWebCryptoAvailable()) {
    return encryptPayload(payload, pass).then(function (enc) {
      return {
        text: JSON.stringify(enc, null, 2),
        encrypted: true,
        notice: 'This file is encrypted with your passphrase.',
        payload: enc
      };
    });
  }

  return Promise.resolve({
    text: JSON.stringify(payload, null, 2),
    encrypted: false,
    notice: 'This file is not password-protected.',
    payload: payload
  });
}

/**
 * Merges backup into local state:
 * 1. Validates format, v, checksum.
 * 2. Merges Class B record via mergeRecords (respecting epoch precedence).
 * 3. Unions events into EventLog by ID (never overwrites).
 * 4. Replays all events with explicit localNow and merged epoch to refresh derived states.
 */
export function restoreBackup(
  payload: BackupPayload,
  localNow: number,
  activeKidName?: string
): RestoreResult {
  if (typeof localNow !== 'number' || isNaN(localNow)) {
    throw new Error('restoreBackup requires an explicit localNow timestamp');
  }

  var validation = validateBackupPayload(payload);
  if (!validation.valid) {
    return {
      success: false,
      message: validation.message || 'This backup file looks damaged. Nothing was changed.',
      kid: payload && payload.kid ? payload.kid : ''
    };
  }

  var kid = (payload.kid || 'default_player').toLowerCase().trim();

  // 1. Read existing local Class B profile
  var localName = kid;
  var localAvatar = 'princess';
  var rawProfiles = localStorage.getItem('alp_profiles');
  var profilesList: any[] = [];
  if (rawProfiles) {
    try {
      profilesList = JSON.parse(rawProfiles);
    } catch (e) {
      profilesList = [];
    }
  }
  for (var p = 0; p < profilesList.length; p++) {
    if (profilesList[p] && String(profilesList[p].name).toLowerCase().trim() === kid) {
      localName = profilesList[p].name;
      localAvatar = profilesList[p].avatar || 'princess';
      break;
    }
  }

  var localProfile = SyncEngine.buildLocal(kid, localName, localAvatar);

  // 2. Class B merge
  var mergedProfile = mergeRecords(localProfile, payload.profile);
  var isCurrentKid = !activeKidName || activeKidName.toLowerCase().trim() === kid;
  SyncEngine.applyRecord(kid, mergedProfile, isCurrentKid);

  // Ensure kid is in saved profiles list
  var exists = false;
  for (var ep = 0; ep < profilesList.length; ep++) {
    if (profilesList[ep] && String(profilesList[ep].name).toLowerCase().trim() === kid) {
      profilesList[ep].name = mergedProfile.name || localName;
      profilesList[ep].avatar = mergedProfile.avatar || localAvatar;
      exists = true;
      break;
    }
  }
  if (!exists) {
    profilesList.push({
      name: mergedProfile.name || kid,
      avatar: mergedProfile.avatar || 'princess'
    });
  }
  localStorage.setItem('alp_profiles', JSON.stringify(profilesList));

  // 3. Event Log merge: union by event ID (ev.i)
  EventLog.unionEvents(kid, payload.events || []);

  // 4. Replay from the unioned event log with explicit localNow and merged epoch
  var currentEpoch = mergedProfile ? (mergedProfile.epoch || 0) : 0;
  var allEvents = EventLog.getEvents(kid);
  var refreshedStates = replay(allEvents, currentEpoch, localNow);
  var serializedStates = JSON.stringify(refreshedStates);
  localStorage.setItem('alp_' + kid + '_assessment_states', serializedStates);
  if (kid === 'default_player') {
    localStorage.setItem('alp_assessment_states', serializedStates);
  }

  return {
    success: true,
    message: 'Everything is saved.',
    kid: kid
  };
}
