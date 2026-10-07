// Pure, order-independent merge of two child progress records. merge(a,b)==merge(b,a); merge(a,a)==a.
// Used by BOTH the app and the Apps Script server (the server copy is this code with types removed).
export function mergeRecords(a: any, b: any): any {
  if (!a) return b ? clone(b) : null;
  if (!b) return clone(a);
  var ea = a.epoch || 0, eb = b.epoch || 0;
  if (ea !== eb) return clone(ea > eb ? a : b); // a reset happened: higher epoch wins the whole record
  var newer = (a.updated || 0) >= (b.updated || 0) ? a : b;
  var out: any = {
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
  var k: string;
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
function num(x: any): number { var n = Number(x); return isNaN(n) ? 0 : n; }
function clone(x: any): any { return JSON.parse(JSON.stringify(x)); }
