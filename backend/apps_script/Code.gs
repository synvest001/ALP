// Google Apps Script (GAS) API Endpoint for ALP Sync & Backup
// Deploy steps:
// 1. Extensions > Apps Script in Google Sheets.
// 2. Paste this file into Code.gs.
// 3. Deploy > New deployment > Web app (Execute as: Me, Who has access: Anyone).
// 4. Daily Snapshot Setup (in Apps Script Editor):
//    a. In the left navigation bar, click the clock icon: "Triggers".
//    b. Click "+ Add Trigger" (bottom right).
//    c. Choose which function to run: "runDailySnapshot".
//    d. Choose which deployment should run: "Head".
//    e. Select event source: "Time-driven".
//    f. Select type of time based trigger: "Day timer".
//    g. Select time of day: "1am to 2am" (or preferred hour).
//    h. Click "Save".
//    Note: Snapshots retain the last 7 daily tabs (events_snap_YYYYMMDD). To restore a snapshot,
//    the spreadsheet owner manually copies the desired snapshot tab back to the 'events' tab.

var SNAPSHOT_KEEP = 7;

/**
 * Top-level entrypoint for Apps Script Time-driven trigger.
 * Can also be run manually from the Apps Script code editor.
 */
function runDailySnapshot() {
  var sheetAccess = getSheetAccess();
  var nowMs = Date.now();
  return handleSnapshot(sheetAccess, nowMs);
}

function getSheetAccess(ss) {
  if (!ss) {
    ss = SpreadsheetApp.getActiveSpreadsheet();
  }
  return {
    getOrCreateSheet: function (name, headers) {
      var sheet = ss.getSheetByName(name);
      if (!sheet) {
        sheet = ss.insertSheet(name);
        if (headers && headers.length) {
          sheet.appendRow(headers);
        }
      }
      return sheet;
    },
    getSheet: function (name) {
      return ss.getSheetByName(name);
    },
    getAllSheets: function () {
      return ss.getSheets();
    },
    deleteSheet: function (sheet) {
      ss.deleteSheet(sheet);
    }
  };
}

function doGet() {
  return ContentService.createTextOutput(JSON.stringify({ status: 'success', message: 'ALP sync server is running' }))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
  } catch (lockError) {
    return ContentService.createTextOutput(JSON.stringify({ status: 'error', message: "Couldn't reach the server. Your progress is safe on this device." }))
      .setMimeType(ContentService.MimeType.JSON);
  }

  try {
    var contents = (e && e.postData && e.postData.contents) ? e.postData.contents : '';
    var req = {};
    try {
      req = JSON.parse(contents || '{}');
    } catch (parseEx) {
      return ContentService.createTextOutput(JSON.stringify({ status: 'error', message: 'Invalid JSON payload' }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    var sheetAccess = getSheetAccess();
    var nowMs = Date.now();
    var result = handleRequest(sheetAccess, req, nowMs);

    return ContentService.createTextOutput(JSON.stringify(result))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ status: 'error', message: String(err && err.message ? err.message : err) }))
      .setMimeType(ContentService.MimeType.JSON);
  } finally {
    try {
      lock.releaseLock();
    } catch (ignore) {}
  }
}

// ---------------------------------------------------------------------------
// Pure / Parameterized Handlers (Testable in Node without Apps Script runtime)
// ---------------------------------------------------------------------------

function handleRequest(sheetAccess, req, nowMs) {
  var action = req.action;
  var fam = String(req.fam || req.family || '').trim().toLowerCase();

  if (!fam || fam.length < 8) {
    return { status: 'error', message: 'Invalid or missing family code hash' };
  }

  if (action === 'sync') {
    return handleSync(sheetAccess, req, fam, nowMs);
  } else if (action === 'list') {
    return handleList(sheetAccess, fam);
  } else if (action === 'delete_kid') {
    return handleDeleteKid(sheetAccess, req, fam, nowMs);
  } else if (action === 'export_check') {
    return handleExportCheck(sheetAccess, req, fam);
  } else if (action === 'snapshot') {
    return handleSnapshot(sheetAccess, nowMs);
  } else {
    return { status: 'error', message: 'Unknown action: ' + action };
  }
}

