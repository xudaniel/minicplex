const fs=require('fs'), crypto=require('crypto');
const src=fs.readFileSync(process.argv[2],'utf8');
const core=src.includes('/*CORE-START*/')?src.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0]:src;
const A=new Function(core+';return {sha256,hashText,hexBytes,leadingZeroBits,digText,digRun,DIG_LEVELS,BET_LEVELS,BET_RACES,BET_TOLERANCE,slotOf,race,expectedThrows,pctOff,histogram,mulberry};')();
let fail=0; const ok=(n,c,x)=>{ if(!c) fail++; console.log((c?'OK   ':'FAIL ')+n+(x?'  '+x:'')); };
const real=s=>crypto.createHash('sha256').update(s).digest('hex');
// SHA-256 against Node's own, including the padding edge lengths and repeated calls (shared work buffer)
let bad=0; for (const t of ['', 'a', 'x'.repeat(55), 'x'.repeat(56), 'x'.repeat(64), '长'.repeat(40), 'x'.repeat(119), 'x'.repeat(120), 'hash为什么基本就是唯一的', 'minicplex #0']) if (A.hexBytes(A.hashText(t))!==real(t)) bad++;
for (let i=0;i<2000;i++){ const t='minicplex #'+i; if (A.hexBytes(A.hashText(t))!==real(t)) bad++; }
ok('sha256 matches node crypto (2010 inputs)', bad===0);
// leading zero bits
const lz=hex=>A.leadingZeroBits(Uint8Array.from(Buffer.from(hex.padEnd(64,'f'),'hex')));
ok('leadingZeroBits', lz('ff')===0&&lz('7f')===1&&lz('0f')===4&&lz('08')===4&&lz('00ff')===8&&lz('0001')===15&&lz('00000f')===20&&A.leadingZeroBits(new Uint8Array(32))===256, [lz('ff'),lz('7f'),lz('0f'),lz('08'),lz('00ff'),lz('0001'),lz('00000f')].join(','));
// mining: the nonce it reports really has that many zero bits, and no earlier nonce does
for (const target of [8,12,16]) { const t0=Date.now(); const r=A.digRun('minicplex',0,5e6,target); const h=real(A.digText('minicplex',r.found));
  const zeros=h.match(/^0*/)[0].length; let earlier=false; for(let i=0;i<Math.min(r.found,3000);i++) if (A.leadingZeroBits(A.hashText(A.digText('minicplex',i)))>=target) earlier=true;
  ok('dig '+target+' bits', r.found>=0 && lz(h)>=target && zeros>=Math.floor(target/4) && !earlier && r.tried===r.found+1, 'nonce '+r.found+'  '+h.slice(0,12)+'…  '+(Date.now()-t0)+' ms'); }
{ const t0=Date.now(); const r=A.digRun('minicplex',0,2e7,20); const dt=Date.now()-t0; ok('dig 20 bits', r.found>=0 && lz(real(A.digText('minicplex',r.found)))>=20, 'nonce '+r.found+'  '+real(A.digText('minicplex',r.found)).slice(0,12)+'…  '+dt+' ms  ≈'+Math.round(r.tried/dt*1000)+' hashes/s'); }
const first=A.leadingZeroBits(A.hashText('minicplex #0')); console.log('     minicplex #0 →', real('minicplex #0').slice(0,16), 'zero bits', first);
let m4=-1; for(let i=1;i<200;i++) if (A.leadingZeroBits(A.hashText(A.digText('minicplex',i)))>=4){m4=i;break;} console.log('     first hand-dig with 4 zero bits: #'+m4);
// races
for (const L of [1,2,3]) for (const n of A.BET_LEVELS[L]) { let tot=0; const N=A.BET_RACES; for(let r=0;r<N;r++) tot+=A.race(n,'t'+r,false).throws; const avg=tot/N, e=A.expectedThrows(n);
  ok('race n='+n, Math.abs(avg-e)/e<0.12, 'avg of 200 = '+avg.toFixed(1)+'  theory '+e.toFixed(1)+'  1.25√n = '+(1.25*Math.sqrt(n)).toFixed(1)+'  theory vs rule '+(Math.abs(1.25*Math.sqrt(n)-e)/e*100).toFixed(1)+'%'); }
const r1=A.race(64,'x',true); ok('race keeps sequence, ends on a repeat', r1.seq.length===r1.throws && r1.seq.indexOf(r1.seq[r1.throws-1])<r1.throws-1 && new Set(r1.seq.slice(0,-1)).size===r1.throws-1);
ok('birthday: 365 slots', Math.abs(A.expectedThrows(365)-24.6)<0.1, A.expectedThrows(365).toFixed(2));
ok('pctOff', A.pctOff(25,20)===25 && A.pctOff(16,20)===20);
const hg=A.histogram([1,2,3,10,40],8); ok('histogram', hg.counts.reduce((a,b)=>a+b,0)===5 && hg.max>=41, JSON.stringify(hg));
console.log(fail?'FAILURES '+fail:'ALL OK');
process.exit(fail?1:0);
