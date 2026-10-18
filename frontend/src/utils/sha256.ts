// Pure ES5 SHA-256 implementation with UTF-8 support.
// No external dependencies, strictly conforms to FIPS 180-4.

function rightRotate(value: number, amount: number): number {
  return (value >>> amount) | (value << (32 - amount));
}

export function sha256(ascii: string): string {
  var mathPow = Math.pow;
  var maxWord = mathPow(2, 32);
  var i: number, j: number;
  var result = '';

  var words: number[] = [];
  var asciiBitLength = 0;

  // UTF-8 encode input string to bytes
  var utf8Bytes: number[] = [];
  for (i = 0; i < ascii.length; i++) {
    var code = ascii.charCodeAt(i);
    if (code < 0x80) {
      utf8Bytes.push(code);
    } else if (code < 0x800) {
      utf8Bytes.push(0xc0 | (code >> 6));
      utf8Bytes.push(0x80 | (code & 0x3f));
    } else if (code < 0xd800 || code >= 0xe000) {
      utf8Bytes.push(0xe0 | (code >> 12));
      utf8Bytes.push(0x80 | ((code >> 6) & 0x3f));
      utf8Bytes.push(0x80 | (code & 0x3f));
    } else {
      // Surrogate pair
      i++;
      var code2 = ascii.charCodeAt(i);
      var fullCode = 0x10000 + (((code & 0x3ff) << 10) | (code2 & 0x3ff));
      utf8Bytes.push(0xf0 | (fullCode >> 18));
      utf8Bytes.push(0x80 | ((fullCode >> 12) & 0x3f));
      utf8Bytes.push(0x80 | ((fullCode >> 6) & 0x3f));
      utf8Bytes.push(0x80 | (fullCode & 0x3f));
    }
  }

  asciiBitLength = utf8Bytes.length * 8;

  // Pack bytes into 32-bit big-endian words
  for (i = 0; i < utf8Bytes.length; i++) {
    var wordIndex = i >> 2;
    words[wordIndex] = (words[wordIndex] || 0) | (utf8Bytes[i] << (24 - (i % 4) * 8));
  }

  // Padding
  var byteCount = utf8Bytes.length;
  var padWordIndex = byteCount >> 2;
  words[padWordIndex] = (words[padWordIndex] || 0) | (0x80 << (24 - (byteCount % 4) * 8));

  var totalWords = (((byteCount + 8) >> 6) + 1) * 16;
  while (words.length < totalWords - 2) {
    words.push(0);
  }
  words.push(Math.floor(asciiBitLength / maxWord));
  words.push(asciiBitLength >>> 0);

  // Initial hash values (first 32 bits of the fractional parts of square roots of first 8 primes 2..19)
  var hash = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
  ];

  // Round constants (first 32 bits of the fractional parts of cube roots of first 64 primes 2..311)
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
    for (j = 0; j < 16; j++) {
      w[j] = words[i + j] || 0;
    }
    for (j = 16; j < 64; j++) {
      var s0 = rightRotate(w[j - 15], 7) ^ rightRotate(w[j - 15], 18) ^ (w[j - 15] >>> 3);
      var s1 = rightRotate(w[j - 2], 17) ^ rightRotate(w[j - 2], 19) ^ (w[j - 2] >>> 10);
      w[j] = (((w[j - 16] + s0) >>> 0) + ((w[j - 7] + s1) >>> 0)) >>> 0;
    }

    var a = hash[0], b = hash[1], c = hash[2], d = hash[3];
    var e = hash[4], f = hash[5], g = hash[6], h = hash[7];

    for (j = 0; j < 64; j++) {
      var S1 = rightRotate(e, 6) ^ rightRotate(e, 11) ^ rightRotate(e, 25);
      var ch = (e & f) ^ (~e & g);
      var temp1 = (((((h + S1) >>> 0) + ch) >>> 0) + ((k[j] + w[j]) >>> 0)) >>> 0;
      var S0 = rightRotate(a, 2) ^ rightRotate(a, 13) ^ rightRotate(a, 22);
      var maj = (a & b) ^ (a & c) ^ (b & c);
      var temp2 = (S0 + maj) >>> 0;

      h = g;
      g = f;
      f = e;
      e = (d + temp1) >>> 0;
      d = c;
      c = b;
      b = a;
      a = (temp1 + temp2) >>> 0;
    }

    hash[0] = (hash[0] + a) >>> 0;
    hash[1] = (hash[1] + b) >>> 0;
    hash[2] = (hash[2] + c) >>> 0;
    hash[3] = (hash[3] + d) >>> 0;
    hash[4] = (hash[4] + e) >>> 0;
    hash[5] = (hash[5] + f) >>> 0;
    hash[6] = (hash[6] + g) >>> 0;
    hash[7] = (hash[7] + h) >>> 0;
  }

  for (i = 0; i < 8; i++) {
    var hex = hash[i].toString(16);
    while (hex.length < 8) {
      hex = '0' + hex;
    }
    result += hex;
  }

  return result;
}
