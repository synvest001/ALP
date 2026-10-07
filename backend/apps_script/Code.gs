// Deploy steps:
// 1. Create a Google Sheet.
// 2. Extensions > Apps Script.
// 3. Paste this file into Code.gs.
// 4. Deploy > New deployment > Web app.
// 5. Execute as: Me.
// 6. Who has access: Anyone.
// 7. Copy the /exec URL and paste into frontend/src/engine/SyncEngine.ts as SYNC_ENDPOINT.

var SHEET_NAME = 'progress';

function sheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    sheet.appendRow(['key', 'record_json', 'updated_iso']);
  }
  return sheet;
}

function doGet() {
  return ContentService.createTextOutput(JSON.stringify({ status: 'success', message: 'ALP sync is running' }))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
  } catch (lockError) {
    return ContentService.createTextOutput(JSON.stringify({ status: 'error', message: 'Could not obtain lock' }))
      .setMimeType(ContentService.MimeType.JSON);
  }

  try {
    var contents = (e && e.postData && e.postData.contents) ? e.postData.contents : '';
    var req = JSON.parse(contents || '{}');
    var family = String(req.family || '').trim().toLowerCase();
    if (family.length < 6) {
      return ContentService.createTextOutput(JSON.stringify({ status: 'error', message: 'Family code too short' }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    var sheet = sheet_();
    var data = sheet.getDataRange().getValues();

    if (req.action === 'list') {
      var prefix = family + '|';
      var kids = [];
      for (var i = 1; i < data.length; i++) {
        var rowKey = String(data[i][0] || '');
        if (rowKey.indexOf(prefix) === 0) {
          var kidId = rowKey.substring(prefix.length);
          var record = {};
          try {
            record = JSON.parse(data[i][1] || '{}');
          } catch (ex) {}
          kids.push({
            kid: kidId,
            name: record.name || kidId,
            avatar: record.avatar || ''
          });
        }
      }
      return ContentService.createTextOutput(JSON.stringify({ status: 'success', kids: kids }))
        .setMimeType(ContentService.MimeType.JSON);
    } else if (req.action === 'sync') {
      var kid = String(req.kid || '').trim().toLowerCase();
      if (!kid) {
        return ContentService.createTextOutput(JSON.stringify({ status: 'error', message: 'Missing kid parameter' }))
          .setMimeType(ContentService.MimeType.JSON);
      }
      var rowKey = family + '|' + kid;
      var foundRow = -1;
      var current = null;
      for (var r = 1; r < data.length; r++) {
        if (String(data[r][0] || '') === rowKey) {
          foundRow = r + 1;
          try {
            current = JSON.parse(data[r][1] || 'null');
          } catch (ex) {
            current = null;
          }
          break;
        }
      }

      var merged = mergeRecords(current, req.record || null);
      var mergedJson = JSON.stringify(merged);
      if (mergedJson.length > 45000) {
        return ContentService.createTextOutput(JSON.stringify({ status: 'error', message: 'Record too large' }))
          .setMimeType(ContentService.MimeType.JSON);
      }

      var iso = new Date().toISOString();
      if (foundRow > -1) {
        sheet.getRange(foundRow, 2).setValue(mergedJson);
        sheet.getRange(foundRow, 3).setValue(iso);
      } else {
        sheet.appendRow([rowKey, mergedJson, iso]);
      }

      return ContentService.createTextOutput(JSON.stringify({ status: 'success', record: merged }))
        .setMimeType(ContentService.MimeType.JSON);
    } else {
      return ContentService.createTextOutput(JSON.stringify({ status: 'error', message: 'Unknown action' }))
        .setMimeType(ContentService.MimeType.JSON);
    }
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ status: 'error', message: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  } finally {
    try {
      lock.releaseLock();
    } catch (ignore) {}
  }
}

// Pure, order-independent merge of two child progress records. merge(a,b)==merge(b,a); merge(a,a)==a.
// Used by BOTH the app and the Apps Script server (the server copy is this code with types removed).
function mergeRecords(a, b) {
  if (!a) return b ? clone(b) : null;
  if (!b) return clone(a);
  var ea = a.epoch || 0, eb = b.epoch || 0;
  if (ea !== eb) return clone(ea > eb ? a : b); // a reset happened: higher epoch wins the whole record
  var newer = (a.updated || 0) >= (b.updated || 0) ? a : b;
  var out = {
    v: 1,
    name: newer.name || a.name || b.name || '',
    avatar: newer.avatar || a.avatar || b.avatar || '',
    epoch: ea,
    nodes: Math.max(num(a.nodes), num(b.nodes)),
    stars: Math.max(num(a.stars), num(b.stars)),
    domain_counts: {},
    quest: { date: '', count: 0 },
    states: {},
    updated: Math.max(a.updated || 0, b.updated || 0)
  };
  var k;
  var dcs = [a.domain_counts || {}, b.domain_counts || {}];
  for (var i = 0; i < 2; i++) {
    for (k in dcs[i]) {
      if (Object.prototype.hasOwnProperty.call(dcs[i], k)) {
        out.domain_counts[k] = Math.max(num(out.domain_counts[k]), num(dcs[i][k]));
      }
    }
  }
  var qa = a.quest || { date: '', count: 0 }, qb = b.quest || { date: '', count: 0 };
  if (qa.date === qb.date) out.quest = { date: qa.date || '', count: Math.max(num(qa.count), num(qb.count)) };
  else out.quest = clone(qa.date > qb.date ? qa : qb);
  var sts = [a.states || {}, b.states || {}];
  for (var j = 0; j < 2; j++) {
    for (k in sts[j]) {
      if (!Object.prototype.hasOwnProperty.call(sts[j], k)) continue;
      var cur = out.states[k], cand = sts[j][k];
      if (!cur || num(cand.last_active) > num(cur.last_active) ||
          (num(cand.last_active) === num(cur.last_active) && num(cand.attempts) > num(cur.attempts))) {
        out.states[k] = clone(cand);
      }
    }
  }
  return out;
}
function num(x) { var n = Number(x); return isNaN(n) ? 0 : n; }
function clone(x) { return JSON.parse(JSON.stringify(x)); }
