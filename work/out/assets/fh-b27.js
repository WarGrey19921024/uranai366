/* 人生予報 2027年版 誕生日占い 共通JS（fh-b27）
 * 生成元: work/scripts/templates/fh-b27.js（work/scripts/build_html.py が GEN を埋めて work/out/assets/ に出力）
 * 先に fh-b27-setsuiri.js（節入り日時 1930〜2030年）と fh-b27-kyureki.js（旧暦の月の表）を読み込むこと。
 * 計算の規則は work/scripts/calc_*.py と同じ（テスト: work/scripts/test_js_calc.py）。
 * ページ側は <div class="fh-b27" data-m data-d data-base data-sekki> に月日とデータだけを持つ。
 */
(function(G){
  'use strict';
  var GEN={"center2027":9,"monthStar2027":[6,5,4,3,2,1,9,8,7,6,5,4],"yearMin":1930,"yearMax":2020,"kyuseiKw":{"1":"柔軟・内省・人とのつながり","2":"地道・支える・育てる","3":"発進・若さ・音","4":"調和・信用・ご縁","5":"中心・強さ・再生","6":"責任・向上・まっすぐ","7":"喜び・社交・楽しみ","8":"変化・継承・積み重ね","9":"明るさ・知性・美"},"nikkan":{"甲":"大樹（まっすぐ、向上心、リーダー）","乙":"草花・つる草（しなやか、協調、粘り強さ）","丙":"太陽（明るい、おおらか、目立つ）","丁":"灯火（ともしび）（温かい、繊細、内に秘めた情熱）","戊":"山（安定、包容力、頼りがい）","己":"田畑の土（育てる、まじめ、面倒見）","庚":"鉄・刃物（決断、正義感、改革）","辛":"宝石・装飾品（美意識、繊細、プライド）","壬":"海・大河（自由、スケールの大きさ、知恵）","癸":"雨・露（静か、思いやり、直感）"},"shukuKw":{"昴":"品のよさ・美意識・恵まれた運","畢":"粘り強さ・堅実・地に足","觜":"話術・知識・金銭感覚","参":"行動力・好奇心・刷新","井":"知性・分析・冷静さ","鬼":"純粋さ・直感・自由","柳":"情熱・一途・集中力","星":"独立心・努力・負けず嫌い","張":"華やかさ・自己表現・人気","翼":"向上心・理想・遠くへ","軫":"社交性・器用さ・移動","角":"遊び心・洗練・楽しさ","亢":"正義感・反骨・筋を通す","氐":"生命力・実利・押しの強さ","房":"恵まれた縁・財運・穏やかさ","心":"愛嬌・人心掌握・演出力","尾":"根性・忍耐・信念","箕":"豪快さ・開放的・親分肌","斗":"統率力・高い志・カリスマ","女":"勤勉・学び・堅実","虚":"繊細さ・多才・理想と現実","危":"社交・新しもの好き・自由","室":"行動力・大胆・エネルギー","壁":"支える力・誠実・口の堅さ","奎":"品格・誠実・精神性","婁":"気配り・調整力・器用さ","胃":"意欲・向上心・闘志"},"sealKw":{"1":"育む／誕生／存在","2":"伝える／霊（スピリット）／呼吸","3":"夢見る／豊かさ／直観","4":"目指す／開花／気づき","5":"生き残る／生命力／本能","6":"等しくする／死／機会","7":"知る／達成／癒し","8":"美しくする／優美／芸術","9":"浄化する／宇宙の水／流れ","10":"愛する／ハート／忠実","11":"遊ぶ／魔術／幻想","12":"影響を与える／自由意志／知恵","13":"探検する／空間／目覚め","14":"魅了する／時間を超えること／受容性","15":"創り出す／ヴィジョン／心","16":"問う／知性／恐れのなさ","17":"進化させる／舵取り（ナビゲーション）／共時性","18":"映す／果てしなさ／秩序","19":"触媒する／自己発生／エネルギー","20":"照らす／宇宙の火／生命"},"toneKw":{"1":"統一する／目的","2":"二極化する／挑戦","3":"活性化する／奉仕","4":"定義する／形","5":"力を与える／輝き","6":"組織する／平等","7":"調律する／ひらめき","8":"調和させる／完全性","9":"脈動させる／意図","10":"完成させる／顕現","11":"解き放つ／解放","12":"献身する／協力","13":"耐える／存在"},"lpKw":{"1":"始まり・自立・リーダー","2":"協力・調和・受け止める力","3":"表現・楽しさ・創造","4":"安定・土台・誠実","5":"自由・変化・冒険","6":"愛情・責任・調和","7":"探求・分析・ひとりの時間","8":"力・達成・豊かさ","9":"完成・思いやり・広い視野","11":"ひらめき・直感・感性（マスター）","22":"大きな形をつくる力（マスター）","33":"無条件の愛・奉仕（マスター）"}};

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
      if(bioGood(n))good.push(lab);if(bioCare(n))care.push(lab);}
    return {good:good,care:care};
  }
  var EL={1:'水',2:'土',3:'木',4:'木',5:'土',6:'金',7:'金',8:'土',9:'火'};
  var GENR={'木':'火','火':'土','土':'金','金':'水','水':'木'},CTL={'木':'土','土':'水','水':'火','火':'金','金':'木'};
  function kyuseiScore(me,ms){var a=EL[me],b=EL[ms];if(a===b)return 78;if(GENR[b]===a)return 88;if(GENR[a]===b)return 66;if(CTL[b]===a)return 55;return 72;}
  function wareki(y){if(y>=2019)return '令和'+(y===2019?'元':(y-2018))+'年';if(y>=1989)return y===1989?'昭和64年／平成元年':'平成'+(y-1988)+'年';return '昭和'+(y-1925)+'年';}

  var CALC={jdn:jdn,honmei:honmei,palace2027:palace2027,pillars:pillars,setsuDay:setsuDay,kyureki:kyureki,shuku:shuku,kin:kin,lifePath:lifePath,animal:animal,bioAt:bioAt,bioMark:bioMark,bioGood:bioGood,bioCare:bioCare,bioDays:bioDays,kyuseiScore:kyuseiScore,STAR:STAR};
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
      for(var m=1;m<=12;m++){var sum=0,n=daysIn(m);for(var d=1;d<=n;d++){var v=bioAt(jdn(2027,m,d)-b);sum+=(v[0]+v[1]+v[2])/3;}bv.push(Math.round(65+30*(sum/n)));}
      list.push({key:'bio',name:'バイオリズム',color:EXTRA_COLORS.bio,w:2,values:bv});
    }
    var vis=list.filter(function(s){return !state.hidden[s.key]});
    var tot=MONTHS.map(function(_,i){if(!vis.length)return null;return Math.round(vis.reduce(function(a,s){return a+s.values[i]},0)/vis.length)});
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
  /* --- バイオリズム（月ごと） --- */
  function drawBio(){
    var box=document.getElementById('fh-b27-bchart');if(!box)return;if(!state.year){box.innerHTML='';return;}
    var b=jdn(state.year,M,D),m=state.bioMonth,n=daysIn(m),p=[],e=[],it=[],labels=[],bands=[];
    for(var d=1;d<=n;d++){var k=jdn(2027,m,d)-b,v=bioAt(k);p.push(Math.round(v[0]*100));e.push(Math.round(v[1]*100));it.push(Math.round(v[2]*100));labels.push(m+'/'+d);
      if(bioGood(k))bands.push({i:d-1,color:'#E3C77E',op:.3});else if(bioCare(k))bands.push({i:d-1,color:'#8A8678',op:.25});}
    lineChart(box,{labels:labels,labelStep:5,series:[{name:'身体',color:'#d95926',values:p,w:2},{name:'感情',color:'#3987e5',values:e,w:2},{name:'知性',color:'#199e70',values:it,w:2}],min:-100,max:100,base:0,grid:[-100,-50,0,50,100],h:220,bands:bands,aria:'2027年'+m+'月のバイオリズム',fmt:function(v){return (v>0?'+':'')+v}});
    var W='日月火水木金土'.split(''),h='<table class="fh-b27-btab"><thead><tr><th>日付</th><th>曜日</th><th>身体</th><th>感情</th><th>知性</th><th>総合</th></tr></thead><tbody>';
    for(var dd=1;dd<=n;dd++){var vv=bioAt(jdn(2027,m,dd)-b),av=(vv[0]+vv[1]+vv[2])/3,cells=[vv[0],vv[1],vv[2],av].map(function(x){var q=bioMark(x);return '<td class="fh-b27-s'+q[1]+'">'+q[0]+'</td>'}).join('');
      h+='<tr><th>'+dd+'</th><td>'+W[new Date(2027,m-1,dd).getDay()]+'</td>'+cells+'</tr>';}
    document.getElementById('fh-b27-btable').innerHTML=h+'</tbody></table>';
    document.getElementById('fh-b27-btitle').textContent='2027年'+m+'月のバイオリズム（日ごとの表）';
    var mb=document.getElementById('fh-b27-mbtn');mb.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed',Number(x.value)===m?'true':'false')});
  }
  function txt(id,s){var e=document.getElementById(id);if(e)e.textContent=s;}
  function drawPanel(){
    var mine=document.getElementById('fh-b27-mine'),bw=document.getElementById('fh-b27-biowrap');
    if(!mine)return;
    if(!state.year){mine.hidden=true;if(bw)bw.hidden=true;return;}
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
    if(bio)bio.innerHTML='<b>好調日（金色の帯・'+bd.good.length+'日）</b>　'+(bd.good.join('、')||'—')+'<br><b>注意日（灰色の帯・'+bd.care.length+'日）</b>　'+(bd.care.join('、')||'—');
    drawBio();
  }
  function drawNotes(){
    root.querySelectorAll('[data-fh-yearnote]').forEach(function(e){
      e.innerHTML=state.year?('生まれ年：<b>'+state.year+'年（'+wareki(state.year)+'）</b>で表示中　<a href="#b27-yearbar">変更する</a>'):'生まれ年を選ぶと表示されます　<a href="#b27-yearbar">ページ上部で生まれ年を選ぶ →</a>';
    });
  }
  /* --- 年の選択（ページ上部の1か所） --- */
  var sels=root.querySelectorAll('[data-fh-year]');
  sels.forEach(function(sel){
    var o=document.createElement('option');o.value='';o.textContent='選ばない';sel.appendChild(o);
    for(var y=GEN.yearMax;y>=GEN.yearMin;y--){if(M===2&&D===29&&!isLeap(y))continue;o=document.createElement('option');o.value=y;o.textContent=y+'年（'+wareki(y)+'）';sel.appendChild(o);}
    sel.addEventListener('change',function(){state.year=sel.value?Number(sel.value):null;sels.forEach(function(s2){s2.value=sel.value});drawMain();drawPanel();drawNotes();});
  });
  var mb=document.getElementById('fh-b27-mbtn');
  if(mb)MONTHS.forEach(function(lb,i){var b=document.createElement('button');b.type='button';b.value=i+1;b.textContent=lb;b.className='fh-b27-mb';b.addEventListener('click',function(){state.bioMonth=i+1;drawBio();});mb.appendChild(b);});
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
})(typeof window!=='undefined'?window:globalThis);
