/* 人生予報 誕生日相性占い（/compatibility/）の JS（fh-b27-compat）
 * 生成元: work/scripts/templates/fh-b27-compat.js（work/scripts/build_compatibility.py が366日の表を埋めて work/out/assets/ に出力）
 * 先に fh-b27-setsuiri.js・fh-b27-kyureki.js・fh-b27.js を読み込むこと（本命星は FHB27Calc.honmei を使う）。
 * <div class="fh-b27" data-fh-page="compatibility"> があるページでだけ表示の処理が動く。
 * 相性の計算は 366日の誕生日ページと同じ（work/scripts/build_compat.py の scores() をそのまま移したもの。
 * テスト: work/scripts/test_compatibility.py）。生年月日は送信・保存しない。
 *
 * 5段階の目安（決め方。ページ下の「この診断について」にも同じことを書いている）
 *   5 ◎ とても息が合う … 良い相性の点 1.0 以上
 *   4 ○ 息が合う       … 良い相性の点 0 より大きく 1.0 未満（または誕生日ページの「相性の良い誕生日」に入っている組）
 *   3 ◇ ほどよい距離   … 角度の関係なし
 *   2 △ 刺激がある     … ぶつかりやすさの点 0 より大きく 0.9 未満（または「気をつけたい誕生日」に入っている組）
 *   1 ▽ 刺激が強め     … ぶつかりやすさの点 0.9 以上
 *   （良い相性の点は最高で約1.7、ぶつかりやすさの点は最高で約1.5。366日×366日の組では、良い点1.0以上は良い組のおよそ上位2割）
 */