function handleSync(sheetAccess, req, fam, nowMs) {
  var kid = String(req.kid || '').trim().toLowerCase();
  if (!kid) {
    return { status: 'error', message: 'Missing kid parameter' };
  }

  var eventsSheet = sheetAccess.getOrCreateSheet('events', ['fam', 'kid', 'dev', 'seq', 'recv_ms', 'json']);
  var profilesSheet = sheetAccess.getOrCreateSheet('profiles', ['fam', 'kid', 'record_json', 'updated_ms']);
  var tombstonesSheet = sheetAccess.getOrCreateSheet('tombstones', ['fam', 'kid', 'deleted_ms']);

  // 1. Check Tombstone
  var tombstoneData = tombstonesSheet.getDataRange().getValues();
  var tombstoneRowIndex = -1;
  var deletedMs = 0;
  for (var t = 1; t < tombstoneData.length; t++) {
    if (String(tombstoneData[t][0]) === fam && String(tombstoneData[t][1]).toLowerCase() === kid) {
      tombstoneRowIndex = t + 1;
      deletedMs = Number(tombstoneData[t][2]) || 0;
      break;
    }
  }

  var incomingEvents = req.events || [];
  var incomingProfile = req.profile || null;

  // Check if incoming push has events newer than deleted_ms to clear tombstone
  var hasNewerEvidence = false;
  for (var ie = 0; ie < incomingEvents.length; ie++) {
    if ((incomingEvents[ie].t || 0) > deletedMs) {
      hasNewerEvidence = true;
      break;
    }
  }
  if (incomingProfile && (incomingProfile.updated || 0) > deletedMs) {
    hasNewerEvidence = true;
  }

  if (tombstoneRowIndex > -1) {
    if (hasNewerEvidence) {
      // Clear tombstone: child is re-created
      tombstonesSheet.deleteRow(tombstoneRowIndex);
    } else {
      // Child is still tombstoned on server
      return {
        status: 'success',
        tombstoned: true,
        events: [],
        more: false,
        serverVec: {},
        profile: null
      };
    }
  }

  // 2. Read existing events to dedupe pushes and track max sequence
  var eventsData = eventsSheet.getDataRange().getValues();
  var storedKeys = {}; // dev + '_' + seq -> true
  var serverVec = {}; // dev -> maxSeq

  for (var r = 1; r < eventsData.length; r++) {
    var rowFam = String(eventsData[r][0]);
    var rowKid = String(eventsData[r][1]).toLowerCase();
    if (rowFam === fam && rowKid === kid) {
      var rDev = String(eventsData[r][2]);
      var rSeq = Number(eventsData[r][3]) || 0;
      storedKeys[rDev + '_' + rSeq] = true;
      if (!serverVec[rDev] || rSeq > serverVec[rDev]) {
        serverVec[rDev] = rSeq;
      }
    }
  }

  // Append new pushed events
  for (var p = 0; p < incomingEvents.length; p++) {
    var ev = incomingEvents[p];
    var dev = String(ev.d || '');
    var seq = Number(ev.q) || 0;
    var key = dev + '_' + seq;
    if (!storedKeys[key]) {
      storedKeys[key] = true;
      eventsSheet.appendRow([fam, kid, dev, seq, nowMs, JSON.stringify(ev)]);
      if (!serverVec[dev] || seq > serverVec[dev]) {
        serverVec[dev] = seq;
      }
    }
  }

  // 3. Class B profile merge
  var profilesData = profilesSheet.getDataRange().getValues();
  var profileRowIndex = -1;
  var storedProfile = null;
  for (var pr = 1; pr < profilesData.length; pr++) {
    if (String(profilesData[pr][0]) === fam && String(profilesData[pr][1]).toLowerCase() === kid) {
      profileRowIndex = pr + 1;
      try {
        storedProfile = JSON.parse(profilesData[pr][2] || 'null');
      } catch (ex) {
        storedProfile = null;
      }
      break;
    }
  }

  var mergedProfile = mergeRecords(storedProfile, incomingProfile);
  if (mergedProfile) {
    var mergedJson = JSON.stringify(mergedProfile);
    var updatedMs = mergedProfile.updated || nowMs;
    if (profileRowIndex > -1) {
      profilesSheet.getRange(profileRowIndex, 3).setValue(mergedJson);
      profilesSheet.getRange(profileRowIndex, 4).setValue(updatedMs);
    } else {
      profilesSheet.appendRow([fam, kid, mergedJson, updatedMs]);
    }
  }

  // 4. Query events whose seq > vec[dev]
  var clientVec = req.vec || {};
  // Re-read events after append
  var freshEventsData = eventsSheet.getDataRange().getValues();
  var eligibleEvents = [];

  for (var fe = 1; fe < freshEventsData.length; fe++) {
    if (String(freshEventsData[fe][0]) === fam && String(freshEventsData[fe][1]).toLowerCase() === kid) {
      var fDev = String(freshEventsData[fe][2]);
      var fSeq = Number(freshEventsData[fe][3]) || 0;
      var fRecv = Number(freshEventsData[fe][4]) || nowMs;
      var clientKnownSeq = Number(clientVec[fDev]) || 0;

      if (fSeq > clientKnownSeq) {
        var parsedEv = {};
        try {
          parsedEv = JSON.parse(freshEventsData[fe][5] || '{}');
        } catch (ex2) {
          parsedEv = {};
        }
        // Attach server receive timestamp r
        if (parsedEv.y === 'ckp') {
          parsedEv.recv_r = fRecv;
        } else {
          parsedEv.r = fRecv;
        }
        eligibleEvents.push({ dev: fDev, seq: fSeq, ev: parsedEv });
      }
    }
  }

  // Order by (dev, seq)
  eligibleEvents.sort(function (a, b) {
    if (a.dev !== b.dev) return a.dev < b.dev ? -1 : 1;
    return a.seq - b.seq;
  });

  var PAGE_SIZE = 200;
  var page = [];
  var more = eligibleEvents.length > PAGE_SIZE;
  var limit = Math.min(eligibleEvents.length, PAGE_SIZE);
  for (var el = 0; el < limit; el++) {
    page.push(eligibleEvents[el].ev);
  }

  // 5. Trigger snapshot
  try {
    handleSnapshot(sheetAccess, nowMs);
  } catch (snapErr) {}

  return {
    status: 'success',
    events: page,
    more: more,
    serverVec: serverVec,
    profile: mergedProfile,
    tombstoned: false
  };
}

