// Pure, order-independent merge of two Class B child progress records.
// Invariant: merge(a, b) == merge(b, a); merge(a, a) == a.
// Used by BOTH the client app and the Apps Script server.

export interface ClassBProfile {
  v: number;
  name: string;
  avatar: string;
  epoch: number;
  nodes: number;
  stars: number;
  domain_counts: { [domain: string]: number };
  quest: { date: string; count: number };
  modality_preferences?: any;
  updated: number;
}

function num(x: any): number {
  var n = Number(x);
  return isNaN(n) ? 0 : n;
}

function clone<T>(x: T): T {
  return JSON.parse(JSON.stringify(x));
}

export function mergeRecords(a: any, b: any): any {
  if (!a) return b ? clone(b) : null;
  if (!b) return clone(a);

  var ea = num(a.epoch), eb = num(b.epoch);
  if (ea !== eb) {
    // Reset happened: higher epoch wins the whole record
    return clone(ea > eb ? a : b);
  }

  // Determine which record supplies name, avatar, and modality preferences
  var ua = num(a.updated), ub = num(b.updated);
  var newer = a;
  if (ua > ub) {
    newer = a;
  } else if (ub > ua) {
    newer = b;
  } else {
    // Exact tie on updated timestamp: lexicographical string tie-breaker
    var sa = JSON.stringify(a);
    var sb = JSON.stringify(b);
    newer = sa >= sb ? a : b;
  }

  var out: any = {
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

  var k: string;
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
    out.quest = {
      date: qa.date || '',
      count: Math.max(num(qa.count), num(qb.count))
    };
  } else {
    out.quest = clone(qa.date > qb.date ? qa : qb);
  }

  return out;
}
