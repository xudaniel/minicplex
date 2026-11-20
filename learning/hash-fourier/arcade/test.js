const fs=require('fs'); const html=fs.readFileSync(process.argv[2],'utf8');
const core=html.split('/*CORE-START*/')[1].split('/*CORE-END*/')[0];
const A=new Function(core+';return {mulberry,mixAt,sampleParts,spectrum,probe,matchPct,TUNE_LEVELS,tuneRandom,SNAP_PLAN,snapRound,barsOf,partsKey,HUNT_LEVELS,huntBoard,resample,epicycles,circlesNeeded,reconAt,heartShape,circleGoals};')();
let fail=0; const ok=(n,c,extra)=>{ if(!c) fail++; console.log((c?'OK   ':'FAIL ')+n+(extra?'  '+extra:'')); };
// Tune
for(const l of [1,2,3,4]){ const t=A.TUNE_LEVELS[l]; const mine=[0,1,2].map(i=>t[i]?{f:t[i].f,a:Number(String(t[i].a))}:{f:12,a:0}); ok('tune L'+l+' exact=100', A.matchPct(t,mine)>=99.999); const near=mine.map(p=>({...p})); near[0].a=Math.round((near[0].a-0.05)*20)/20; ok('tune L'+l+' one step off < 99.5', A.matchPct(t,near)<99.5, A.matchPct(t,near).toFixed(2)); }
let bad=0; for(let s=1;s<=300;s++){ const t=A.tuneRandom(A.mulberry(s)); if(t.length!==3||t.some(p=>p.f<1||p.f>12||p.a<0.2||p.a>1||Math.abs(p.a*20-Math.round(p.a*20))>1e-9)) bad++; const mine=t.map(p=>({f:p.f,a:Number((Math.round(p.a/0.05)*0.05).toFixed(2))})); if(A.matchPct(t,mine)<99.999) bad++; }
ok('tune random reachable x300', bad===0);
const sp=A.spectrum(A.sampleParts(A.TUNE_LEVELS[3],64),12); ok('spectrum L3', sp[3].toFixed(3)==='0.700'&&sp[5].toFixed(3)==='0.500'&&sp[11].toFixed(3)==='0.300'&&sp[4]<1e-9);
// Snap
bad=0; let kinds={};
for(let seed=1;seed<=400;seed++){ const r=A.mulberry(seed); for(const n of A.SNAP_PLAN){ const q=A.snapRound(r,n);
  if(q.options.length!==4) bad++; const keys=new Set(q.options.map(A.partsKey)); if(keys.size!==4) bad++;
  if(A.partsKey(q.options[q.answer])!==A.partsKey(q.parts)) bad++;
  if(q.parts.length!==n) bad++;
  for(const o of q.options){ if(o.some(p=>p.f<1||p.f>12||!(p.a>0))) bad++; if(new Set(o.map(p=>p.f)).size!==o.length) bad++; }
  // the right option's bars equal the real DFT of the wave
  const real=A.spectrum(A.sampleParts(q.parts,64),12), bars=A.barsOf(q.options[q.answer],12); for(let k=0;k<=12;k++) if(Math.abs(real[k]-bars[k])>1e-9) bad++;
  kinds[q.answer]=(kinds[q.answer]||0)+1; } }
ok('snap rounds valid x3200', bad===0, 'answer positions '+JSON.stringify(kinds));
// Hunt
bad=0;
for(const L of [1,2,3]) for(let seed=1;seed<=300;seed++){ const b=A.huntBoard(A.mulberry(seed),L); if(b.length!==A.HUNT_LEVELS[L].n) bad++; const hid=new Map(b.map(p=>[p.f,p.a]));
  for(let k=1;k<=16;k++){ const r=A.probe(b,k,64); const want=hid.get(k)||0; if(Math.abs(r.amp-want)>1e-9) bad++; } }
ok('hunt probes exact x900 boards', bad===0);
const b3=A.huntBoard(A.mulberry(2026),1); console.log('     first board (seed 2026):', JSON.stringify(b3));
// Circles
const heart=A.epicycles(A.resample(A.heartShape(),256).pts); ok('heart demo', A.circlesNeeded(heart,95)>=1, 'n90 '+A.circlesNeeded(heart,90)+' n95 '+A.circlesNeeded(heart,95)+' fid20 '+heart.fid[20].toFixed(1)+' goals '+A.circleGoals(heart));
const hp=A.heartShape(); ok('heart inside pad', hp.every(p=>p[0]>0.05&&p[0]<0.95&&p[1]>0.05&&p[1]<0.95), 'x '+Math.min(...hp.map(p=>p[0])).toFixed(2)+'..'+Math.max(...hp.map(p=>p[0])).toFixed(2)+' y '+Math.min(...hp.map(p=>p[1])).toFixed(2)+'..'+Math.max(...hp.map(p=>p[1])).toFixed(2));
const circle=Array.from({length:60},(_,i)=>[0.5+0.3*Math.cos(i/60*6.283185),0.5+0.3*Math.sin(i/60*6.283185)]);
ok('circle → goal 0', A.circleGoals(A.epicycles(A.resample(circle,256).pts)).join()==='true,false,false');
const oval=Array.from({length:60},(_,i)=>[0.5+0.35*Math.cos(i/60*6.283185),0.5+0.18*Math.sin(i/60*6.283185)]);
ok('oval → goal 1', A.circleGoals(A.epicycles(A.resample(oval,256).pts)).join()==='false,true,false');
const fig8=Array.from({length:120},(_,i)=>{const t=2*Math.PI*i/120;return [0.5+0.3*Math.sin(t),0.5+0.2*Math.sin(2*t)]});
ok('figure-8 → goal 2', A.circleGoals(A.epicycles(A.resample(fig8,256).pts)).join()==='false,false,true');
const ep=A.epicycles(A.resample(fig8,256).pts); ok('fidelity monotone, ends at 100', ep.fid.every((v,i)=>i===0||v>=ep.fid[i-1]-1e-9)&&ep.fid[ep.fid.length-1]>99.999);
console.log(fail?'FAILURES '+fail:'ALL OK');