function handleList(sheetAccess, fam) {
  var profilesSheet = sheetAccess.getOrCreateSheet('profiles', ['fam', 'kid', 'record_json', 'updated_ms']);
  var tombstonesSheet = sheetAccess.getOrCreateSheet('tombstones', ['fam', 'kid', 'deleted_ms']);

  var tombstonesData = tombstonesSheet.getDataRange().getValues();
  var tombstones = {};
  for (var t = 1; t < tombstonesData.length; t++) {
    if (String(tombstonesData[t][0]) === fam) {
      var tKid = String(tombstonesData[t][1]).toLowerCase();
      tombstones[tKid] = Number(tombstonesData[t][2]) || 0;
    }
  }

  var profilesData = profilesSheet.getDataRange().getValues();
  var kids = [];
  var seenKids = {};

  for (var p = 1; p < profilesData.length; p++) {
    if (String(profilesData[p][0]) === fam) {
      var kidId = String(profilesData[p][1]).toLowerCase();
      seenKids[kidId] = true;
      var rec = {};
      try {
        rec = JSON.parse(profilesData[p][2] || '{}');
      } catch (ex) {}
      kids.push({
        kid: kidId,
        name: rec.name || kidId,
        avatar: rec.avatar || 'princess',
        tombstoned: Boolean(tombstones[kidId]),
        deleted_ms: tombstones[kidId] || 0
      });
    }
  }

  // Include tombstoned kids that may not have active profile rows
  for (var tk in tombstones) {
    if (!seenKids[tk]) {
      kids.push({
        kid: tk,
        name: tk,
        avatar: 'princess',
        tombstoned: true,
        deleted_ms: tombstones[tk]
      });
    }
  }

  return { status: 'success', kids: kids };
}