(function(G){
  'use strict';
  /*@CPDATA@*/
  /* CP.d[i] = [太陽の位置×1000, 誕生日の数, 星座の番号, エレメントの番号, 良い5日の番号, 気をつけたい3日の番号]（i は 1/1=0 … 2/29=59 … 12/31=365）
     CP.ky = 九星どうしの相性（本人＼相手、9行×9文字。knowledge/04_九星気学.md 3-3） */
  var SIGN12=['牡羊座','牡牛座','双子座','蟹座','獅子座','乙女座','天秤座','蠍座','射手座','山羊座','水瓶座','魚座'];
  var ELEM=['火','地','風','水'];
  var ML=[31,29,31,30,31,30,31,31,30,31,30,31];
  var KEYS=[],IDX={};
  (function(){for(var m=1;m<=12;m++)for(var d=1;d<=ML[m-1];d++){IDX[m*100+d]=KEYS.length;KEYS.push([m,d]);}})();
  /* 誕生日の数のグループ（11は2、22は4として） */
  var GRP={1:'行動',5:'行動',7:'行動',2:'堅実',4:'堅実',8:'堅実',3:'表現',6:'表現',9:'表現'};
  var GORDER=['行動','堅実','表現'];
  function red(n){return n===11?2:n===22?4:n;}
  function day(i){var r=CP.d[i];return {i:i,m:KEYS[i][0],d:KEYS[i][1],lon:r[0]/1000,num:r[1],sign:r[2],el:r[3],good:r[4],bad:r[5]};}
  function idx(m,d){var v=IDX[m*100+d];return v==null?-1:v;}
  /* 太陽の位置どうしの角度（短いほうの弧） */
  function ang(a,b){return Math.abs((((a-b+180)%360)+360)%360-180);}
  var GOOD_ASP=[[120,8,1.0],[60,6,.7],[0,8,.45]],BAD_ASP=[[90,8,1.0],[180,8,.75]];
  /* build_compat.scores(A,B,wide) と同じ。返り値 {good,gAsp,bad,bAsp,d} */
  function scores(A,B,wide){
    wide=wide||0;
    var d=ang(A.lon,B.lon),na=red(A.num),nb=red(B.num),ga=GRP[na],gb=GRP[nb],good=0,bad=0,gAsp=null,bAsp=null,i,a,orb;
    for(i=0;i<GOOD_ASP.length;i++){a=GOOD_ASP[i][0];orb=GOOD_ASP[i][1]+wide;if(Math.abs(d-a)<=orb){good=GOOD_ASP[i][2]*(1-Math.abs(d-a)/orb)+.1;gAsp=a;}}
    for(i=0;i<BAD_ASP.length;i++){a=BAD_ASP[i][0];orb=BAD_ASP[i][1]+wide;if(Math.abs(d-a)<=orb){bad=BAD_ASP[i][2]*(1-Math.abs(d-a)/orb)+.1;bAsp=a;}}
    if(gAsp!==null){good+=ga===gb?.45:0;good+=na===nb?.15:0;}
    if(bAsp!==null){var ab=(ga==='行動'&&gb==='堅実')||(ga==='堅実'&&gb==='行動');bad+=ab?.4:ga!==gb?.15:0;}
    return {good:good,gAsp:gAsp,bad:bad,bAsp:bAsp,d:d};
  }
  /* 誕生日ページの相性リストに入っているか（対称なので片方を見ればよいが、念のため両方） */
  function listed(A,B){
    if(A.good.indexOf(B.i)>=0||B.good.indexOf(A.i)>=0)return 'good';
    if(A.bad.indexOf(B.i)>=0||B.bad.indexOf(A.i)>=0)return 'bad';
    return null;
  }
  var TYPE_OF={120:'h',60:'k',0:'n',90:'s',180:'m'};
  /* 2人の関係：型（h 調和／k 協力／n 似た者どうし／s 刺激し合う／m 向かい合う／o おだやか）と5段階 */
  function relation(ia,ib){
    var A=day(ia),B=day(ib),s=scores(A,B,0),L=listed(A,B),asp=s.gAsp!==null?s.gAsp:s.bAsp,wide=0;
    if(asp===null&&L){/* リストは幅を広げて選んだ組もある（build_compat.py の widen）。そのときは広げた幅で型を出す */
      for(var w=4;w<=12;w+=4){var t=scores(A,B,w),x=L==='good'?t.gAsp:t.bAsp;if(x!==null){asp=x;wide=w;break;}}
    }
    var type=asp===null?'o':TYPE_OF[asp];
    var level=s.good>=1.0?5:(s.good>0||L==='good')?4:s.bad>=0.9?1:(s.bad>0||L==='bad')?2:3;
    return {A:A,B:B,s:s,listed:L,type:type,asp:asp,wide:wide,level:level};
  }

  /* ================= 文の材料（度数の数字は出さない） ================= */
  var REL={
    h:{name:'自然に息が合う「調和」のふたり',
      s:['{SA}のあなたと{SB}のお相手は、考え方の土台が自然にそろう組み合わせです。仕事の打ち合わせでも、説明を半分しないうちに「それでいこう」と話がまとまっていきます。',
         '2人でいると、無理に話題を探さなくても沈黙が気まずくならない間柄。恋人なら、休日の予定をすり合わせる手間がほとんどかからないでしょう。',
         'あなたが言いかけたことを、お相手が先に形にしてくれる。そんな場面が何度も起こる、追い風の吹きやすい2人です。',
         '初対面でも「前から知っていたような」気安さを感じやすい{SA}と{SB}。友人どうしなら、何年か会わなくても、会えばすぐ元の空気に戻れます。'],
      t:['居心地がよいぶん「言わなくても伝わる」と思いこみがち。感謝だけは言葉にして渡しましょう。',
         '順調なときほど、2人で新しいことに挑むのがおすすめ。相性の良さがいちばん生きる使い方です。',
         '判断が似やすい2人なので、大事な決めごとの前には第三者の意見も一度聞いておくと安心。']},
    k:{name:'声をかけ合って伸びる「協力」のふたり',
      s:['{SA}のあなたと{SB}のお相手は、ほどよい違いが刺激になる組み合わせ。職場なら、片方が出したアイデアをもう片方が実行に移す流れが自然にできます。',
         '最初から何でも分かり合える仲というより、声をかけるたびに距離が縮まっていく2人です。友人なら、誘い合うほど楽しい予定が増えていきます。',
         'あなたが困ったとき、お相手は「ちょっと手伝おうか」と軽く手を貸してくれる存在。恋愛でも、気負わない優しさが長続きの鍵になりそうです。',
         '得意なことが少しずつずれている{SA}と{SB}は、2人で動くと役割分担がうまくはまります。旅行の準備や引っ越しなど、手を分けられる場面で力を発揮する間柄。'],
      t:['自分から一声かけるほど育つ相性です。待つより先に誘ってみて。',
         'お互いの得意なことを言葉にして伝え合っておくと、頼り合いがもっとスムーズになります。',
         'ときどき役割を入れ替えてみると、相手の苦労と工夫が見えてきます。']},
    n:{name:'同じ景色を見る「似た者どうし」',
      s:['生まれた季節が近いあなたとお相手は、物事の感じ方がよく似た者どうし。同じ映画の同じ場面で笑い、同じところで胸を打たれるような2人です。',
         '{SA}のあなたと{SB}のお相手は、ペースや好みが重なりやすい組み合わせ。仕事では、説明なしで同じ方向に走り出せる頼もしい相棒になります。',
         '似ているからこそ、言葉にしない気持ちまで分かってしまう間柄。友人なら、一緒にいるだけで気持ちが落ち着く存在でしょう。',
         'お互いの長所も弱点も、鏡を見るように分かる2人。恋愛では、相手の喜びを自分のことのように感じられる関係になれます。'],
      t:['得意なことが重なるぶん、苦手なことも重なりがち。苦手な作業は、ほかの人の手も借りましょう。',
         '似た者どうしは張り合いやすい一面も。勝ち負けのない趣味を一緒に持つと穏やかです。',
         'どちらかが落ちこむと、もう一方も引っぱられやすい相性。元気なほうが支える役、と順番を意識して。']},
    s:{name:'刺激し合って育つふたり',
      s:['{SA}のあなたと{SB}のお相手は、物事を進める順番が食い違いやすい組み合わせ。仕事では意見がぶつかることもありますが、そのぶん結論はよく練られたものになります。',
         'あなたの「今すぐ」と、お相手の「もう少し待って」が交差しやすい2人です。恋愛では、ちょっとした行き違いをきっかけに本音を話せる仲へ育っていきます。',
         'ぶつかることがあっても、相手から学ぶことがいちばん多いのがこの組み合わせ。友人なら、自分ひとりでは選ばない世界へ連れ出してくれる存在です。',
         '一緒にいると退屈しない反面、疲れているときは小さなことで火花が散りがちな{SA}と{SB}。家族やルームメイトなら、暮らしのリズムを先に決めておくと穏やかに過ごせるはず。'],
      t:['意見が割れたら、まず相手の案を最後まで聞いてから自分の案を出すと、話がこじれにくくなります。',
         '急ぎの用事ほど、役割と期限を先に決めておくのがコツ。気持ちのぶつかり合いを減らせます。',
         '言い合いのあとは、少し時間をおいて「ありがとう」を一言。仲直りが早いほど絆は強くなります。']},
    m:{name:'向かい合って補い合うふたり',
      s:['{SA}のあなたと{SB}のお相手は、ちょうど反対側から同じものを見ている組み合わせ。自分にないものを持つ相手に、強く惹かれやすい間柄です。',
         'あなたが外へ向かうとき、お相手は内を固める。視点が逆になりやすい2人なので、仕事では片方が見落とした点をもう片方が拾ってくれます。',
         '最初は「どうしてそう考えるの」と驚くことが多いかもしれません。恋愛では、その驚きがそのまま魅力に変わっていく、引き合う力の強い組み合わせ。',
         '向かい合う位置にいる{SA}と{SB}は、お互いを映す鏡のような存在。友人どうしなら、相手の一言で自分の思いこみに気づく場面が何度もありそうです。'],
      t:['正反対の意見が出たら、どちらが正しいかより「両方を合わせるとどうなるか」を考えてみましょう。',
         '引き合う力が強いぶん、相手を自分に合わせたくなりがち。違いは違いのまま楽しむ余裕を。',
         '近づきすぎると疲れやすい相性です。ひとりの時間をお互いに大切にすると、長く続きます。']},
    o:{name:'ほどよい距離の「おだやか」なふたり',
      s:['{SA}のあなたと{SB}のお相手は、星の上では強く引き合うこともぶつかることも少ない組み合わせ。だからこそ2人の関係は、一緒に過ごした時間のぶんだけ形になっていきます。',
         '特別な追い風も向かい風もない、自由度の高い2人です。仕事では決まった型にはまらず、その都度ちょうどよい役割分担を選べます。',
         'お互いに干渉しすぎない、風通しのよい間柄。友人なら、会う回数が少なくても気持ちが離れにくい関係です。',
         '一目で惹かれ合うより、少しずつ相手の良さを見つけていく{SA}と{SB}。恋愛では、話した回数がそのまま信頼の厚みになります。'],
      t:['決まった型がない相性なので、毎月の食事など2人だけの小さな習慣を作ると関係が育ちます。',
         '相手の好きなことに一度付き合ってみると、思いがけない共通点が見つかるかもしれません。',
         '距離をとりやすい2人です。連絡が途切れたら、気づいたほうから気軽に声をかけて。']}
  };
  /* 誕生日の数のグループの組み合わせ（{X}{Y}＝あなた／お相手。X が GORDER で先のグループの人）
     g＝関係が調和・協力・似た者・おだやかのとき／t＝刺激し合う・向かい合うとき */
  var NUMTXT={
    '行動行動':{g:['2人とも誕生日の数が行動派で、思い立ったらすぐ動くところがそっくり。旅行の計画も、気づけば出発日まで決まっています。',
                  '行動派どうしの2人は、スタートの速さが自慢。新しい仕事や引っ越しなど、勢いのいる場面で頼りになるコンビです。',
                  '誕生日の数はどちらも行動派。休日に「どこか行こう」と言い出すのがどちらでも、もう片方は迷わずついていくでしょう。'],
               t:['誕生日の数はどちらも行動派なので、2人とも先頭に立ちたがる場面がありそう。主導権の取り合いが、ちょっとした言い合いの種になります。',
                  '行動派どうしで、決めるのも動くのも速い2人。そのぶん相手の確認を待たずに進めてしまい、すれ違うことも。',
                  'どちらも自分で道を切り開きたい行動派。同じ目標を向いているときは心強いのに、行き先が違うと譲らない者どうしになりがちです。'],
               tip:['先頭に立つ役は、場面ごとに交代制にすると不満がたまりません。','動き出す前に、ゴールだけは2人で確かめておきましょう。']},
    '堅実堅実':{g:['2人とも誕生日の数が堅実派で、約束や時間をきちんと守る感覚が似ています。一緒に貯金や計画を立てると、着実に形になる組み合わせ。',
                  '堅実派どうしの2人は、派手さより安心を大切にするところが共通点。職場では、ミスの少ない仕事ぶりで周りから信頼されるコンビです。',
                  '誕生日の数はどちらも堅実派。家具や旅先の宿も、2人で比べて納得してから決めるので後悔が少ないでしょう。'],
               t:['誕生日の数はどちらも堅実派なので、2人とも自分のやり方を崩したくないタイプ。小さなこだわりの違いが、なかなか譲れない場面を生みます。',
                  '堅実派どうしで慎重さは同じでも、何を先に大事にするかの順番が違いがち。話し合いが長引く原因はたいていそこにあります。',
                  'どちらも足元を固めたい堅実派。意見が割れると、どちらも引かないまま時間だけが過ぎてしまうことがありそうです。'],
               tip:['ときにはどちらかが思い切って決めてしまうと、2人の世界が広がります。','計画どおりにいかない日を楽しむ余白を、予定に入れておいて。']},
    '表現表現':{g:['2人とも誕生日の数が表現派で、気持ちを言葉や表情にするのが上手。話していると、時間を忘れるほど会話がはずみます。',
                  '表現派どうしの2人は、楽しいことを見つける名人。友人どうしなら、2人のまわりに自然と人が集まってきます。',
                  '誕生日の数はどちらも表現派。贈り物やサプライズを考えるのが好きなところが似ていて、記念日が楽しみになる組み合わせです。'],
               t:['誕生日の数はどちらも表現派なので、感じたことをすぐ口に出す2人。言葉が強くなった日は、思った以上に相手に響いてしまいます。',
                  '表現派どうしで、どちらも「わかってほしい」気持ちが強め。聞き役がいなくなると、話がかみ合わないまま終わることがあります。',
                  'どちらも気持ちを表に出す表現派。気分が合う日は最高に楽しく、合わない日はささいな一言で空気が変わりやすい間柄です。'],
               tip:['話すのと同じくらい、聞く役も交代で引き受けると会話がもっと楽しくなります。','気分が乗らない日は「今日は静かにしたい」と先に伝えておくと、すれ違いを防げます。']},
    '行動堅実':{g:['誕生日の数では、{X}が行動派、{Y}が堅実派。{X}が先に一歩を踏み出し、{Y}が後ろで足場を整える、理想的な二人三脚になれます。',
                  '{X}の行動派の勢いと、{Y}の堅実派の慎重さがうまくかみ合う組み合わせ。仕事なら、企画を出す人と仕上げる人として名コンビに。',
                  '行動派の{X}が「やってみよう」と言い、堅実派の{Y}が「それならこう準備しよう」と応える。2人の会話には、自然と前へ進む流れがあります。'],
               t:['誕生日の数では、{X}が行動派、{Y}が堅実派。{X}の「早く決めたい」と{Y}の「よく確かめたい」がぶつかりやすく、歩く速さの違いを感じる場面が多そうです。',
                  '行動派の{X}には{Y}が慎重すぎるように、堅実派の{Y}には{X}が急ぎすぎるように見えがち。待ち合わせ一つでも、感覚の違いが出やすい2人です。',
                  '{X}は行動派、{Y}は堅実派で、物事を進める速さが違う組み合わせ。仕事では、スケジュールの立て方で意見が分かれることがあります。'],
               tip:['{X}は決める前に一言相談を、{Y}は「いつまでに決めるか」を先に伝えると、速さの違いが気にならなくなります。','{X}が動く役、{Y}が確かめる役と、はじめから分担を決めてしまうのがおすすめ。']},
    '行動表現':{g:['誕生日の数では、{X}が行動派、{Y}が表現派。{X}が決めた行き先を、{Y}が楽しい思い出に変えてくれる、にぎやかな組み合わせです。',
                  '行動派の{X}が動き、表現派の{Y}がその良さを周りに伝える。仕事でも遊びでも、2人がそろうと話が広がっていきます。',
                  '{X}の行動力と{Y}の表現力は、お互いにないものを補い合う関係。友人なら、イベントの幹事を一緒に引き受けるとうまくいきそう。'],
               t:['誕生日の数では、{X}が行動派、{Y}が表現派。{X}は結論を急ぎ、{Y}は気持ちを話したいので、会話の目的がずれることがあります。',
                  '行動派の{X}が先へ進もうとするとき、表現派の{Y}は「その前に聞いて」と感じがち。気持ちの置き去りが、すれ違いの始まりになります。',
                  '{X}は行動派、{Y}は表現派。{X}の短い返事が、{Y}には冷たく聞こえてしまうことがあるかもしれません。'],
               tip:['{X}は結論の前に{Y}の気持ちを一つ聞いてみて。{Y}は話の最後に「どうしたいか」を添えると伝わりやすくなります。','2人で動くときは、{X}が段取り、{Y}が盛り上げ役と分けると息がそろいます。']},
    '堅実表現':{g:['誕生日の数では、{X}が堅実派、{Y}が表現派。{Y}の思いつきを、{X}が実現できる形に整えていく補い合いの組み合わせです。',
                  '堅実派の{X}の落ち着きと、表現派の{Y}の明るさがちょうどよく混ざる2人。家族なら、安心とにぎやかさが両方そろう関係です。',
                  '{Y}が表現派らしく場を和ませ、{X}が堅実派らしく約束を守る。職場では、雰囲気と信頼を同時につくれるペアになります。'],
               t:['誕生日の数では、{X}が堅実派、{Y}が表現派。{X}には{Y}の気分の変わりやすさが、{Y}には{X}の慎重さが、ときどきもどかしく映ります。',
                  '堅実派の{X}は筋道を、表現派の{Y}は気持ちを大事にするので、話し合いの着地点がずれやすい2人です。',
                  '{X}は堅実派、{Y}は表現派。お金の使い方や休日の過ごし方で「そこにこだわるの」と驚き合う場面がありそう。'],
               tip:['{X}は{Y}の思いつきにまず「いいね」を返して。{Y}は大事な約束だけはメモに残すと、信頼がぐっと増します。','{Y}のアイデアを{X}が予定表に落とす、という流れを2人の決まりにすると心強いでしょう。']}
  };
  /* 星座のエレメントの組み合わせ（{X}＝ELEM の順で先のエレメントの人） */
  var ELTXT={
    '火火':['どちらも火の星座で、熱くなるポイントが同じ。応援しているチームや好きな歌手の話で、一緒に盛り上がれる2人です。','火の星座どうしは、情熱の温度がそろう組み合わせ。一緒に挑戦すると、互いの火がもっと大きくなります。'],
    '地地':['どちらも地の星座で、お金や時間の感覚が近い2人。買い物で「高い」「安い」と感じる線がよく似ています。','地の星座どうしは、現実的な判断がそろう組み合わせ。暮らしの段取りを任せ合える安心感があります。'],
    '風風':['どちらも風の星座で、話題があちこちへ飛んでも平気な2人。長電話や長話になりやすい組み合わせです。','風の星座どうしは、軽やかさが共通点。新しい情報を教え合うだけで、毎日が少し楽しくなります。'],
    '水水':['どちらも水の星座で、言葉にしない気持ちを察し合える2人。疲れた日の「おつかれさま」が、誰よりも心にしみる相手です。','水の星座どうしは、共感の深さがそろう組み合わせ。映画や音楽の感想を話し始めると、時間を忘れそうです。'],
    '火地':['星座では、{X}が火、{Y}が地。{X}の熱意に、{Y}が現実的な段取りで形を与えます。','火の星座の{X}は「楽しそう」で動き、地の星座の{Y}は「続けられるか」で動く。動機の違いを知っておくと、ぐっと付き合いやすくなります。'],
    '火風':['星座では、{X}が火、{Y}が風。風が火を大きくするように、{Y}のひと言が{X}のやる気に火をつけます。','火の星座の{X}と風の星座の{Y}は、ノリと勢いが合う組み合わせ。思いつきの小旅行も楽しめる2人です。'],
    '火水':['星座では、{X}が火、{Y}が水。まっすぐな{X}と、気持ちのひだを大切にする{Y}は、温度差に気づくことから始まる関係です。','火の星座の{X}が引っぱり、水の星座の{Y}が心配りで包む。違いを分かっていれば、補い合える組み合わせです。'],
    '地風':['星座では、{X}が地、{Y}が風。じっくり型の{X}と身軽な{Y}は、予定の立て方がまるで違うかもしれません。','地の星座の{X}が足場を作り、風の星座の{Y}が外から新しい風を運ぶ。暮らしの中に安定と変化を両方持ちこめます。'],
    '地水':['星座では、{X}が地、{Y}が水。大地が水を受けとめるように、{X}が{Y}の気持ちをしっかり支えます。','地の星座の{X}と水の星座の{Y}は、互いを育て合う組み合わせ。家族や長い仕事仲間として、時間とともに味が出る2人です。'],
    '風水':['星座では、{X}が風、{Y}が水。理屈で考える{X}と気持ちで感じる{Y}は、同じ出来事への受け止め方が違いがち。','風の星座の{X}が話題を運び、水の星座の{Y}が気持ちをくみ取る。会話の役割が自然に分かれる2人です。']
  };
  var LEVEL={5:['◎','とても息が合う'],4:['○','息が合う'],3:['◇','ほどよい距離'],2:['△','刺激がある'],1:['▽','刺激が強め']};
  /* 九星どうしの相性の記号の意味（knowledge/04_九星気学.md 3-3） */
  var KYMARK={'◎':'相手から助けてもらいやすい（最良）','○':'自分が相手を支える（吉）','◇':'似た者どうし（まずまず）','△':'自分が相手を押さえる側（少し注意）','×':'相手に押さえられやすい側（注意）'};

  /* 2つの日付から決まる番号（同じ組なら A/B を入れ替えても同じ。文の選び方に使う） */
  function hsh(s){var h=7;for(var i=0;i<s.length;i++)h=(h*131+s.charCodeAt(i))%2147483647;return h;}
  function pick(arr,key,salt){return arr[hsh(key+'|'+salt)%arr.length];}
  function fill(t,v){for(var k in v){if(Object.prototype.hasOwnProperty.call(v,k))t=t.split('{'+k+'}').join(v[k]);}return t;}

  /* 文の組み立て。返り値 {name, lead, num, elem, tips[], list} */
  function texts(r){
    var A=r.A,B=r.B,key=Math.min(A.i,B.i)+'-'+Math.max(A.i,B.i),R=REL[r.type],pol=(r.type==='s'||r.type==='m')?'t':'g';
    var v={SA:SIGN12[A.sign],SB:SIGN12[B.sign]};
    var ga=GRP[red(A.num)],gb=GRP[red(B.num)],aFirst=GORDER.indexOf(ga)<=GORDER.indexOf(gb);
    var gk=aFirst?ga+gb:gb+ga,vn={X:aFirst?'あなた':'お相手',Y:aFirst?'お相手':'あなた'};
    var eFirst=A.el<=B.el,ek=eFirst?ELEM[A.el]+ELEM[B.el]:ELEM[B.el]+ELEM[A.el],ve={X:eFirst?'あなた':'お相手',Y:eFirst?'お相手':'あなた'};
    var N=NUMTXT[gk];
    var lead=fill(pick(R.s,key,'s'),v);
    if(A.i===B.i)lead='2人は同じ誕生日です。'+lead;
    var tips=[pick(R.t,key,'t'),fill(pick(N.tip,key,'nt'),vn)];
    var list;
    if(r.listed==='good')list='2人の誕生日ページの「相性の良い誕生日」（各5日）に、お互いの誕生日が入っています。366日の中から選んだ、特に息の合う組み合わせです。';
    else if(r.listed==='bad')list='2人の誕生日ページの「気をつけたい誕生日」（各3日）に、お互いの誕生日が入っています。ぶつかりやすいぶん、学び合えることも多い組み合わせです。';
    else list='2人の誕生日ページの相性リスト（良い5日・気をつけたい3日）には入っていない組み合わせです。リストは366日の中から点の特に高い組を選んだもので、入っていなくても相性が悪いという意味ではありません。';
    return {name:R.name,lead:lead,num:fill(pick(N[pol],key,'n'),vn),elem:fill(pick(ELTXT[ek],key,'e'),ve),tips:tips,list:list};
  }
  /* 九星どうしの相性（本人 a から見た相手 b）。a,b は 1〜9 */
  function kyusei(a,b){var m=CP.ky[a-1].charAt(b-1);return {mark:m,text:KYMARK[m]};}

  G.FHB27Compat={idx:idx,day:day,scores:scores,relation:relation,texts:texts,kyusei:kyusei,LEVEL:LEVEL,REL:REL,NUMTXT:NUMTXT,ELTXT:ELTXT,KEYS:KEYS};

  /* ================= ページの表示（ブラウザだけ） ================= */
  if(typeof document==='undefined')return;
  function boot(){
    var root=document.querySelector('.fh-b27[data-fh-page="compatibility"]');if(!root)return;
    var C=G.FHB27Calc||null;
    var $=function(id){return document.getElementById('fh-b27-cp-'+id);};
    var R=C&&C.yearRange?C.yearRange():{min:1930,max:2030};
    var isLeap=function(y){return (y%4===0&&y%100!==0)||y%400===0;};
    var wareki=C&&C.wareki?C.wareki:function(){return '';};
    function wlabel(y){return y===2019?'平成31年／令和元年':wareki(y);}
    function opt(sel,val,txt){var o=document.createElement('option');o.value=val;o.textContent=txt;sel.appendChild(o);}
    function fillMonth(sel){sel.innerHTML='';opt(sel,'','月を選ぶ');for(var m=1;m<=12;m++)opt(sel,m,m+'月');}
    function fillDay(sel,m){var cur=sel.value;sel.innerHTML='';opt(sel,'','日を選ぶ');var n=m?ML[m-1]:31;for(var d=1;d<=n;d++)opt(sel,d,d+'日');if(cur&&Number(cur)<=n)sel.value=cur;}
    function fillYear(sel,leapOnly){var cur=sel.value;sel.innerHTML='';opt(sel,'','わからない・選ばない');
      for(var y=R.max;y>=R.min;y--){if(leapOnly&&!isLeap(y))continue;opt(sel,y,y+'年（'+wlabel(y)+'）');}
      if(cur&&(!leapOnly||isLeap(Number(cur))))sel.value=cur;}
    var P={};
    ['a','b'].forEach(function(k){
      var m=$(k+'m'),d=$(k+'d'),y=$(k+'y');P[k]={m:m,d:d,y:y};
      fillMonth(m);fillDay(d,0);fillYear(y,false);
      m.addEventListener('change',function(){fillDay(d,Number(m.value));fillYear(y,Number(m.value)===2&&Number(d.value)===29);});
      d.addEventListener('change',function(){fillYear(y,Number(m.value)===2&&Number(d.value)===29);});
    });
    function val(k){var p=P[k];return {m:Number(p.m.value)||0,d:Number(p.d.value)||0,y:Number(p.y.value)||0};}
    function md(x){return x.m+'月'+x.d+'日';}
    function pad(n){return (n<10?'0':'')+n;}
    function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
    var msg=$('msg');
    function render(){
      var a=val('a'),b=val('b');
      var miss=!a.m?P.a.m:!a.d?P.a.d:!b.m?P.b.m:!b.d?P.b.d:null;
      if(miss){msg.textContent=(miss===P.a.m||miss===P.a.d?'あなた':'お相手')+'の誕生日の月と日を選んでください。';msg.hidden=false;miss.focus();return false;}
      msg.hidden=true;
      var ia=idx(a.m,a.d),ib=idx(b.m,b.d),r=relation(ia,ib),t=texts(r),L=LEVEL[r.level];
      $('pair').textContent=md(a)+'生まれのあなた × '+md(b)+'生まれのお相手';
      $('type').textContent=t.name;
      $('mk').textContent=L[0];$('lv').textContent=L[1];
      var meter=$('meter');meter.setAttribute('data-lv',r.level);meter.setAttribute('aria-label','息の合いやすさ 5段階の'+r.level+'：'+L[1]);meter.setAttribute('role','img');
      var bars=$('bar').children;for(var i=0;i<bars.length;i++)bars[i].className=i<r.level?'fh-b27-cp-on':'';
      $('lead').textContent=t.lead;$('num').textContent=t.num;$('elem').textContent=t.elem;$('list').textContent=t.list;
      var ul=$('tips');ul.innerHTML='';t.tips.forEach(function(x){var li=document.createElement('li');li.textContent=x;ul.appendChild(li);});
      /* 2人のプロフィール */
      function prof(who,x,D){var g=GRP[red(D.num)];
        return '<div class="fh-b27-cp-pf"><small>'+who+'</small><b>'+md(x)+'生まれ'+(x.y?'<em>'+x.y+'年（'+esc(wlabel(x.y))+'）</em>':'')+'</b>'+
          '<span>'+SIGN12[D.sign]+'（'+ELEM[D.el]+'の星座）／誕生日の数'+D.num+'（'+g+'派）</span></div>';}
      $('who').innerHTML=prof('あなた',a,r.A)+prof('お相手',b,r.B);
      /* 九星（2人とも生まれ年があるときだけ） */
      var ky=$('kyusei');
      if(a.y&&b.y&&C&&C.honmei){
        var ha=C.honmei(a.y,a.m,a.d),hb=C.honmei(b.y,b.m,b.d),ka=kyusei(ha.star,hb.star),kb=kyusei(hb.star,ha.star),S=C.STAR;
        var pv=function(h){return h.prev?'<small>（立春より前の生まれなので前の年の星）</small>':'';};
        ky.className='fh-b27-cp-kyusei fh-b27-cp-ky-on';
        ky.innerHTML='<h3><i class="fh-b27-ic fh-b27-ic-calendar-next" aria-hidden="true"></i>九星気学で見る2人</h3>'+
          '<p class="fh-b27-cp-stars"><span>あなた <b>'+S[ha.star]+'</b>'+pv(ha)+'</span><span>お相手 <b>'+S[hb.star]+'</b>'+pv(hb)+'</span></p>'+
          '<ul><li><span class="fh-b27-cp-km">'+ka.mark+'</span><span><b>あなたから見たお相手：</b>'+ka.text+'</span></li>'+
          '<li><span class="fh-b27-cp-km">'+kb.mark+'</span><span><b>お相手から見たあなた：</b>'+kb.text+'</span></li></ul>'+
          '<p class="fh-b27-small">九星の五行（木・火・土・金・水）が生み合うか、抑え合うかで見る相性です。誕生日の相性とは別の見方なので、両方を重ねて楽しんでください。</p>';
      }else{
        ky.className='fh-b27-cp-kyusei';
        ky.innerHTML='<p class="fh-b27-small"><b>生まれた年は選ばなくても占えます。</b>'+(a.y||b.y?'もう1人の生まれた年も選ぶと':'2人とも生まれた年を選ぶと')+
          '、九星気学の本命星どうしの相性（助け合う関係か、似た者どうしかなど）もここに表示します。</p>';
      }
      /* 2人の誕生日ページへ */
      $('da').href='/366uranai/'+pad(a.m)+'-'+pad(a.d)+'/';$('dat').textContent=md(a)+'生まれの誕生日占い →';
      $('db').href='/366uranai/'+pad(b.m)+'-'+pad(b.d)+'/';$('dbt').textContent=md(b)+'生まれの誕生日占い →';
      document.getElementById('b27-cp-result').hidden=false;
      return true;
    }
    function show(){var o=document.getElementById('b27-cp-result');if(render()&&o.scrollIntoView)o.scrollIntoView({behavior:'smooth',block:'start'});}
    $('go').addEventListener('click',show);
    $('swap').addEventListener('click',function(){
      var a=val('a'),b=val('b');
      function set(k,x){var p=P[k];p.m.value=x.m||'';fillDay(p.d,x.m);p.d.value=x.d||'';fillYear(p.y,x.m===2&&x.d===29);p.y.value=x.y||'';}
      set('a',b);set('b',a);render();
    });
    $('again').addEventListener('click',function(){var f=document.getElementById('b27-cp-input');if(f&&f.scrollIntoView)f.scrollIntoView({behavior:'smooth',block:'start'});P.a.m.focus({preventScroll:true});});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
})(typeof window!=='undefined'?window:globalThis);
