const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const h=fs.readFileSync(process.argv[2],'utf8');fs.writeFileSync('/tmp/pv.html','<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width"><body style="margin:0">'+h);
const b=await chromium.launch();for(const w of [390,1100]){const p=await b.newPage({viewport:{width:w,height:1000}});await p.goto('file:///tmp/pv.html');await p.waitForTimeout(500);
for(const [sel,name] of process.argv.slice(4).map(s=>s.split('='))){const e=await p.$(sel);if(!e)continue;const bb=await e.boundingBox();await p.screenshot({fullPage:true,path:`${process.argv[3]}-${name}-${w}.png`,clip:{x:0,y:Math.max(0,bb.y-20),width:w,height:Math.min(1400,bb.height+40)}});}
const sw=await p.evaluate(()=>document.documentElement.scrollWidth);console.log(w,'scrollWidth',sw);}
await b.close();})();