function handleDeleteKid(sheetAccess, req, fam, nowMs) {
  var kid = String(req.kid || '').trim().toLowerCase();
  if (!kid) {
    return { status: 'error', message: 'Missing kid parameter' };
  }

  var eventsSheet = sheetAccess.getOrCreateSheet('events', ['fam', 'kid', 'dev', 'seq', 'recv_ms', 'json']);
  var profilesSheet = sheetAccess.getOrCreateSheet('profiles', ['fam', 'kid', 'record_json', 'updated_ms']);
  var tombstonesSheet = sheetAccess.getOrCreateSheet('tombstones', ['fam', 'kid', 'deleted_ms']);

  // Delete matching rows from events
  var evData = eventsSheet.getDataRange().getValues();
  for (var r = evData.length - 1; r >= 1; r--) {
    if (String(evData[r][0]) === fam && String(evData[r][1]).toLowerCase() === kid) {
      eventsSheet.deleteRow(r + 1);
    }
  }

  // Delete matching rows from profiles
  var prData = profilesSheet.getDataRange().getValues();
  for (var pr = prData.length - 1; pr >= 1; pr--) {
    if (String(prData[pr][0]) === fam && String(prData[pr][1]).toLowerCase() === kid) {
      profilesSheet.deleteRow(pr + 1);
    }
  }

  // Add/update tombstone row
  var tbData = tombstonesSheet.getDataRange().getValues();
  var foundTb = false;
  for (var tb = 1; tb < tbData.length; tb++) {
    if (String(tbData[tb][0]) === fam && String(tbData[tb][1]).toLowerCase() === kid) {
      tombstonesSheet.getRange(tb + 1, 3).setValue(nowMs);
      foundTb = true;
      break;
    }
  }
  if (!foundTb) {
    tombstonesSheet.appendRow([fam, kid, nowMs]);
  }

  return { status: 'success', message: 'Child deleted' };
}

function handleExportCheck(sheetAccess, req, fam) {
  var kid = String(req.kid || '').trim().toLowerCase();
  if (!kid) {
    return { status: 'error', message: 'Missing kid parameter' };
  }

  var eventsSheet = sheetAccess.getOrCreateSheet('events', ['fam', 'kid', 'dev', 'seq', 'recv_ms', 'json']);
  var data = eventsSheet.getDataRange().getValues();
  var events = [];

  for (var r = 1; r < data.length; r++) {
    if (String(data[r][0]) === fam && String(data[r][1]).toLowerCase() === kid) {
      var dev = String(data[r][2]);
      var seq = Number(data[r][3]) || 0;
      var parsed = {};
      try {
        parsed = JSON.parse(data[r][5] || '{}');
      } catch (ex) {}
      events.push({ dev: dev, seq: seq, ev: parsed });
    }
  }

  // Canonical sort by (d, q)
  events.sort(function (a, b) {
    if (a.dev !== b.dev) return a.dev < b.dev ? -1 : 1;
    return a.seq - b.seq;
  });

  var canonicalEvents = [];
  for (var i = 0; i < events.length; i++) {
    canonicalEvents.push(events[i].ev);
  }

  var jsonStr = JSON.stringify(canonicalEvents);
  var hash = computeSha256(jsonStr);

  return {
    status: 'success',
    eventCount: canonicalEvents.length,
    checksum: hash
  };
}

