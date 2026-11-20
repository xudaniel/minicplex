// 从页面里取出算法部分，和 C 版的结果逐项对比
const fs = require('fs');
const html = fs.readFileSync(process.argv[2], 'utf8');
const core = html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];
const api = new Function(core + '; return {utf8, fnv1a, sha256, diffBytes, hexBytes, hex8, compareTrace, findCollision, expectedTries, sampleMix, dft, fft, ifft, lowpass, roundTripError, makeNoise, zhNum, zhTime};')();
const crypto = require('crypto');
let fail = 0;
const eq = (name, got, want) => { const ok = String(got) === String(want); if (!ok) fail++; console.log((ok ? 'OK   ' : 'FAIL ') + name + ' = ' + got + (ok ? '' : '  (want ' + want + ')')); };

const s1 = 'hash为什么基本就是唯一的', s2 = s1 + '。';
eq('bytes', api.utf8(s1).length, 34);
eq('sha(s1)', api.hexBytes(api.sha256(api.utf8(s1))), '2878a4e9a062efa46dbea845b7a04df4d36baa049c2b96ed54607027f08cad48');
eq('sha(s2)', api.hexBytes(api.sha256(api.utf8(s2))), '43e5cfab28efe410deafa5c4cc277c38eea762b52445c563353ca79a71cc3179');
eq('diff', api.diffBytes(api.sha256(api.utf8(s1)), api.sha256(api.utf8(s2))), 121);
eq('fnv', api.hex8(api.fnv1a(api.utf8('我的一句话'))), '21838ace');
eq('fnv2', api.hex8(api.fnv1a(api.utf8('我的一句话。'))), '5656f755');
eq('fnv empty', api.hex8(api.fnv1a(api.utf8(''))), '811c9dc5');
for (const t of ['', 'a', 'x'.repeat(55), 'x'.repeat(56), 'x'.repeat(64), '长'.repeat(40), 'x'.repeat(119), 'x'.repeat(120)]) {
  eq('sha len ' + Buffer.byteLength(t), api.hexBytes(api.sha256(api.utf8(t))), crypto.createHash('sha256').update(t).digest('hex'));
}
const c = api.compareTrace(api.sha256(api.utf8(s1), true), api.sha256(api.utf8(s2), true));
eq('md', c.md.join(','), '8,9,15');
eq('round diffs 8,9,10,11,12,63', [9, 10, 11, 12, 13, 64].map(i => c.diffs[i]).join(','), '14,47,80,109,127,117');
eq('zero before', c.diffs.slice(0, 9).join(''), '000000000');
eq('a after r8', api.hex8(c.A.rounds[9][0]) + ' ' + api.hex8(c.B.rounds[9][0]), '8da4e4da 8da5485a');
eq('trace hash same', api.hexBytes(api.sha256(api.utf8(s1), true).hash), api.hexBytes(api.sha256(api.utf8(s1))));
eq('identical', api.compareTrace(api.sha256(api.utf8(s1), true), api.sha256(api.utf8(s1), true)), null);
const L = '长'.repeat(30);
const c2 = api.compareTrace(api.sha256(api.utf8(L), true), api.sha256(api.utf8(L + '。'), true));
eq('long block', c2.bi + ' ' + c2.md[0], '1 6');

// 撞车
for (const bits of [8, 16, 24]) {
  const r = api.findCollision(bits, 1);
  const ha = crypto.createHash('sha256').update(r.a).digest('hex'), hb = crypto.createHash('sha256').update(r.b).digest('hex');
  eq('collision ' + bits, r.a !== r.b && ha.slice(0, bits / 4) === hb.slice(0, bits / 4) && ha.slice(0, bits / 4) === r.v.toString(16).padStart(bits / 4, '0'), true);
}
let tot = 0; for (let i = 0; i < 200; i++) tot += api.findCollision(16, 'T' + i).tries;
console.log('     16-bit mean tries over 200 runs =', (tot / 200).toFixed(0), ' expected', api.expectedTries(16).toFixed(0));
console.log('     half-chance: 16b', (1.1774 * 2 ** 8).toFixed(0), ' 32b', (1.1774 * 2 ** 16).toFixed(0), ' 64b', (1.1774 * 2 ** 32).toExponential(2), ' 256b', (1.1774 * 2 ** 128).toExponential(2));

// 傅里叶
const parts = [{ f: 3, a: 1 }, { f: 7, a: 0.5 }, { f: 12, a: 0 }];
const x = api.sampleMix(parts, 0, 64), X = api.dft(x);
const amp = k => Math.hypot(X.re[k], X.im[k]) * 2 / 64;
eq('amp3', amp(3).toFixed(3), '1.000'); eq('amp7', amp(7).toFixed(3), '0.500'); eq('amp5', amp(5).toFixed(3), '0.000');
const xp = api.sampleMix(parts, 90, 64), Xp = api.dft(xp);
eq('phase90 amp3', (Math.hypot(Xp.re[3], Xp.im[3]) * 2 / 64).toFixed(3), '1.000');
const F = api.fft(x, new Float64Array(64));
let md = 0; for (let k = 0; k < 64; k++) md = Math.max(md, Math.abs(F.re[k] - X.re[k]), Math.abs(F.im[k] - X.im[k]));
eq('fft==dft', md < 1e-9, true);
const noisy = Float64Array.from(api.sampleMix(parts, 0, 256), (v, i) => v + api.makeNoise(256, 20261120, 0.5)[i]);
console.log('     round trip err', api.roundTripError(noisy).toExponential(1));
const clean = api.sampleMix(parts, 0, 256);
const rms = a => Math.sqrt(a.reduce((s, v, i) => s + (v - clean[i]) ** 2, 0) / 256);
console.log('     rms noise before', rms(noisy).toFixed(3), ' after cut 20', rms(api.lowpass(noisy, 20)).toFixed(3), ' cut 128', rms(api.lowpass(noisy, 128)).toFixed(3));
const nz = api.makeNoise(256, 20261120, 0.5); console.log('     noise min/max', Math.min(...nz).toFixed(2), Math.max(...nz).toFixed(2));

// 次数
const N = 2 ** 20; eq('ratio 2^20', Math.round(N * N / (N / 2 * 20)), 104858);
eq('zh D', api.zhNum(N * N), '1.1 万亿'); eq('zh F', api.zhNum(N / 2 * 20), '1049 万');
eq('time', api.zhTime(N * N / 1e8) + ' / ' + api.zhTime(N / 2 * 20 / 1e8), '3.1 小时 / 105 毫秒');
eq('p12', api.zhNum(4096 * 4096) + ' ' + api.zhNum(2048 * 12) + ' ' + api.zhNum(4096 * 4096 / (2048 * 12)), '1678 万 2.5 万 683');

// 倒推
const target = api.sha256(api.utf8(s1)); let best = 0; const t0 = Date.now();
for (let i = 0; i < 20000; i++) best = Math.max(best, 256 - api.diffBytes(api.sha256(api.utf8('猜 1-' + i)), target));
console.log('     brute best of 20000 =', best, ' ms', Date.now() - t0);
console.log(fail ? 'FAILURES: ' + fail : 'ALL OK');
