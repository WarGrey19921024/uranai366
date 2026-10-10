/* 人生予報 2027年版 誕生日占い 共通JS（fh-b27）
 * 生成元: work/scripts/templates/fh-b27.js（work/scripts/build_html.py が GEN を埋めて work/out/assets/ に出力）
 * 先に fh-b27-setsuiri.js（節入り日時 1930〜2030年）と fh-b27-kyureki.js（旧暦の月の表）を読み込むこと。
 * 計算の規則は work/scripts/calc_*.py と同じ（テスト: work/scripts/test_js_calc.py）。
 * ページ側は <div class="fh-b27" data-m data-d data-base data-sekki> に月日とデータだけを持つ。
 */
(function(G){
  'use strict';
  /*@GEN@*/

  /* ================= 計算（DOMを使わない部分。node からもテストする） ================= */
  var STEM='甲乙丙丁戊己庚辛壬癸'.split(''),BR='子丑寅卯辰巳午未申酉戌亥'.split('');
  var ANI=['ねずみ','うし','とら','うさぎ','たつ','へび','うま','ひつじ','さる','とり','いぬ','いのしし'];
  var STAR=['','一白水星','二黒土星','三碧木星','四緑木星','五黄土星','六白金星','七赤金星','八白土星','九紫火星'];
  /* 後天定位盤の飛泊順（calc_kanshi_kyusei.py の HOUI と同じ） */
  var HOUI=['中央','北西','西','北東','南','北','南西','東','南東'];
  /* 節の順（1月の小寒〜12月の大雪）と、その節から始まる月の十二支の番号 */
  var SETSU_NAME=['小寒','立春','啓蟄','清明','立夏','芒種','小暑','立秋','白露','寒露','立冬','大雪'];
  var SETSU_BRANCH=[1,2,3,4,5,6,7,8,9,10,11,0];
  var TORA_KAN={0:2,5:2,1:4,6:4,2:6,7:6,3:8,8:8,4:0,9:0};
  var SHUKU27=['昴','畢','觜','参','井','鬼','柳','星','張','翼','軫','角','亢','氐','房','心','尾','箕','斗','女','虚','危','室','壁','奎','婁','胃'];
  var MONTH_START={1:'室',2:'奎',3:'胃',4:'畢',5:'参',6:'鬼',7:'張',8:'角',9:'氐',10:'心',11:'斗',12:'虚'};
  var SEAL=['赤い龍','白い風','青い夜','黄色い種','赤い蛇','白い世界の橋渡し','青い手','黄色い星','赤い月','白い犬','青い猿','黄色い人','赤い空歩く人','白い魔法使い','青い鷲','黄色い戦士','赤い地球','白い鏡','青い嵐','黄色い太陽'];
  var TONE=['磁気','月','電気','自己存在','倍音','律動','共振','銀河','太陽','惑星','スペクトル','水晶','宇宙'];
  var ANIMALS=['狼','猿','虎','ライオン','チーター','熊','象','コアラ','ひつじ','ペガサス','黒ひょう','たぬき'];
  var ACOLORS=['レッド','ゴールド','グリーン','ブルー','パープル'];

  function jdn(y,m,d){var a=Math.floor((14-m)/12),yy=y+4800-a,mm=m+12*a-3;return d+Math.floor((153*mm+2)/5)+365*yy+Math.floor(yy/4)-Math.floor(yy/100)+Math.floor(yy/400)-32045;}
  function isLeap(y){return (y%4===0&&y%100!==0)||y%400===0;}
  function sumd(s){return String(s).split('').reduce(function(a,c){return a+Number(c)},0);}
  function mod(a,n){return ((a%n)+n)%n;}

  /* 節入り（日本時間）。FH_B27_SETSU.d[年-y0] は 12個 × "MMDDhhmm" */
  function setsuList(y){
    var SETSU=G.FH_B27_SETSU;if(!SETSU)return null;var s=SETSU.d[y-SETSU.y0];if(!s)return null;
    var out=[];for(var i=0;i<12;i++)out.push(Number(s.substr(i*8,8)));return out;
  }
  /* 誕生時刻は不明なので 12:00（日本時間）で判定する */
  var NOON=1200;
  function stamp(m,d,hm){return m*1000000+d*10000+(hm==null?NOON:hm);}
  function etoYear(y,m,d,hm){var L=setsuList(y);return stamp(m,d,hm)>=L[1]?y:y-1;}
  function monthBranch(y,m,d,hm){var L=setsuList(y),t=stamp(m,d,hm),b=0;/* 小寒より前＝前年の大雪＝子 */
    for(var i=0;i<12;i++){if(t>=L[i])b=SETSU_BRANCH[i];}return b;}
  /* 本命星（立春で切替） */
  function honmei(y,m,d,hm){var ey=etoYear(y,m,d,hm);return {star:mod(11-mod(ey,9),9)||9,etoYear:ey,prev:ey!==y};}
  /* 2027年（九紫火星中宮）の年盤で、その星がいる方位 */
  function palace2027(star){return HOUI[mod(star-GEN.center2027,9)];}
  /* 四柱推命の年柱・月柱・日柱 */
  function pillars(y,m,d,hm){
    var ey=etoYear(y,m,d,hm),yi=mod(ey-4,60),ys=yi%10;
    var b=monthBranch(y,m,d,hm),k=(TORA_KAN[ys]+mod(b-2,12))%10;
    var di=mod(10+(jdn(y,m,d)-jdn(1900,1,1)),60);
    return {year:STEM[ys]+BR[yi%12],month:STEM[k]+BR[b],day:STEM[di%10]+BR[di%12],nikkan:STEM[di%10]};
  }
  /* 誕生日がその年の節入りの日か（時刻で月柱・本命星が変わる日） */
  function setsuDay(y,m,d){var L=setsuList(y);if(!L)return null;var md=m*100+d;
    for(var i=0;i<12;i++){if(Math.floor(L[i]/10000)===md)return SETSU_NAME[i];}return null;}
  /* 旧暦（FH_B27_KYUREKI：月の長さ"9"=29日/"0"=30日 と 月番号 a-l／閏月 A-L） */
  var KY=null;
  function kyInit(){
    if(KY||!G.FH_B27_KYUREKI)return KY;var K=G.FH_B27_KYUREKI,p=K.s.split('-').map(Number),j=jdn(p[0],p[1],p[2]),st=[],mo=[],lp=[];
    for(var i=0;i<K.len.length;i++){var c=K.mon.charAt(i),up=c===c.toUpperCase();st.push(j);mo.push(c.toLowerCase().charCodeAt(0)-96);lp.push(up);j+=K.len.charAt(i)==='9'?29:30;}
    st.push(j);KY={st:st,mo:mo,lp:lp};return KY;
  }
  function kyureki(y,m,d){
    var T=kyInit();if(!T)return null;var j=jdn(y,m,d),lo=0,hi=T.mo.length-1;
    if(j<T.st[0]||j>=T.st[T.st.length-1])return null;
    while(lo<hi){var mid=(lo+hi+1)>>1;if(T.st[mid]<=j)lo=mid;else hi=mid-1;}
    return {month:T.mo[lo],leap:T.lp[lo],day:j-T.st[lo]+1};
  }
  /* 宿曜の本命宿（旧暦の月の1日の宿から日数ぶん進める。閏月はもとの月と同じ） */
  function shuku(y,m,d){var k=kyureki(y,m,d);if(!k)return null;
    return {name:SHUKU27[(SHUKU27.indexOf(MONTH_START[k.month])+k.day-1)%27],kyu:k};}
  /* マヤ暦（ドリームスペル方式・2/29は数えない）基準 2013-07-26 = KIN164 */
  function kin(y,m,d){
    var a=jdn(2013,7,26),b=jdn(y,m,d),n=b-a,lo=Math.min(a,b),hi=Math.max(a,b),leaps=0;
    for(var yy=Math.floor(Math.min(y,2013));yy<=Math.max(y,2013);yy++){if(isLeap(yy)){var f=jdn(yy,2,29);if(f>lo&&f<=hi)leaps++;}}
    n=n>=0?n-leaps:n+leaps;
    var k=mod(163+n,260)+1;return {kin:k,seal:SEAL[(k-1)%20],sealNo:(k-1)%20+1,tone:(k-1)%13+1,toneName:TONE[(k-1)%13]};
  }
  /* ライフパス（全けた足し・11/22/33は残す） */
  function lifePath(y,m,d){var s=sumd(''+y+m+d);while(s>9&&s!==11&&s!==22&&s!==33)s=sumd(s);return s;}
  /* 動物×色（/animal-color/ の calculateAnimal と同じ式） */
  function animal(y,m,d){var b=(y+m*12+d)%60;return {base:b,animal:ANIMALS[b%12],color:ACOLORS[Math.floor(b/12)%5],label:ANIMALS[b%12]+'・'+ACOLORS[Math.floor(b/12)%5]};}
  /* バイオリズム（出生日＝0日） */
  var PER=[23,28,33];
  function bioAt(n){return PER.map(function(p){return Math.sin(2*Math.PI*n/p)});}
  function bioMark(v){return v>=.8?['★',5]:v>=.4?['◎',4]:v>=-.2?['〇',3]:v>=-.6?['△',2]:['▽',1];}
  /* 好調日＝3本の平均0.6以上／注意日＝n〜n+1の間にどれかの線が0を横切る日 */
  function bioGood(n){var v=bioAt(n);return (v[0]+v[1]+v[2])/3>=0.6;}
  function bioCare(n){for(var i=0;i<3;i++){var p=PER[i];if(Math.ceil(2*n/p)<2*(n+1)/p)return true;}return false;}
  function bioDays(by,bm,bd){
    var j=jdn(by,bm,bd),s=jdn(2027,1,1),good=[],care=[];
    for(var k=0;k<365;k++){var n=s+k-j,dt=new Date(2027,0,1+k),lab=(dt.getMonth()+1)+'/'+dt.getDate();
      if(n<0)continue;/* 生まれる前の日は数えない（2027年生まれ） */
      if(bioGood(n))good.push(lab);if(bioCare(n))care.push(lab);}
    return {good:good,care:care};
  }
  var EL={1:'水',2:'土',3:'木',4:'木',5:'土',6:'金',7:'金',8:'土',9:'火'};
  var GENR={'木':'火','火':'土','土':'金','金':'水','水':'木'},CTL={'木':'土','土':'水','水':'火','火':'金','金':'木'};
  function kyuseiScore(me,ms){var a=EL[me],b=EL[ms];if(a===b)return 78;if(GENR[b]===a)return 88;if(GENR[a]===b)return 66;if(CTL[b]===a)return 55;return 72;}
  function wareki(y){if(y>=2019)return '令和'+(y===2019?'元':(y-2018))+'年';if(y>=1989)return y===1989?'昭和64年／平成元年':'平成'+(y-1988)+'年';return '昭和'+(y-1925)+'年';}

  var CALC={jdn:jdn,honmei:honmei,palace2027:palace2027,pillars:pillars,setsuDay:setsuDay,kyureki:kyureki,shuku:shuku,kin:kin,lifePath:lifePath,animal:animal,bioAt:bioAt,bioMark:bioMark,bioGood:bioGood,bioCare:bioCare,bioDays:bioDays,kyuseiScore:kyuseiScore,STAR:STAR};
  /* --- 追加：生年月日まるごと診断（/seinengappi/）用。誕生日ページの計算・表示は変えない --- */
  var SIGN12=['牡羊座','牡牛座','双子座','蟹座','獅子座','乙女座','天秤座','蠍座','射手座','山羊座','水瓶座','魚座'];
  var SIGN_EN=['aries','taurus','gemini','cancer','leo','virgo','libra','scorpio','sagittarius','capricorn','aquarius','pisces'];
  /* 太陽の星座。FH_B27_SIGN.d[年-y0] は各月の星座の切り替わり日時（日本時間）12個 × "DDhhmm"（fh-b27-sign.js・build_seinengappi.py が calc_sekki.py の計算から作る）。
     m月の切り替わりで (m+9)%12 番の星座に入る（1月＝水瓶座 … 12月＝山羊座）。時刻不明なので正午で判定。border＝切り替わりの日（時刻で星座が変わる） */
  function sunSign(y,m,d,hm){
    var S=G.FH_B27_SIGN;if(!S)return null;var s=S.d[y-S.y0];if(!s)return null;
    var t=Number(s.substr((m-1)*6,6)),cur=d*10000+(hm==null?NOON:hm),i=cur>=t?(m+9)%12:(m+8)%12,j=cur>=t?(m+8)%12:(m+9)%12,b=Math.floor(t/10000)===d;
    return {name:SIGN12[i],idx:i,en:SIGN_EN[i],border:b,other:b?SIGN12[j]:null};
  }
  /* 計算できる生まれ年の範囲（節入りの表の範囲＝1930〜2030年） */
  function yearRange(){var S=G.FH_B27_SETSU;return S?{min:S.y0,max:S.y0+S.d.length-1}:{min:GEN.yearMin,max:GEN.yearMax};}
  /* --- その日の総合（改善第2弾）：カレンダーの印と「その日のひとこと」の5段階を同じ計算で出す ---
     点＝2＋日の数（1・3・8は＋0.5、7・9は−0.25）＋日の干支の五行とあなたの五行の関係（生じられる＋1・比和＋0.5・剋す＋0.25・生じる0・剋される−0.75）
        ＋（生まれ年あり）生まれた日の十二支との関係（支合＋1・三合＋0.5・同じ＋0.25・冲−1）＋バイオリズム（好調日＋1・注意日−0.75・平均＞0.2で＋0.5・＜−0.2で−0.5）
        ＋その月の運勢（◎＋0.5・△−0.5）。DAY_CUT で5段階（4＝★追い風 … 0＝▽休む）に分ける。試算は work/scripts/test_day_score.py */
  var STEM_EL=['木','木','火','火','土','土','金','金','水','水'];
  function red(n){while(n>9)n=sumd(n);return n;}
  function pDayOf(py,m,d){return red(red(py+m)+d);}
  function dayKanshi(y,m,d){var i=mod(10+(jdn(y,m,d)-jdn(1900,1,1)),60);return {s:STEM[i%10],b:BR[i%12],si:i%10,bi:i%12};}
  function rel(a,b){if(a===b)return 'same';if(GENR[b]===a)return 'helped';if(GENR[a]===b)return 'give';if(CTL[a]===b)return 'rule';return 'pressed';}
  var GO={0:1,1:0,2:11,11:2,3:10,10:3,4:9,9:4,5:8,8:5,6:7,7:6};
  function brRel(a,b){if(a===b)return 'same';if(GO[a]===b)return 'go';if(mod(a-b,12)===6)return 'chu';if(mod(a-b,12)===4||mod(a-b,12)===8)return 'san';return 'none';}
  var DAY_CUT=[0.75,1.75,2.75,3.5],DAY_CUT_NY=[1.25,2,2.75,3.25];/* 点がこの値以上で ▽0→△1→〇2→◎3→★4。生まれ年なしは材料が少なく点の幅が狭いので別の区切り（どちらも試算で目安の割合に合わせた） */
  var DAY_MARK=['▽','△','〇','◎','★'];
  function dayScore(o,m,d){
    var pd=pDayOf(o.py,m,d),kd=dayKanshi(2027,m,d),me=o.gogyo,ke=STEM_EL[kd.si],score=2,x={pd:pd,kd:kd,ke:ke};
    if(o.year){var bp=pillars(o.year,o.M,o.D);x.bday=bp.day;x.bbi=BR.indexOf(bp.day.charAt(1));me=STEM_EL[STEM.indexOf(bp.day.charAt(0))];}
    x.me=me;
    if(pd===1||pd===3||pd===8)score+=.5;if(pd===7||pd===9)score-=.25;
    x.r=rel(me,ke);score+={helped:1,same:.5,give:0,rule:.25,pressed:-.75}[x.r];
    if(o.year){x.br=brRel(x.bbi,kd.bi);score+={go:1,san:.5,chu:-1,same:.25,none:0}[x.br];
      var k=jdn(2027,m,d)-jdn(o.year,o.M,o.D);
      if(k>=0){var v=bioAt(k),av=(v[0]+v[1]+v[2])/3,g=bioGood(k),c=bioCare(k);x.bio={v:v,av:av,g:g,c:c};score+=g?1:c?-.75:av>.2?.5:av<-.2?-.5:0;}}
    x.mm=o.marks?o.marks[m-1]:'';score+=x.mm==='◎'?.5:x.mm==='△'?-.5:0;
    var cut=o.year?DAY_CUT:DAY_CUT_NY,vi=0;for(var i=0;i<4;i++)if(score>=cut[i])vi=i+1;
    x.score=score;x.vi=vi;x.mark=DAY_MARK[vi];return x;
  }
  CALC.dayScore=dayScore;CALC.pDayOf=pDayOf;CALC.DAY_CUT=DAY_CUT;CALC.DAY_CUT_NY=DAY_CUT_NY;
  CALC.dayKanshiIndex=function(y,m,d){return mod(10+(jdn(y,m,d)-jdn(1900,1,1)),60);};
  CALC.sunSign=sunSign;CALC.yearRange=yearRange;CALC.wareki=wareki;CALC.isLeap=isLeap;CALC.GEN=GEN;CALC.STEM=STEM;CALC.BR=BR;CALC.ANI=ANI;CALC.SIGN12=SIGN12;
  G.FHB27Calc=CALC;

  /* ================= ページの表示（ブラウザだけ） ================= */
  if(typeof document==='undefined')return;
  function boot(){
  var root=document.querySelector('.fh-b27[data-m]');if(!root)return;
  var M=Number(root.getAttribute('data-m')),D=Number(root.getAttribute('data-d'));
  var NS='http://www.w3.org/2000/svg';
  var MONTHS=['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月'];
  var BASE=[];try{BASE=JSON.parse(root.getAttribute('data-base')||'[]');}catch(e){BASE=[];}
  var EXTRA_COLORS={kyusei:'#9085e9',bio:'#d55181'};
  var DIRSLUG={'北':'north','南西':'southwest','東':'east','南東':'southeast','北西':'northwest','西':'west','北東':'northeast','南':'south'};
  function daysIn(m){return new Date(2027,m,0).getDate();}

  var state={year:null,hidden:{},bioMonth:1};
  var LS='fh-b27-hidden';
  try{var h=JSON.parse(localStorage.getItem(LS)||'{}');if(h&&typeof h==='object')state.hidden=h;}catch(e){}
  function series(){
    var list=BASE.map(function(s){return {key:s.key,name:s.name,color:s.color,values:s.values,w:2}});
    if(state.year){
      var me=honmei(state.year,M,D).star;
      list.push({key:'kyusei',name:'九星',color:EXTRA_COLORS.kyusei,w:2,values:GEN.monthStar2027.map(function(ms){return kyuseiScore(me,ms)})});
      var b=jdn(state.year,M,D),bv=[];
      for(var m=1;m<=12;m++){var sum=0,cnt=0,n=daysIn(m);for(var d=1;d<=n;d++){var k=jdn(2027,m,d)-b;if(k<0)continue;var v=bioAt(k);sum+=(v[0]+v[1]+v[2])/3;cnt++;}bv.push(cnt?Math.round(65+30*(sum/cnt)):null);}
      list.push({key:'bio',name:'バイオリズム',color:EXTRA_COLORS.bio,w:2,values:bv});
    }
    var vis=list.filter(function(s){return !state.hidden[s.key]});
    var tot=MONTHS.map(function(_,i){var vs=vis.map(function(s){return s.values[i]}).filter(function(v){return v!=null});if(!vs.length)return null;return Math.round(vs.reduce(function(a,v){return a+v},0)/vs.length)});
    list.unshift({key:'total',name:'総合',color:'#ECE7DA',values:tot,w:3,total:true});
    return list;
  }
  /* --- 汎用の折れ線グラフ --- */
  function el(tag,attrs,parent){var e=document.createElementNS(NS,tag);for(var k in attrs)e.setAttribute(k,attrs[k]);if(parent)parent.appendChild(e);return e;}
  function lineChart(box,opt){
    box.innerHTML='';
    var W=Math.max(280,(box.clientWidth||640)-8),H=opt.h||260,L=34,R=12,T=14,B=28,pw=W-L-R,ph=H-T-B,n=opt.labels.length;
    var svg=el('svg',{width:W,height:H,viewBox:'0 0 '+W+' '+H,role:'img','aria-label':opt.aria},box);
    function x(i){return L+(n===1?pw/2:pw*i/(n-1));}
    function y(v){return T+ph*(1-(v-opt.min)/(opt.max-opt.min));}
    opt.grid.forEach(function(g){el('line',{x1:L,x2:W-R,y1:y(g),y2:y(g),stroke:g===opt.base?'#6B7898':'#33405C','stroke-width':1,'stroke-dasharray':g===opt.base?'':'3 4'},svg);var t=el('text',{x:L-6,y:y(g)+4,'text-anchor':'end',fill:'#A9A497','font-size':11},svg);t.textContent=opt.gridLabel?opt.gridLabel(g):g;});
    if(opt.bands)opt.bands.forEach(function(b){el('rect',{x:x(b.i)-pw/(n-1)/2,y:T,width:pw/(n-1),height:ph,fill:b.color,opacity:b.op},svg);});
    var step=opt.labelStep||1;
    opt.labels.forEach(function(lb,i){if(i%step&&i!==n-1)return;var t=el('text',{x:x(i),y:H-8,'text-anchor':'middle',fill:'#A9A497','font-size':11},svg);t.textContent=lb;});
    opt.series.forEach(function(s){
      if(s.off)return;var d='';s.values.forEach(function(v,i){if(v==null)return;d+=(d?'L':'M')+x(i).toFixed(1)+' '+y(v).toFixed(1);});
      el('path',{d:d,fill:'none',stroke:s.color,'stroke-width':s.w,'stroke-linejoin':'round','stroke-linecap':'round'},svg);
      if(s.dots)s.values.forEach(function(v,i){if(v!=null)el('circle',{cx:x(i),cy:y(v),r:4,fill:s.color,stroke:'#1F2638','stroke-width':2},svg);});
    });
    var cross=el('line',{x1:0,x2:0,y1:T,y2:T+ph,stroke:'#ECE7DA','stroke-width':1,opacity:0},svg);
    var tip=document.createElement('div');tip.className='fh-b27-tip';tip.hidden=true;box.appendChild(tip);
    function show(i){
      cross.setAttribute('x1',x(i));cross.setAttribute('x2',x(i));cross.setAttribute('opacity',.5);
      tip.innerHTML='<b>'+opt.labels[i]+(opt.tipSuffix||'')+'</b>'+opt.series.filter(function(s){return !s.off}).map(function(s){return '<span><i style="background:'+s.color+'"></i>'+s.name+'<em>'+(opt.fmt?opt.fmt(s.values[i]):s.values[i])+'</em></span>'}).join('');
      tip.hidden=false;var tx=x(i)+12;if(tx+170>W)tx=x(i)-182;tip.style.left=Math.max(0,tx)+'px';tip.style.top=T+'px';
    }
    function hide(){cross.setAttribute('opacity',0);tip.hidden=true;}
    var hitW=pw/Math.max(1,n-1);
    opt.labels.forEach(function(_,i){var r=el('rect',{x:x(i)-hitW/2,y:0,width:hitW,height:H,fill:'transparent'},svg);r.addEventListener('mouseenter',function(){show(i)});r.addEventListener('click',function(){show(i)});});
    svg.addEventListener('mouseleave',hide);
  }
  /* --- 月別グラフ --- */
  var chartBox=document.getElementById('fh-b27-chart'),legBox=document.getElementById('fh-b27-leg'),tbl=document.getElementById('fh-b27-tbl');
  function drawMain(){
    if(!chartBox)return;
    var ss=series();
    legBox.innerHTML='';
    ss.forEach(function(s){
      var b=document.createElement('button');b.type='button';b.className='fh-b27-legbtn';
      var on=s.total||!state.hidden[s.key];b.setAttribute('aria-pressed',on?'true':'false');
      b.innerHTML='<i style="background:'+s.color+(s.total?';height:4px':'')+'"></i>'+s.name;
      if(s.total){b.disabled=true;}else b.addEventListener('click',function(){state.hidden[s.key]=!state.hidden[s.key];try{localStorage.setItem(LS,JSON.stringify(state.hidden))}catch(e){}drawMain();});
      legBox.appendChild(b);
    });
    var drawn=ss.map(function(s){return {name:s.name,color:s.color,values:s.values,w:s.w,dots:s.total,off:!s.total&&state.hidden[s.key]}});
    lineChart(chartBox,{labels:MONTHS,series:drawn,min:20,max:100,grid:[20,40,60,80,100],aria:'2027年の月別運勢。占いごとの折れ線と総合',tipSuffix:'の運勢'});
    var h='<table><thead><tr><th>月</th>'+ss.map(function(s){return '<th>'+s.name+'</th>'}).join('')+'</tr></thead><tbody>';
    MONTHS.forEach(function(m,i){h+='<tr><th>'+m+'</th>'+ss.map(function(s){return '<td>'+(s.values[i]==null?'—':s.values[i])+'</td>'}).join('')+'</tr>'});
    tbl.innerHTML=h+'</tbody></table>';
  }
  /* --- 生まれる前の日はバイオリズムを出さない（2027〜2030年生まれ） --- */
  function born(k){return k>=0;}
  /* --- バイオリズム（月ごと）：カレンダー表示とグラフ表示、日付を押すと「その日のひとこと」 --- */
  var BD=(root.getAttribute('data-bday')||(M+'-'+D)).split('-').map(Number);
  var now=new Date(),inY=now.getFullYear()===2027;
  state.bioMonth=inY?now.getMonth()+1:BD[0];
  state.pick=inY?{m:now.getMonth()+1,d:now.getDate()}:{m:BD[0],d:BD[1]};
  state.view='cal';
  var PY=Number(root.getAttribute('data-py'))||1,GOGYO=root.getAttribute('data-gogyo')||'土';
  function pDay(m,d){return pDayOf(PY,m,d);}
  /* 12か月の運勢（ページの中の◎○△と一行）を読む */
  var MMARK=[],MLINE=[];
  root.querySelectorAll('.fh-b27-months > div').forEach(function(x){var b=x.querySelector('b');MMARK.push(b?b.textContent.trim():'');});
  root.querySelectorAll('.fh-b27-monthlist > div').forEach(function(x){var sp=x.querySelectorAll('span'),t=sp.length?sp[sp.length-1].textContent:'';var i=t.indexOf('。');t=i>0?t.slice(0,i+1):t;if(t.length>46)t=t.slice(0,45)+'…';MLINE.push(t);});
  function opts(){return {M:M,D:D,py:PY,gogyo:GOGYO,year:state.year,marks:MMARK.length===12?MMARK:null};}
  function pickv(arr,seed){return arr[mod(seed,arr.length)];}
  var PD_TIP={1:['新しいことを一つだけ始めてみて。','迷っていたことに、今日は答えを出してみて。'],2:['返事は少しゆっくりめに、言葉は丁寧に。','一人で決めず、誰かに相談すると話がまとまりやすい日。'],3:['楽しいと思うことを、まず自分に許してあげて。','気軽な連絡や雑談から、いい話が転がり込みそう。'],4:['机の上や予定表を整えると、気持ちも落ち着きます。','派手さより、決めたことを一つずつ。'],5:['いつもと違う道や店を選ぶと、小さな発見があります。','予定が変わっても、それを楽しむくらいでちょうどいい日。'],6:['家族や身近な人に「ありがとう」を伝えてみて。','頼まれごとを気持ちよく引き受けると、運が巡ります。'],7:['ひとりで考える時間を少しだけ確保して。','調べものや読書に向く日。無理に人に合わせなくて大丈夫。'],8:['先送りにしていた仕事や手続きを片づけるチャンス。','数字やお金のことを、今日のうちに確かめておくと安心。'],9:['使わない物を一つ手放すと、気持ちが軽くなります。','誰かのために動くと、自分にもいい流れが返ってきます。']};
  var EL_TXT={helped:['日の干支「{k}」は、あなたの「{me}」を育てる「{el}」の気。周りの助けを受け取りやすい日です。','「{k}」の日は、{el}の気があなたの{me}を後押し。人の厚意は素直に受け取って。'],same:['「{k}」の日は、あなたと同じ「{el}」の気。自分らしさを出しやすく、勢いもつきます。','日の干支「{k}」はあなたと同じ{el}の気。得意なことで力を発揮しやすい日です。'],give:['「{k}」の日は、あなたの{me}が「{el}」を生む関係。人に何かを与えると喜ばれる日です。','日の干支「{k}」は、あなたが力を注ぐ側に回る組み合わせ。張り切りすぎには気をつけて。'],rule:['「{k}」の日は、あなたの{me}が「{el}」をおさえる関係。主導権を握りやすい反面、言い方はやわらかく。','日の干支「{k}」とは、あなたがリードする組み合わせ。仕切る場面で力が出ます。'],pressed:['「{k}」の日は、「{el}」の気があなたの{me}をおさえる関係。予定は詰め込みすぎずに。','日の干支「{k}」は少しプレッシャーを感じやすい組み合わせ。早めに休むのが吉です。']};
  var BR_TXT={go:'生まれた日の「{b}」と今日の「{t}」は引き合う関係（支合）。人との縁が結ばれやすい日です。',san:'生まれた日の「{b}」と今日の「{t}」は仲間の関係（三合）。協力すると物事が進みます。',chu:'生まれた日の「{b}」と今日の「{t}」は向かい合う関係（冲）。予定の変更や行き違いに気をつけて。',same:'今日は生まれた日と同じ「{t}」の日。原点に返るような出来事がありそうです。',none:''};
  var VERD=[['ゆっくり休む日','無理をせず、体と心を休めることを優先して。'],['ひと息つく日','大きな決断は別の日に回し、身の回りを整える日に。'],['ふつうの日','いつものペースを大切に。小さな楽しみを一つ見つけて。'],['いい流れの日','気になっていたことに手をつけるのに向いています。'],['追い風の日','大切な予定や、人に会う用事を入れるのに向く日です。']];
  function fill(t,o){return t.replace(/\{(\w+)\}/g,function(_,k){return o[k]});}
  var MM_TXT={'◎':'この月は12か月の運勢で◎の月。流れに乗って動きやすい時期です。','○':'この月は12か月の運勢で○の月。いつもの調子で進めて大丈夫。','△':'この月は12か月の運勢で△の月。月全体が慎重に過ごしたい時期なので、少し控えめに。'};
  function dayFortune(m,d){
    var y=state.year,x=dayScore(opts(),m,d),pd=x.pd,kd=x.kd,seed=m*31+d,lines=[],me=x.me,ke=x.ke,vi=x.vi;
    var label=y?'生まれた日の日干「'+x.bday.charAt(0)+'」':'星座の五行';
    lines.push(['日の数 '+pd,'「'+(GEN.pdKw[pd]||'')+'」。'+pickv(PD_TIP[pd],seed)]);
    lines.push(['日の干支 '+kd.s+kd.b,fill(pickv(EL_TXT[x.r],seed+d),{k:kd.s+kd.b,me:me,el:ke})+'（あなたの五行は'+label+'の「'+me+'」で見ています）']);
    if(y){if(BR_TXT[x.br])lines.push(['生まれた日との関係',fill(BR_TXT[x.br],{b:BR[x.bbi],t:kd.b})]);
      if(!x.bio)lines.push(['バイオリズム','まだ生まれる前の日なので、バイオリズムは出しません。']);
      else{var v=x.bio.v,av=x.bio.av,g=x.bio.g,c=x.bio.c;
        lines.push(['バイオリズム','身体'+bioMark(v[0])[0]+'・感情'+bioMark(v[1])[0]+'・知性'+bioMark(v[2])[0]+'。'+(g?'3つの波がそろって高い「好調日」です。':c?'波が切り替わる「注意日」。うっかりミスに気をつけて。':av>.2?'波は上向きで、動きやすい日。':av<-.2?'波は低めなので、ペースを落として。':'波はおだやかな日です。')]);}}
    if(MM_TXT[x.mm])lines.push([m+'月の運勢 '+x.mm,MM_TXT[x.mm]]);
    var W='日月火水木金土'.charAt(new Date(2027,m-1,d).getDay());
    var h='<div class="fh-b27-dayhead"><b>2027年'+m+'月'+d+'日（'+W+'）</b><span class="fh-b27-verd fh-b27-v'+vi+'">'+x.mark+' '+VERD[vi][0]+'</span></div>';
    h+='<p class="fh-b27-daysum">'+VERD[vi][1]+'</p><dl>';
    lines.forEach(function(l){h+='<div><dt>'+l[0]+'</dt><dd>'+l[1]+'</dd></div>';});
    h+='</dl>'+(y?'':'<p class="fh-b27-small">生まれ年を選ぶと、生まれた日の干支との関係とバイオリズムも加えて読みます。</p>');
    h+='<a class="fh-b27-next fh-b27-omikuji" href="/omikuji/"><i class="fh-b27-ic fh-b27-ic-omikuji fh-b27-nextic" aria-hidden="true"></i><span><small>運だめしに</small><b>今日のおみくじを引く →</b></span></a>';
    return h;
  }
  function drawDay(){var o=document.getElementById('fh-b27-dayout');if(!o||!state.pick)return;o.innerHTML=dayFortune(state.pick.m,state.pick.d);}
  function drawCal(){
    var box=document.getElementById('fh-b27-cal');if(!box)return;
    var m=state.bioMonth,n=daysIn(m),first=new Date(2027,m-1,1).getDay(),b=state.year?jdn(state.year,M,D):null;
    var h='<div class="fh-b27-calhead">'+'日月火水木金土'.split('').map(function(w,i){return '<span'+(i===0?' class="fh-b27-sun"':i===6?' class="fh-b27-sat"':'')+'>'+w+'</span>'}).join('')+'</div><div class="fh-b27-calgrid">';
    for(var i=0;i<first;i++)h+='<span class="fh-b27-calpad"></span>';
    var o=opts();
    for(var d=1;d<=n;d++){var cls='fh-b27-cday',x=dayScore(o,m,d),mk=x.mark;
      if(b!==null){var k=jdn(2027,m,d)-b;if(born(k)){if(bioGood(k))cls+=' fh-b27-cg';else if(bioCare(k))cls+=' fh-b27-cc';}}
      cls+=' fh-b27-cm'+x.vi;
      var sub='<span class="fh-b27-cmk">'+mk+'</span><span class="fh-b27-cpd">'+x.pd+'</span>';
      if(state.pick&&state.pick.m===m&&state.pick.d===d)cls+=' fh-b27-csel';
      if(m===BD[0]&&d===BD[1])cls+=' fh-b27-cbd';
      h+='<button type="button" class="'+cls+'" data-d="'+d+'" aria-label="'+m+'月'+d+'日'+(mk?'（'+mk+'）':'')+'"><b>'+d+'</b><small>'+sub+'</small></button>';}
    var mh=MMARK[m-1]?'<div class="fh-b27-calmonth"><b>2027年'+m+'月</b><span class="fh-b27-mark fh-b27-'+(MMARK[m-1]==='◎'?'good':MMARK[m-1]==='△'?'care':'ok')+'">'+MMARK[m-1]+'</span><span>'+(MLINE[m-1]||'')+'</span></div>':'';
    box.innerHTML=mh+h+'</div><p class="fh-b27-small"><b>印（★◎〇△▽）＝その日の総合</b>（日の数・日の干支・その月の運勢'+(b!==null?'・生まれた日との関係・バイオリズム':'')+'から。押すと出る「その日のひとこと」と同じ5段階）。小さな数字はその日の数（数秘）。'+(b!==null?'<b>色＝バイオリズム</b>（金色＝好調日、灰色＝注意日）。':'')+'誕生日は点線の枠。</p>';
    box.querySelectorAll('button').forEach(function(bt){bt.addEventListener('click',function(){state.pick={m:m,d:Number(bt.getAttribute('data-d'))};drawCal();drawDay();});});
  }
  function drawBio(){
    var mb=document.getElementById('fh-b27-mbtn');if(mb)mb.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed',Number(x.value)===state.bioMonth?'true':'false')});
    root.querySelectorAll('[data-fh-view]').forEach(function(x){var v=x.getAttribute('data-fh-view');x.setAttribute('aria-pressed',v===state.view?'true':'false');if(v==='graph')x.disabled=!state.year;});
    var cal=document.getElementById('fh-b27-cal'),box=document.getElementById('fh-b27-bchart');
    if(!cal)state.view='graph';/* 古い本文（カレンダーの無いページ）でもグラフを出す */
    else if(state.view==='graph'&&!state.year)state.view='cal';
    if(cal)cal.hidden=state.view!=='cal';var cb=root.querySelector('.fh-b27-calbox');if(cb)cb.setAttribute('data-view',state.view);if(box)box.hidden=state.view!=='graph';
    drawCal();drawDay();
    if(!box)return;if(!state.year){box.innerHTML='';return;}
    var b=jdn(state.year,M,D),m=state.bioMonth,n=daysIn(m),p=[],e=[],it=[],labels=[],bands=[];
    for(var d=1;d<=n;d++){var k=jdn(2027,m,d)-b,v=bioAt(k),ok=born(k);p.push(ok?Math.round(v[0]*100):null);e.push(ok?Math.round(v[1]*100):null);it.push(ok?Math.round(v[2]*100):null);labels.push(m+'/'+d);
      if(ok&&bioGood(k))bands.push({i:d-1,color:'#E3C77E',op:.3});else if(ok&&bioCare(k))bands.push({i:d-1,color:'#8A8678',op:.25});}
    if(state.view==='graph')lineChart(box,{labels:labels,labelStep:5,series:[{name:'身体',color:'#d95926',values:p,w:2},{name:'感情',color:'#3987e5',values:e,w:2},{name:'知性',color:'#199e70',values:it,w:2}],min:-100,max:100,base:0,grid:[-100,-50,0,50,100],h:220,bands:bands,aria:'2027年'+m+'月のバイオリズム',fmt:function(v){return v==null?'—':(v>0?'+':'')+v}});
    var W='日月火水木金土'.split(''),h='<table class="fh-b27-btab"><thead><tr><th>日付</th><th>曜日</th><th>身体</th><th>感情</th><th>知性</th><th>総合</th></tr></thead><tbody>';
    for(var dd=1;dd<=n;dd++){var kk=jdn(2027,m,dd)-b,cells;
      if(born(kk)){var vv=bioAt(kk),av=(vv[0]+vv[1]+vv[2])/3;cells=[vv[0],vv[1],vv[2],av].map(function(x){var q=bioMark(x);return '<td class="fh-b27-s'+q[1]+'">'+q[0]+'</td>'}).join('');}
      else cells='<td colspan="4">（生まれる前）</td>';
      h+='<tr><th>'+dd+'</th><td>'+W[new Date(2027,m-1,dd).getDay()]+'</td>'+cells+'</tr>';}
    document.getElementById('fh-b27-btable').innerHTML=h+'</tbody></table>';
    document.getElementById('fh-b27-btitle').textContent='2027年'+m+'月のバイオリズム（日ごとの表）';
  }
  function txt(id,s){var e=document.getElementById(id);if(e)e.textContent=s;}
  function drawPanel(){
    var mine=document.getElementById('fh-b27-mine'),bw=document.getElementById('fh-b27-biowrap');
    if(!mine)return;
    root.querySelectorAll('[data-fh-noyear]').forEach(function(x){x.hidden=!!state.year;});
    if(!state.year){mine.hidden=true;if(bw)bw.hidden=true;drawBio();return;}
    mine.hidden=false;if(bw)bw.hidden=false;
    var y=state.year,h=honmei(y,M,D),pos=palace2027(h.star),sd=setsuDay(y,M,D);
    txt('fh-b27-star',STAR[h.star]);
    txt('fh-b27-star-n',(h.prev?'立春前の生まれなので前年（'+h.etoYear+'年）の星。':'')+(GEN.kyuseiKw[h.star]?'「'+GEN.kyuseiKw[h.star]+'」の星。':'')+'2027年の位置：'+pos);
    var ci=mod(y-4,12);
    txt('fh-b27-eto',STEM[mod(y-4,10)]+BR[ci]+'・'+ANI[ci]+'年');
    var pl=pillars(y,M,D);
    txt('fh-b27-eto-n',h.prev?'四柱推命・九星気学では立春で年が切り替わるため、'+M+'月'+D+'日生まれは前年の「'+pl.year+'」として計算します。':'一般の干支（1月1日切り替え）。四柱推命の年柱も同じ「'+pl.year+'」です。');
    txt('fh-b27-pillars',pl.year+'年 ・ '+pl.month+'月 ・ '+pl.day+'日');
    var nk=GEN.nikkan[pl.nikkan];
    txt('fh-b27-nikkan-n','日干は「'+pl.nikkan+'」'+(nk?'＝'+nk:'')+'。'+(sd?'この年は'+M+'月'+D+'日が「'+sd+'」の節入りの日なので、生まれた時刻によって月柱'+(sd==='立春'?'・年柱・本命星':'')+'が変わります（正午生まれとして計算）。':''));
    var dir=document.getElementById('fh-b27-dir');if(dir){dir.href=DIRSLUG[pos]?'/kaiun/direction-'+DIRSLUG[pos]+'/':'/kaiun/compass/';dir.textContent=DIRSLUG[pos]?pos+'の方角の意味を開運ライフで見る →':'8方位の読み方を開運ライフで見る →';}
    var sk=shuku(y,M,D);
    if(sk){txt('fh-b27-shuku',sk.name+'宿');txt('fh-b27-shuku-n','旧暦'+(sk.kyu.leap?'閏':'')+sk.kyu.month+'月'+sk.kyu.day+'日の生まれ。'+(GEN.shukuKw[sk.name]?'キーワードは「'+GEN.shukuKw[sk.name]+'」。':''));}
    else{txt('fh-b27-shuku','—');txt('fh-b27-shuku-n','この年は計算の範囲外です');}
    var kk=kin(y,M,D);txt('fh-b27-kin','KIN'+kk.kin);
    txt('fh-b27-kin-n','太陽の紋章「'+kk.seal+'」'+(GEN.sealKw[kk.sealNo]?'（'+GEN.sealKw[kk.sealNo]+'）':'')+'・銀河の音'+kk.tone+'「'+kk.toneName+'」'+(GEN.toneKw[kk.tone]?'（'+GEN.toneKw[kk.tone]+'）':''));
    var lp=lifePath(y,M,D);txt('fh-b27-lp',String(lp));
    txt('fh-b27-lp-n',(GEN.lpKw[lp]?'「'+GEN.lpKw[lp]+'」の数。':'')+'生年月日の数字をすべて足して出す数');
    txt('fh-b27-animal',animal(y,M,D).label);
    var bd=bioDays(y,M,D),bio=document.getElementById('fh-b27-bio');
    if(bio)bio.innerHTML=(y>=2027?'<b>2027年の誕生日より前の日は数えていません。</b><br>':'')+'<b>好調日（金色・'+bd.good.length+'日）</b>　'+(bd.good.join('、')||'—')+'<br><b>注意日（灰色・'+bd.care.length+'日）</b>　'+(bd.care.join('、')||'—');
    drawBio();
  }
  function drawNotes(){
    root.querySelectorAll('[data-fh-yearnote]').forEach(function(e){
      e.innerHTML=state.year?('<b>'+state.year+'年（'+wareki(state.year)+'）</b>生まれで表示中。ここで選び直してもページ全体に反映されます'):'選ぶと「あなた専用」の表示に変わります（'+GEN.yearMin+'〜'+GEN.yearMax+'年）';
    });
  }
  /* --- 年の選択（ページ上部の1か所） --- */
  var sels=root.querySelectorAll('[data-fh-year]');
  sels.forEach(function(sel){
    var o=document.createElement('option');o.value='';o.textContent='選ばない';sel.appendChild(o);
    for(var y=GEN.yearMax;y>=GEN.yearMin;y--){if(M===2&&D===29&&!isLeap(y))continue;o=document.createElement('option');o.value=y;o.textContent=y+'年（'+wareki(y)+'）';sel.appendChild(o);}
    sel.addEventListener('change',function(){state.year=sel.value?Number(sel.value):null;sels.forEach(function(s2){s2.value=sel.value});drawMain();drawPanel();drawNotes();});
  });
  /* --- スマホ：生まれ年の選択欄が画面に無いとき、画面下に小さな「生まれ年 ▼」を出す --- */
  var fl=document.getElementById('fh-b27-yfloat'),ybar=document.getElementById('b27-yearbar');
  if(fl&&ybar&&'IntersectionObserver' in window){
    var vis={},watch=[ybar].concat([].slice.call(root.querySelectorAll('.fh-b27-ypick')));
    var top=root.querySelector('#b27-nature'),end=root.querySelector('#b27-letter'),past=false,before=true;
    var upd=function(){var any=Object.keys(vis).some(function(k){return vis[k]});fl.hidden=any||!past||!before;};
    var io=new IntersectionObserver(function(es){es.forEach(function(en){var i=watch.indexOf(en.target);if(i>=0)vis[i]=en.isIntersecting;});upd();});
    watch.forEach(function(w){io.observe(w)});
    var chk=function(){var r=top?top.getBoundingClientRect().top:0,q=end?end.getBoundingClientRect().top:1e9;past=r<window.innerHeight*.5;before=q>window.innerHeight*.6;upd();};
    window.addEventListener('scroll',chk,{passive:true});chk();
  }
  root.querySelectorAll('[data-fh-view]').forEach(function(bt){bt.addEventListener('click',function(){state.view=bt.getAttribute('data-fh-view');drawBio();});});
  var mb=document.getElementById('fh-b27-mbtn');
  if(mb)MONTHS.forEach(function(lb,i){var b=document.createElement('button');b.type='button';b.value=i+1;b.textContent=lb;b.className='fh-b27-mb';b.addEventListener('click',function(){state.bioMonth=i+1;if(!state.pick||state.pick.m!==i+1)state.pick={m:i+1,d:(i+1===BD[0]?BD[1]:1)};drawBio();});mb.appendChild(b);});
  var rt;window.addEventListener('resize',function(){clearTimeout(rt);rt=setTimeout(function(){drawMain();drawBio();},150);});
  drawMain();drawPanel();drawNotes();

  /* --- 誕生日カードを画像で保存（canvasに描いてPNGにする） --- */
  var card=root.querySelector('.fh-b27-card');
  var saveBtn=root.querySelector('[data-fh-action="save-card"]');
  if(saveBtn&&card)saveBtn.addEventListener('click',function(ev){
    ev.preventDefault();
    var go=function(){
      var c=document.createElement('canvas'),W=1080,H=1350;c.width=W;c.height=H;var x=c.getContext('2d');
      x.fillStyle='#1F2638';x.fillRect(0,0,W,H);
      x.fillStyle='#33405C';for(var gy=20;gy<H;gy+=44)for(var gx=20;gx<W;gx+=44){x.beginPath();x.arc(gx,gy,2.4,0,7);x.fill();}
      x.save();x.translate(W/2,H/2);x.rotate(-0.025);
      x.fillStyle='#F7F1E3';x.fillRect(-430,-520,860,1040);
      x.fillStyle='rgba(227,199,126,.85)';x.fillRect(-110,-548,220,56);
      x.fillStyle='#6B645B';x.font='600 30px "Klee One", cursive';x.fillText('誕生日カード',-370,-430);
      x.textAlign='right';x.font='26px "Zen Kaku Gothic New", sans-serif';x.fillText(card.getAttribute('data-no')||'',370,-430);x.textAlign='left';
      x.fillStyle='#2E2A26';x.font='800 150px "Shippori Mincho", serif';x.fillText(card.getAttribute('data-label')||(M+'/'+D),-370,-250);
      x.font='600 56px "Klee One", cursive';x.fillText(card.getAttribute('data-title')||'',-370,-150);
      var rows=root.querySelectorAll('.fh-b27-card dl > div'),yy=-50;
      rows.forEach(function(r){x.fillStyle='#6B645B';x.font='30px "Zen Kaku Gothic New", sans-serif';x.fillText(r.querySelector('dt').textContent,-370,yy);
        x.fillStyle='#2E2A26';x.font='700 34px "Zen Kaku Gothic New", sans-serif';x.textAlign='right';x.fillText(r.querySelector('dd').textContent,370,yy);x.textAlign='left';
        x.strokeStyle='#CFC6B5';x.setLineDash([6,6]);x.beginPath();x.moveTo(-370,yy+20);x.lineTo(370,yy+20);x.stroke();x.setLineDash([]);yy+=62;});
      x.fillStyle='#6B645B';x.font='28px "Zen Kaku Gothic New", sans-serif';x.fillText('人生予報 ｜ uranai.epoch-compass.com',-370,470);
      x.restore();
      c.toBlob(function(b){var u=URL.createObjectURL(b),a=document.createElement('a');a.href=u;a.download='birthday-card-'+(card.getAttribute('data-mmdd')||'')+'.png';document.body.appendChild(a);a.click();a.remove();setTimeout(function(){URL.revokeObjectURL(u)},4000);},'image/png');
    };
    if(document.fonts&&document.fonts.ready)document.fonts.ready.then(go);else go();
  });
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();

  /* ================= 追加：生年月日まるごと診断（<div class="fh-b27" data-fh-page="seinengappi">）だけで動く ================= */
  function bootSeinen(){
    var root=document.querySelector('.fh-b27[data-fh-page="seinengappi"]');if(!root)return;
    var R=yearRange(),$=function(id){return document.getElementById('fh-b27-sg-'+id)};
    var fy=$('y'),fm=$('m'),fd=$('d'),out=$('out');if(!fy||!fm||!fd||!out)return;
    function wlabel(y){return y===2019?'平成31年／令和元年':wareki(y);}
    function opt(sel,v,label){var o=document.createElement('option');o.value=v;o.textContent=label;sel.appendChild(o);}
    opt(fy,'','年');for(var y=R.max;y>=R.min;y--)opt(fy,y,y+'年（'+wlabel(y)+'）');
    opt(fm,'','月');for(var m=1;m<=12;m++)opt(fm,m,m+'月');
    function fillDays(){
      var y=Number(fy.value)||2000,m=Number(fm.value)||1,n=new Date(y,m,0).getDate(),keep=Number(fd.value);
      fd.innerHTML='';opt(fd,'','日');for(var d=1;d<=n;d++)opt(fd,d,d+'日');
      if(keep&&keep<=n)fd.value=keep;
    }
    fillDays();
    function t(id,s){var e=$(id);if(e)e.textContent=s;}
    function link(id,href,s){var e=$(id);if(e){e.href=href;if(s!=null)e.textContent=s;}}
    function pad(n){return (n<10?'0':'')+n;}
    var last=null;
    function render(){
      var y=Number(fy.value),m=Number(fm.value),d=Number(fd.value);
      if(!y||!m||!d){out.hidden=true;last=null;return false;}
      var h=honmei(y,m,d),pl=pillars(y,m,d),sg=sunSign(y,m,d),sk=shuku(y,m,d),kk=kin(y,m,d),lp=lifePath(y,m,d),an=animal(y,m,d),sd=setsuDay(y,m,d);
      var ci=mod(y-4,12),eto=STEM[mod(y-4,10)]+BR[ci],nk=GEN.nikkan[pl.nikkan]||'',mmdd=pad(m)+'-'+pad(d);
      last={y:y,m:m,d:d};
      t('date',y+'/'+m+'/'+d);t('sub',y+'年（'+wlabel(y)+'）'+m+'月'+d+'日生まれ');
      /* カード */
      t('c-sign',sg?sg.name:'—');t('c-star',STAR[h.star]);t('c-eto',eto+'（'+ANI[ci]+'）');
      t('c-pillars',pl.year+'・'+pl.month+'・'+pl.day);t('c-nikkan',pl.nikkan+(nk?'（'+nk.split('（')[0]+'）':''));
      t('c-shuku',sk?sk.name+'宿':'—');t('c-kin','KIN'+kk.kin);t('c-seal',kk.seal+'／音'+kk.tone);
      t('c-lp',String(lp));t('c-animal',an.label);
      /* くわしく */
      t('sign',sg?sg.name:'—');
      t('sign-n',sg&&sg.border?'星座の境目の日です。この年は'+m+'月'+d+'日のうちに太陽が星座を移るため、生まれた時刻によっては'+sg.other+'になります（正午生まれとして計算）。':'太陽がどの星座にあったかで決まる、西洋占星術の基本の星座です。');
      if(sg)link('sign-a','/'+sg.en+'/',sg.name+'の運勢を見る →');
      t('star',STAR[h.star]);
      t('star-n',(h.prev?'立春前の生まれなので、前年（'+h.etoYear+'年）の星になります。':'')+(GEN.kyuseiKw[h.star]?'「'+GEN.kyuseiKw[h.star]+'」の星。':'')+'2027年の年盤では'+palace2027(h.star)+'にいます。');
      t('eto',eto+'・'+ANI[ci]+'年');
      t('eto-n',h.prev?'ふだんの干支（1月1日で切り替え）です。四柱推命・九星気学では立春で年が切り替わるため、'+m+'月'+d+'日生まれは前年の「'+pl.year+'」として計算します。':'ふだんの干支（1月1日で切り替え）。四柱推命の年柱も同じ「'+pl.year+'」です。');
      t('pillars',pl.year+'年・'+pl.month+'月・'+pl.day+'日');
      t('pillars-n','日干は「'+pl.nikkan+'」'+(nk?'＝'+nk:'')+'。'+(sd?'この年は'+m+'月'+d+'日が「'+sd+'」の節入りの日なので、生まれた時刻によって月柱'+(sd==='立春'?'・年柱・本命星':'')+'が変わります（正午生まれとして計算）。':'生まれた時刻（時柱）は使わず、年・月・日の3つの柱で見ています。'));
      if(sk){t('shuku',sk.name+'宿');t('shuku-n','旧暦'+(sk.kyu.leap?'閏':'')+sk.kyu.month+'月'+sk.kyu.day+'日の生まれ。'+(GEN.shukuKw[sk.name]?'キーワードは「'+GEN.shukuKw[sk.name]+'」。':''));}
      else{t('shuku','—');t('shuku-n','この日は計算の範囲外です');}
      t('kin','KIN'+kk.kin);
      t('kin-n','太陽の紋章「'+kk.seal+'」'+(GEN.sealKw[kk.sealNo]?'（'+GEN.sealKw[kk.sealNo]+'）':'')+'・銀河の音'+kk.tone+'「'+kk.toneName+'」'+(GEN.toneKw[kk.tone]?'（'+GEN.toneKw[kk.tone]+'）':''));
      t('lp',String(lp));t('lp-n',(GEN.lpKw[lp]?'「'+GEN.lpKw[lp]+'」の数。':'')+'生年月日の数字をすべて足して出す数です。');
      t('animal',an.label);
      /* タイプの短い解説（type_texts.json）と2027年のひとこと */
      var TT=GEN.typeTexts||{},g=function(o,k){return o&&o[k]?(o[k].desc||o[k]):'';};
      t('star-d',g(TT.kyusei,h.star));t('star-y',(TT.kyusei&&TT.kyusei[h.star]&&TT.kyusei[h.star].y2027)||'');
      t('eto-d',g(TT.eto,BR[ci]));t('pillars-d','日干「'+pl.nikkan+'」：'+g(TT.nikkan,pl.nikkan));
      t('shuku-d',sk?g(TT.shuku,sk.name):'');t('kin-d','紋章：'+g(TT.seal,kk.sealNo)+' 音：'+g(TT.tone,kk.tone));
      t('lp-d',g(TT.lp,lp));t('animal-d',g(TT.animal,an.animal)+g(TT.acolor,an.color));
      var sic=root.querySelector('#fh-b27-sg-sign');if(sic&&sg){var box=sic.parentNode.querySelector('.fh-b27-ic');if(box)box.className='fh-b27-ic fh-b27-ic-'+sg.en+' fh-b27-resic';}
      link('day','/366uranai/'+mmdd+'/');t('day-t',m+'月'+d+'日生まれの誕生日占い（2027年版）');
      link('day-a','/366uranai/'+mmdd+'/',m+'月'+d+'日生まれのページで、生まれ年を選んで続きを見る →');
      out.hidden=false;return true;
    }
    function onChange(e){if(e&&(e.target===fy||e.target===fm))fillDays();if(last||(fy.value&&fm.value&&fd.value))render();}
    [fy,fm,fd].forEach(function(s){s.addEventListener('change',onChange);});
    var go=$('go');if(go)go.addEventListener('click',function(){if(render()){var c=root.querySelector('.fh-b27-sg-cardwrap');if(c&&c.scrollIntoView)c.scrollIntoView({behavior:'smooth',block:'start'});}else{var f=!fy.value?fy:!fm.value?fm:fd;f.focus();}});
    /* --- カードを画像で保存（誕生日カードと同じく canvas に描いて PNG にする） --- */
    var save=root.querySelector('[data-fh-action="save-sg"]');
    if(save)save.addEventListener('click',function(ev){
      ev.preventDefault();if(!last)return;
      var draw=function(){
        var c=document.createElement('canvas'),W=1080,H=1350;c.width=W;c.height=H;var x=c.getContext('2d');
        x.fillStyle='#1F2638';x.fillRect(0,0,W,H);
        x.fillStyle='#33405C';for(var gy=20;gy<H;gy+=44)for(var gx=20;gx<W;gx+=44){x.beginPath();x.arc(gx,gy,2.4,0,7);x.fill();}
        x.save();x.translate(W/2,H/2);x.rotate(-0.025);
        x.fillStyle='#F7F1E3';x.fillRect(-430,-520,860,1040);
        x.fillStyle='rgba(227,199,126,.85)';x.fillRect(-110,-548,220,56);
        x.fillStyle='#6B645B';x.font='600 30px "Klee One", cursive';x.fillText('生年月日まるごとカード',-370,-440);
        x.fillStyle='#2E2A26';x.font='800 112px "Shippori Mincho", serif';x.fillText(last.y+'/'+last.m+'/'+last.d,-370,-300);
        x.fillStyle='#6B645B';x.font='600 34px "Klee One", cursive';x.fillText(($('sub')||{}).textContent||'',-370,-220);
        var rows=root.querySelectorAll('.fh-b27-sg-card dl > div'),yy=-140;
        rows.forEach(function(r){x.fillStyle='#6B645B';x.font='30px "Zen Kaku Gothic New", sans-serif';x.fillText(r.querySelector('dt').textContent,-370,yy);
          x.fillStyle='#2E2A26';x.font='700 34px "Zen Kaku Gothic New", sans-serif';x.textAlign='right';x.fillText(r.querySelector('dd').textContent,370,yy);x.textAlign='left';
          x.strokeStyle='#CFC6B5';x.setLineDash([6,6]);x.beginPath();x.moveTo(-370,yy+20);x.lineTo(370,yy+20);x.stroke();x.setLineDash([]);yy+=56;});
        x.fillStyle='#6B645B';x.font='28px "Zen Kaku Gothic New", sans-serif';x.fillText('人生予報 ｜ uranai.epoch-compass.com',-370,470);
        x.restore();
        c.toBlob(function(b){var u=URL.createObjectURL(b),a=document.createElement('a');a.href=u;a.download='seinengappi-'+last.y+pad(last.m)+pad(last.d)+'.png';document.body.appendChild(a);a.click();a.remove();setTimeout(function(){URL.revokeObjectURL(u)},4000);},'image/png');
      };
      if(document.fonts&&document.fonts.ready)document.fonts.ready.then(draw);else draw();
    });
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bootSeinen);else bootSeinen();
})(typeof window!=='undefined'?window:globalThis);