function handleSnapshot(sheetAccess, nowMs) {
  var d = new Date(nowMs);
  var yyyy = String(d.getUTCFullYear());
  var mm = ('0' + (d.getUTCMonth() + 1)).slice(-2);
  var dd = ('0' + d.getUTCDate()).slice(-2);
  var targetTabName = 'events_snap_' + yyyy + mm + dd;

  // Check if snapshot for today already exists
  if (sheetAccess.getSheet(targetTabName)) {
    return { status: 'success', message: 'Snapshot already exists for today' };
  }

  var eventsSheet = sheetAccess.getSheet('events');
  if (!eventsSheet) {
    return { status: 'success', message: 'No events sheet to snapshot' };
  }

  var data = eventsSheet.getDataRange().getValues();
  var snapSheet = sheetAccess.getOrCreateSheet(targetTabName, []);
  for (var r = 0; r < data.length; r++) {
    snapSheet.appendRow(data[r]);
  }

  // Rotate snapshots: keep only the newest SNAPSHOT_KEEP (7)
  var allSheets = sheetAccess.getAllSheets();
  var snapSheets = [];
  for (var s = 0; s < allSheets.length; s++) {
    var name = allSheets[s].getName();
    if (name.indexOf('events_snap_') === 0) {
      snapSheets.push({ name: name, sheet: allSheets[s] });
    }
  }

  // Sort descending by name (YYYYMMDD)
  snapSheets.sort(function (a, b) {
    return b.name.localeCompare(a.name);
  });

  if (snapSheets.length > SNAPSHOT_KEEP) {
    for (var rem = SNAPSHOT_KEEP; rem < snapSheets.length; rem++) {
      sheetAccess.deleteSheet(snapSheets[rem].sheet);
    }
  }

  return { status: 'success', snapshot: targetTabName };
}

// ---------------------------------------------------------------------------
// Mirrored Class B Merge Logic
// ---------------------------------------------------------------------------

function mergeRecords(a, b) {
  if (!a) return b ? clone(b) : null;
  if (!b) return clone(a);

  var ea = num(a.epoch), eb = num(b.epoch);
  if (ea !== eb) {
    return clone(ea > eb ? a : b);
  }

  var ua = num(a.updated), ub = num(b.updated);
  var newer = a;
  if (ua > ub) {
    newer = a;
  } else if (ub > ua) {
    newer = b;
  } else {
    var sa = JSON.stringify(a);
    var sb = JSON.stringify(b);
    newer = sa >= sb ? a : b;
  }

  var out = {
    v: 1,
    name: newer.name || a.name || b.name || '',
    avatar: newer.avatar || a.avatar || b.avatar || '',
    epoch: ea,
    nodes: Math.max(num(a.nodes), num(b.nodes)),
    stars: Math.max(num(a.stars), num(b.stars)),
    domain_counts: {},
    quest: { date: '', count: 0 },
    updated: Math.max(ua, ub)
  };

  if (newer.modality_preferences) {
    out.modality_preferences = clone(newer.modality_preferences);
  }

  var k;
  var dcs = [a.domain_counts || {}, b.domain_counts || {}];
  for (var i = 0; i < 2; i++) {
    for (k in dcs[i]) {
      if (Object.prototype.hasOwnProperty.call(dcs[i], k)) {
        out.domain_counts[k] = Math.max(num(out.domain_counts[k]), num(dcs[i][k]));
      }
    }
  }

  var qa = a.quest || { date: '', count: 0 };
  var qb = b.quest || { date: '', count: 0 };
  if (qa.date === qb.date) {
    out.quest = { date: qa.date || '', count: Math.max(num(qa.count), num(qb.count)) };
  } else {
    out.quest = clone(qa.date > qb.date ? qa : qb);
  }

  return out;
}

function num(x) {
  var n = Number(x);
  return isNaN(n) ? 0 : n;
}

function clone(x) {
  return JSON.parse(JSON.stringify(x));
}

// ---------------------------------------------------------------------------
// Server SHA-256 Helper (Used for export_check)
// ---------------------------------------------------------------------------

function computeSha256(str) {
  if (typeof Utilities !== 'undefined' && Utilities.computeDigest && Utilities.DigestAlgorithm) {
    var rawHash = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, str, Utilities.Charset.UTF_8);
    var hex = '';
    for (var i = 0; i < rawHash.length; i++) {
      var b = rawHash[i];
      if (b < 0) b += 256;
      var h = b.toString(16);
      if (h.length === 1) hex += '0';
      hex += h;
    }
    return hex;
  }
  // Fallback pure JS for Node test environments
  return pureSha256(str);
}

function pureSha256(ascii) {
  function rRot(v, a) { return (v >>> a) | (v << (32 - a)); }
  var i, j;
  var words = [];
  var utf8 = [];
  for (i = 0; i < ascii.length; i++) {
    var c = ascii.charCodeAt(i);
    if (c < 0x80) utf8.push(c);
    else if (c < 0x800) { utf8.push(0xc0 | (c >> 6)); utf8.push(0x80 | (c & 0x3f)); }
    else if (c < 0xd800 || c >= 0xe000) { utf8.push(0xe0 | (c >> 12)); utf8.push(0x80 | ((c >> 6) & 0x3f)); utf8.push(0x80 | (c & 0x3f)); }
    else {
      i++;
      var c2 = ascii.charCodeAt(i);
      var fc = 0x10000 + (((c & 0x3ff) << 10) | (c2 & 0x3ff));
      utf8.push(0xf0 | (fc >> 18)); utf8.push(0x80 | ((fc >> 12) & 0x3f)); utf8.push(0x80 | ((fc >> 6) & 0x3f)); utf8.push(0x80 | (fc & 0x3f));
    }
  }
  var bitLen = utf8.length * 8;
  for (i = 0; i < utf8.length; i++) {
    var wi = i >> 2;
    words[wi] = (words[wi] || 0) | (utf8[i] << (24 - (i % 4) * 8));
  }
  var pwi = utf8.length >> 2;
  words[pwi] = (words[pwi] || 0) | (0x80 << (24 - (utf8.length % 4) * 8));
  var totalWords = (((utf8.length + 8) >> 6) + 1) * 16;
  while (words.length < totalWords - 2) words.push(0);
  words.push(Math.floor(bitLen / Math.pow(2, 32)));
  words.push(bitLen >>> 0);

  var hash = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
  var k = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
  ];
  var w = new Array(64);
  for (i = 0; i < words.length; i += 16) {
    for (j = 0; j < 16; j++) w[j] = words[i + j] || 0;
    for (j = 16; j < 64; j++) {
      var s0 = rRot(w[j - 15], 7) ^ rRot(w[j - 15], 18) ^ (w[j - 15] >>> 3);
      var s1 = rRot(w[j - 2], 17) ^ rRot(w[j - 2], 19) ^ (w[j - 2] >>> 10);
      w[j] = (((w[j - 16] + s0) >>> 0) + ((w[j - 7] + s1) >>> 0)) >>> 0;
    }
    var a = hash[0], b = hash[1], c = hash[2], d = hash[3];
    var ee = hash[4], f = hash[5], g = hash[6], h = hash[7];
    for (j = 0; j < 64; j++) {
      var S1 = rRot(ee, 6) ^ rRot(ee, 11) ^ rRot(ee, 25);
      var ch = (ee & f) ^ (~ee & g);
      var temp1 = (((((h + S1) >>> 0) + ch) >>> 0) + ((k[j] + w[j]) >>> 0)) >>> 0;
      var S0 = rRot(a, 2) ^ rRot(a, 13) ^ rRot(a, 22);
      var maj = (a & b) ^ (a & c) ^ (b & c);
      var temp2 = (S0 + maj) >>> 0;
      h = g; g = f; f = ee; ee = (d + temp1) >>> 0; d = c; c = b; b = a; a = (temp1 + temp2) >>> 0;
    }
    hash[0] = (hash[0] + a) >>> 0; hash[1] = (hash[1] + b) >>> 0; hash[2] = (hash[2] + c) >>> 0; hash[3] = (hash[3] + d) >>> 0;
    hash[4] = (hash[4] + ee) >>> 0; hash[5] = (hash[5] + f) >>> 0; hash[6] = (hash[6] + g) >>> 0; hash[7] = (hash[7] + h) >>> 0;
  }
  var res = '';
  for (i = 0; i < 8; i++) {
    var hx = hash[i].toString(16);
    while (hx.length < 8) hx = '0' + hx;
    res += hx;
  }
  return res;
}

// Export for Node tests
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    handleRequest: handleRequest,
    handleSync: handleSync,
    handleList: handleList,
    handleDeleteKid: handleDeleteKid,
    handleExportCheck: handleExportCheck,
    handleSnapshot: handleSnapshot,
    runDailySnapshot: runDailySnapshot,
    mergeRecords: mergeRecords,
    pureSha256: pureSha256,
    SNAPSHOT_KEEP: SNAPSHOT_KEEP
  };
}
