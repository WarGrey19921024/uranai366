/* 人生予報 2027年版 誕生日占い 共通JS（fh-b27）
 * 生成元: work/scripts/templates/fh-b27.js（work/scripts/build_html.py が GEN を埋めて work/out/assets/ に出力）
 * 先に fh-b27-setsuiri.js（節入り日時 1930〜2030年）と fh-b27-kyureki.js（旧暦の月の表）を読み込むこと。
 * 計算の規則は work/scripts/calc_*.py と同じ（テスト: work/scripts/test_js_calc.py）。
 * ページ側は <div class="fh-b27" data-m data-d data-base data-sekki> に月日とデータだけを持つ。
 */
(function(G){
  'use strict';
  var GEN={"center2027":9,"monthStar2027":[6,5,4,3,2,1,9,8,7,6,5,4],"yearMin":1930,"yearMax":2030,"kyuseiKw":{"1":"柔軟・内省・人とのつながり","2":"地道・支える・育てる","3":"発進・若さ・音","4":"調和・信用・ご縁","5":"中心・強さ・再生","6":"責任・向上・まっすぐ","7":"喜び・社交・楽しみ","8":"変化・継承・積み重ね","9":"明るさ・知性・美"},"nikkan":{"甲":"大樹（まっすぐ、向上心、リーダー）","乙":"草花・つる草（しなやか、協調、粘り強さ）","丙":"太陽（明るい、おおらか、目立つ）","丁":"灯火（ともしび）（温かい、繊細、内に秘めた情熱）","戊":"山（安定、包容力、頼りがい）","己":"田畑の土（育てる、まじめ、面倒見）","庚":"鉄・刃物（決断、正義感、改革）","辛":"宝石・装飾品（美意識、繊細、プライド）","壬":"海・大河（自由、スケールの大きさ、知恵）","癸":"雨・露（静か、思いやり、直感）"},"shukuKw":{"昴":"品のよさ・美意識・恵まれた運","畢":"粘り強さ・堅実・地に足","觜":"話術・知識・金銭感覚","参":"行動力・好奇心・刷新","井":"知性・分析・冷静さ","鬼":"純粋さ・直感・自由","柳":"情熱・一途・集中力","星":"独立心・努力・負けず嫌い","張":"華やかさ・自己表現・人気","翼":"向上心・理想・遠くへ","軫":"社交性・器用さ・移動","角":"遊び心・洗練・楽しさ","亢":"正義感・反骨・筋を通す","氐":"生命力・実利・押しの強さ","房":"恵まれた縁・財運・穏やかさ","心":"愛嬌・人心掌握・演出力","尾":"根性・忍耐・信念","箕":"豪快さ・開放的・親分肌","斗":"統率力・高い志・カリスマ","女":"勤勉・学び・堅実","虚":"繊細さ・多才・理想と現実","危":"社交・新しもの好き・自由","室":"行動力・大胆・エネルギー","壁":"支える力・誠実・口の堅さ","奎":"品格・誠実・精神性","婁":"気配り・調整力・器用さ","胃":"意欲・向上心・闘志"},"sealKw":{"1":"育む／誕生／存在","2":"伝える／霊（スピリット）／呼吸","3":"夢見る／豊かさ／直観","4":"目指す／開花／気づき","5":"生き残る／生命力／本能","6":"等しくする／死／機会","7":"知る／達成／癒し","8":"美しくする／優美／芸術","9":"浄化する／宇宙の水／流れ","10":"愛する／ハート／忠実","11":"遊ぶ／魔術／幻想","12":"影響を与える／自由意志／知恵","13":"探検する／空間／目覚め","14":"魅了する／時間を超えること／受容性","15":"創り出す／ヴィジョン／心","16":"問う／知性／恐れのなさ","17":"進化させる／舵取り（ナビゲーション）／共時性","18":"映す／果てしなさ／秩序","19":"触媒する／自己発生／エネルギー","20":"照らす／宇宙の火／生命"},"toneKw":{"1":"統一する／目的","2":"二極化する／挑戦","3":"活性化する／奉仕","4":"定義する／形","5":"力を与える／輝き","6":"組織する／平等","7":"調律する／ひらめき","8":"調和させる／完全性","9":"脈動させる／意図","10":"完成させる／顕現","11":"解き放つ／解放","12":"献身する／協力","13":"耐える／存在"},"lpKw":{"1":"始まり・自立・リーダー","2":"協力・調和・受け止める力","3":"表現・楽しさ・創造","4":"安定・土台・誠実","5":"自由・変化・冒険","6":"愛情・責任・調和","7":"探求・分析・ひとりの時間","8":"力・達成・豊かさ","9":"完成・思いやり・広い視野","11":"ひらめき・直感・感性（マスター）","22":"大きな形をつくる力（マスター）","33":"無条件の愛・奉仕（マスター）"},"pdKw":{"1":"何かを始める・決める日","2":"相手に合わせ、丁寧に話す日","3":"楽しむ・伝える日","4":"こつこつ進め、整える日","5":"寄り道・新しい体験の日","6":"人に手を貸す・感謝を伝える日","7":"調べる・休む・振り返る日","8":"交渉・決断・仕事を進める日","9":"区切りをつける・人のために動く日"},"typeTexts":{"kyusei":{"1":{"desc":"水のように相手に合わせられる、柔らかな人です。聞き上手で粘り強い一方、悩みを抱え込みがち。本音を話せる相手を一人持つと楽になります。","y2027":"北西に入り、責任ある役目や目上からの引き立てが増える年。主導権を握れても空回りしやすいので、抱え込まず分担を。"},"2":{"desc":"大地のように人を支え、こつこつ育てるのが得意です。まじめで面倒見がよい反面、慎重すぎて出遅れることも。早めの一歩を意識すると吉。","y2027":"西に入り、実りや楽しい誘いが増える年。九紫の追い風も受けやすい一方、出費はかさみがち。お金の出入りを記録すると安心です。"},"3":{"desc":"雷のように勢いよく動き出せる、明るいアイデアの人。行動の早さが魅力ですが、早とちりや言い過ぎには注意。ひと呼吸おくと伸びます。","y2027":"北東に入り、身の回りの切り替わりが起きやすい年。周りを照らす役回りも増えますが、大きな決断は急がず足元を固めて。"},"4":{"desc":"風のように人と人をつなぎ、信用を集める調和の人です。まとめ役に向く一方、迷って流されることも。自分の軸を一つ決めておきましょう。","y2027":"南に入り、注目を浴びて努力が表に出る年。評価が上がるぶん言葉選びが大切に。見直しと丁寧な説明を心がけると安心です。"},"5":{"desc":"九星の中心に立つ、器の大きな人。困難に強く、自然とリーダー役を任されます。強さが強引さに変わらないよう、人の話を聞く時間を大切に。","y2027":"北に入る、静かに力をためる充電の年。九紫の追い風はあるので焦らず、体を休めて学びや準備に時間を使うと次が開けます。"},"6":{"desc":"天のように高い志と正義感を持つ、責任感の強い人です。決断力がある反面、休むのが苦手。ときには肩の力を抜いて人に任せてみて。","y2027":"南西に入り、地道な努力が求められる年。周りの期待が重く感じる場面も、土台づくりと割り切れば後の実りにつながります。"},"7":{"desc":"湖のほとりの実りのように、人に喜びを運ぶ社交家。話し上手で愛嬌がありますが、楽な方へ流れやすい面も。出費の管理が運を守ります。","y2027":"東に入り、新しいことが動き出す勢いのある年。プレッシャーも感じやすいので、やることを絞って一つずつ形にしていきましょう。"},"8":{"desc":"山のようにどっしりと、積み重ねを力に変える人です。家族思いで貯める力にすぐれる一方、変化の時には迷いがち。変わり目こそ好機と考えて。","y2027":"南東に入り、信用やご縁が整いやすい年。九紫の追い風も受けて、遠方との縁や話し合いがまとまりやすくなります。"},"9":{"desc":"太陽のように明るく、ひらめきと美しさで人を引きつけます。先を見通す知性がある反面、熱しやすく冷めやすい面も。続ける仕組みが味方に。","y2027":"自分の星が真ん中に入る、注目の年。何かと目立つ反面、動きすぎると空回りしがち。新しく広げるより足場固めを優先して。"}},"eto":{"子":"物事の始まりを担う、機転のきく知恵者タイプです。小さな変化にもすぐ気づき、暮らしを豊かに広げていきます。慎重さと大胆さの使い分けがコツ。","丑":"忍耐強く、着実に一歩ずつ進む人。準備を怠らないので、時間をかけた仕事ほど実を結びます。ときにはペースを上げる遊び心も大切に。","寅":"春の始まりのような勢いと決断力の持ち主です。思い切りのよさで道を開きますが、勢い任せは禁物。動く前に行き先を一つ確かめましょう。","卯":"芽吹きの季節のように穏やかで、周りと調和しながら伸びていく人です。温和な人柄で慕われます。迷ったときは自分の気持ちを大事に。","辰":"大きな理想を描き、変化を力に変えるスケールの大きな人。周りを巻き込む力があります。夢を小さな目標に分けると、着実に近づけます。","巳":"内に情熱を秘め、気になることをとことん探る探究心の持ち主。何度でも立ち上がる再生の強さもあります。こだわりを手放す勇気も添えて。","午":"明るく活発で、いるだけで場を華やかにするタイプ。頂点を目指すエネルギーにあふれています。走り続けるだけでなく、休む日も予定に入れて。","未":"穏やかで協調性が高く、周りとの和を大切にする人です。実りに向けて準備を重ねる力も。遠慮しすぎず、ときには自分の希望を口にしてみて。","申":"器用で機転がきき、どんな場面でもうまく立ち回れる人。実りの季節の入口を表すとおり、成果をつかむのも上手です。一つを深める時間も大切に。","酉":"実りを整理し、美しく整えるのが得意な人です。細やかな気配りと美意識が光ります。完璧を求めすぎず、七分目で手放す軽さも持って。","戌":"誠実で、大切な人や約束をしっかり守るタイプ。物事を最後まで締めくくる責任感があります。心配しすぎず、仲間を信じて任せることも。","亥":"まっすぐに目標へ進み、力を蓄えて次に備える人です。ひたむきさが周りの信頼を集めます。ときどき立ち止まって周りを見渡すと安心。"},"nikkan":{"甲":"大きな木のようにまっすぐ伸び、目標へ一直線に進む人です。面倒見がよくまとめ役に。ときには風にまかせる柔らかさも忘れずに。","乙":"草花のようにしなやかで、環境に合わせて伸びていける人。協調性と粘り強さが光ります。好きなものを自分の軸にすると、さらに強くなれます。","丙":"太陽のように明るくおおらかで、場を照らすタイプです。行動が早く人を元気づけますが、熱しやすさも。ペース配分を覚えると長く輝けます。","丁":"灯火のように静かで温かく、周りを照らし続ける人です。内に強い情熱を秘めています。気をつかいすぎたら、信頼できる人のそばで休んで。","戊":"どっしりした山のように、人に安心感を与える頼もしい人。包容力があり大きな仕事を任されます。新しい風を入れる習慣が成長の鍵です。","己":"田畑の土のように、人や物事をこつこつ育てる人です。まじめで面倒見がよく、教える場面で力を発揮。考えすぎたら「十分」と区切って。","庚":"鍛えた鉄のように強く、決断の早い人。白黒をはっきりさせ、仲間のために体を張ります。言葉の切れ味を少しやわらげると味方が増えます。","辛":"磨かれた宝石のように繊細で、美しいものと品を大切にするタイプです。質の高い仕事が持ち味。自分を認めてくれる場所を選ぶと輝きます。","壬":"大海のようにスケールが大きく、自由を愛する人。頭の回転が速く、新しい世界へ飛び込む行動力があります。流れる先を決めると大きな力に。","癸":"静かな雨のように、まわりをそっとうるおす人です。直感が鋭く、相手の気持ちを察するのが得意。悩みは一人で抱えず話してみましょう。"},"shuku":{"昴":"落ち着いた品と、本物を見分ける目を持つ人です。目上に引き立てられやすい運の持ち主。好き嫌いを出しすぎないと人の輪が広がります。","畢":"決めたことを最後までやり抜く粘り強さが持ち味。積み重ねで確かな信頼を得るタイプです。ときにはやり方を変える柔軟さも試してみて。","觜":"言葉の扱いがうまく、知識を分かりやすく伝えられる人。お金の感覚も鋭く堅実です。ひと言多くならないよう、聞く側に回る時間も大切に。","参":"好奇心が強く、思い立ったらすぐ動ける行動派です。変化の多い場面ほど生き生き。始めたことを形にする根気を意識すると、ぐんと伸びます。","井":"筋道立てて考え、全体を見渡して判断できる頭脳派。冷静さから相談役として頼られます。正しさを押しつけない柔らかさが人間関係の鍵。","鬼":"子どものような純粋さと鋭い直感を持つ人です。心が動くものへ素直に向かい、周りを和ませます。段取りは誰かと分け合うとうまくいきます。","柳":"好きになったものに一途に打ち込む、情の深い人。集中したときの力は抜群です。気持ちを言葉にして伝えると、思いが執着に変わりにくくなります。","星":"人に頼らず、自分の力で道を切り開く独立心の持ち主。苦労を糧に遅咲きで花開くタイプです。頼る勇気を持つと、さらに道が広がります。","張":"人前で輝く華やかさがあり、自然と注目を集める存在です。場を盛り上げるリーダー役にぴったり。素の自分を認める余裕が強さになります。","翼":"高い理想を掲げ、遠くの目標へ着実に羽ばたく人。几帳面で丁寧な仕上がりが評判に。七割の出来でよしとする柔軟さが運を広げます。","軫":"誰とでもすぐ打ち解ける社交家で、手先も頭も器用な人です。移動や旅が運を運んでくるとされます。迷ったときは自分の本音を優先して。","角":"明るくおしゃれで、楽しいことを見つける天才。サービス精神で人が集まります。楽しさを人の役に立つ形にすると、魅力が実力に変わります。","亢":"曲がったことが嫌いで、相手が誰でも筋を通す人です。弱い立場の人をかばう気概も。正しさと同じくらい、伝え方を大切にするとよいでしょう。","氐":"心身ともにタフで、欲しいものをつかみ取る生命力にあふれた人。現実的で、物事を着実に増やしていけます。得たものは分け合うと運が広がります。","房":"穏やかで人に好かれ、物にも人にも恵まれやすいとされる人です。品ある振る舞いで信頼を集めます。自分から動く場面を一つ持つと運が生きます。","心":"相手の気持ちを読み、場に合った振る舞いができる愛嬌の人。人の心をつかむ演出力にすぐれます。心を許せる相手を持つと気分が安定します。","尾":"目標を決めたら脇目もふらずに進む、芯の強い人です。困難に耐える力は指折り。ときには人の意見を取り入れると、もっと進みやすくなります。","箕":"細かいことにこだわらない豪快さと、親分肌の気質を持つ人。外の世界でのびのび力を発揮します。勢いのあとに周りへのひと言を添えて。","斗":"大きな目標を掲げ、人を率いて進むカリスマ性の持ち主です。逆境でもあきらめない強さがあります。人に任せる場面を増やすと器が広がります。","女":"こつこつ学び続け、知識や技術を確かに身につける努力家。責任感が強く、任されたことをきちんとやり遂げます。自分にも人にも少し甘めに。","虚":"感受性が豊かで、芸術や学問など多方面に才能を持つ人です。独特の発想で人を驚かせます。心の拠り所を一つ決めておくと安心して伸びます。","危":"新しいものや流行をいち早く取り入れる、人付き合い上手な自由人。遠くの人ともすぐ仲良くなれます。大切な関係は意識して手入れを。","室":"何事にもエネルギッシュに取り組む、大胆で前向きな人。失敗してもすぐ立ち直れる楽天家です。人の歩幅に合わせると、支えがより厚くなります。","壁":"表に立つより陰で人を支えることに力を発揮する人です。誠実で口が堅く、深く信頼されます。ときには自分の希望も言葉にしてみましょう。","奎":"礼儀正しく、まっすぐで清らかな心を持つ人。うそやごまかしを嫌い、品ある振る舞いで信頼されます。白黒つけない余白を持つと楽になります。","婁":"周りによく気がつき、人と人の間を上手に取り持つ調整役です。手際よく実務をこなします。人の目を気にしすぎず、自分の時間も確保して。","胃":"目標に向かう意欲が強く、欲しいものを自分の手でつかみに行く行動派。競争の中で力を伸ばします。力の向け先は自分の成長に絞ると吉。"},"seal":{"1":"物事を最初に生み出す力を持ち、身近な人を家族のように守る人です。思い込むと頑固になりがち。自分を信じて動くほど周りが安心します。","2":"言葉や気持ちを運ぶ役目を持つ、感受性の細やかな人。場の空気をすっと感じ取ります。疲れたら深呼吸して、自分の感覚に戻りましょう。","3":"心に大きな夢を描ける、直感の鋭い人です。ひとりの時間で考えを熟成させるタイプ。夢を口にするほど、豊かさを呼び込みやすくなります。","4":"目標を決めてこつこつ育てる、好奇心の強い人。時間をかけて大きく花開くタイプです。考えすぎて止まったら、まず小さく試してみて。","5":"体の感覚と本能に正直で、好きなことにとことん集中する情熱家。困った場面でも生き抜く粘りがあります。気持ちは言葉で伝える練習を。","6":"人と人、場所と場所をつなぐ役目を持つ人です。手放すことで新しい機会をつかむ、節目に強いタイプ。自分の気持ちも後回しにしないで。","7":"手を動かし、体験から学ぶ器用な人。始めたことをやり遂げ、人の痛みにもそっと手を差しのべます。実際に触れて確かめるほど伸びます。","8":"美しいものへの感覚にすぐれ、物事を整った形に磨き上げる人です。細部にこだわる完璧主義な面も。少し甘めの採点で華やかさが輝きます。","9":"新しい流れを生み出す使命感の強い人。正しいと思えば一直線に進み、周りを巻き込みます。落ち込んだら水に流すように気持ちを切り替えて。","10":"誠実で、仲間や家族を何より大切にする人です。信じた相手には最後まで尽くします。外の人にも素直な愛情を表すと、信頼がさらに広がります。","11":"遊び心とユーモアで場を明るくする、自由な発想の人。難しい状況も楽しみに変えられます。本音を冗談で隠さず、心から楽しめることに打ち込んで。","12":"自分の考えで道を選びたい、学ぶことが好きな人です。知恵を人のために生かそうとします。人の意見を一度受け止めてから決めると影響力が増します。","13":"外の世界へ出て行き、人と人をつなぐ好奇心旺盛な人。行動範囲が広いほど元気に。身軽さを保ちつつ、帰る場所も大切にしましょう。","14":"誠実さと不思議な魅力で人を引きつける、器の大きな人です。許すことで関係を深めます。完璧でなくてよいと認めると、自然体の魅力が伝わります。","15":"高いところから全体を見渡し、先を読む力にすぐれた人。計画づくりが得意です。見えている未来を分かる言葉で伝えると、頼れる案内役に。","16":"疑問を持ち、答えを求めて挑み続ける正義感の強い人です。困難にも逃げません。ひとりで抱え込まず、問いを仲間と分け合うと力が増します。","17":"人との縁や偶然の一致を大切にする、舵取り上手な人。仲間をまとめて同じ方向へ導きます。心配しすぎず、ふと重なる出来事を合図にして。","18":"物事をありのままに映し出し、けじめと秩序を大切にする人です。厳しく見えても内側は情が深いタイプ。自分を責めすぎないことが強さに。","19":"周りを巻き込んで変化を起こす、エネルギーの強い人。思い立ったら一気に動き、停滞した空気を一新します。休む時間も意識してとって。","20":"太陽のように周りを明るく照らし、自然と人の中心に立つ人です。責任感が強く無理をしがち。自分自身を照らす時間も持ちましょう。"},"tone":{"1":"物事の始まりを表し、ひとつの目的へ人や物を引き寄せる音です。迷ったら「何のために」を先に決めると、自然に動き出せます。","2":"二つの間で揺れながら課題に向き合う音。対立や迷いを通り抜けることで、どちらにも偏らない落ち着いた安定を見つけていけます。","3":"動きを生み出し、人と人をつなぐ音です。誰かの役に立とうと動くと自分にもスイッチが入り、周りにも元気が伝わっていきます。","4":"あいまいなものに形と枠組みを与える音。測って確かめ、筋道を立てることで土台を固めます。まず書き出して整理すると力が出ます。","5":"中心に立って周りに力を配る、輝きの音です。自信を持って方向を示し、仲間それぞれの力を引き出せます。任せる場面も上手に作って。","6":"リズムを整え、釣り合いをとる音。かたよりを直し、みんなが同じように動ける流れをつくります。生活のリズムを守ると力が安定します。","7":"13のちょうど真ん中にあり、内側の声に耳を澄ませる音です。静かに受け取ったひらめきを周りへ伝える、橋渡し役に向いています。","8":"考えと行動を一致させる音。決めた筋を最後まで通し、周りとの調和を保ちながら人の手本になっていきます。言行一致が信頼の源です。","9":"はっきりした意図を持ち、形になるまでやり続ける音です。粘り強い実現力と、周りを動かす熱を持っています。目的を言葉にすると加速します。","10":"頭の中の考えを、目に見える結果へきちんと仕上げる音。成果を世の中に送り出す確かな力があります。最後のひと手間を惜しまずに。","11":"古いものを崩し、自由にする音です。こだわりを思い切って手放すことで、新しい可能性が開けます。片づけや見直しが運の入口に。","12":"人と力を合わせる音。知恵や経験を持ち寄って分かち合い、ひとりではできない大きなことを成し遂げます。話し合いの場で輝くタイプです。","13":"一巡りを締めくくる、大きな器の音です。体験をまるごと受け止め、次の始まりへつなげていきます。やり抜いた経験が自信になります。"},"lp":{"1":"自分の力で道を切り開く、始まりの数です。決断が早く先頭に立てますが、ひとりで抱え込みがち。人に頼ることで器の大きなリーダーに。","2":"相手の気持ちをくみ取り、場をやわらげる協調の数。人を支えるのが上手です。自分の本音にも同じだけ気を配ると、穏やかな強さが育ちます。","3":"思ったことを自由に表現し、周りを明るくする創造の数です。飽きっぽさも出やすいので、好きなことを一つ決めて育てると実りになります。","4":"しっかりした土台をつくる、誠実な数。約束を守り、こつこつ積み上げていきます。急な変化に戸惑ったら、少しの余白を持つと安定します。","5":"変化と冒険を楽しむ自由の数です。新しい場所や出会いでいきいきします。経験を一つずつ自分の言葉にまとめると、幅広い知恵になります。","6":"身近な人への愛情と責任を表す数。周りを居心地よく整える力があります。世話を焼きすぎたら、自分を大切にすることも愛のうちと考えて。","7":"目に見えないものを深く探る、探求の数です。納得するまで考え本質を見抜きます。分かったことを人と分かち合うと、知恵が信頼に変わります。","8":"大きな目標を立て、人や物をまとめて形にする力強い数。実行力が持ち味です。結果を急がず、得たものを周りに還すと豊かさが広がります。","9":"すべての数の経験をまとめる、思いやりの数です。心が広く、立場の違う人も受け入れられます。人のために動きすぎず、自分も大切に。","11":"ひらめきが鋭く、言葉にならないものを感じ取って伝える特別な数。感受性が強いぶん緊張をためがち。休む時間と安心できる人を持って。","22":"大きな夢を描き、仕組みや形として世の中に残す特別な数です。責任感が強く抱え込みがち。仲間に任せることで、より大きなものを築けます。","33":"損得を考えずに人を思いやり、独特の感性で周りを癒やす特別な数。気持ちが大きいぶん疲れやすいので、受け取る側に回ることも大切に。"},"animal":{"狼":"群れに頼らず自分のペースを大切にする、独立心の強いタイプです。ひとりの時間で力をため、信じた仲間にはとても誠実に向き合います。","猿":"頭の回転が速く、器用に何でもこなすタイプ。好奇心旺盛な場のムードメーカーです。ひとつのことを深める時間を持つと実力が増します。","虎":"堂々とした存在感と、正義感の強さが光るタイプです。面倒見がよく、頼られると力を発揮します。勢いのある日ほど周りへの気配りを添えて。","ライオン":"誇り高く、自然と人の上に立つ風格を持つタイプ。決めたことはやり抜く意志の強さがあります。ときには弱みを見せると距離が縮まります。","チーター":"思い立ったら一気に走り出す、瞬発力のあるタイプです。挑戦する気持ちが旺盛で、新しいことに強い人。息切れしないよう休憩も計画に。","熊":"のんびりして見えても、芯はしっかりした落ち着きのあるタイプ。じっくり考えてから動くので失敗が少なめです。気持ちは早めに言葉にすると吉。","象":"どっしりと構え、こつこつ努力を重ねていくタイプです。一度決めた道を着実に進みます。周りに頼る場面を作ると、さらに楽に進めます。","コアラ":"穏やかでマイペース、居心地のよい場所づくりが上手なタイプ。のんびりに見えて先を読む目もしっかり。休む時間を大切にすると力が続きます。","ひつじ":"仲間との和を大切にし、人の役に立つことに喜びを感じるタイプです。気配りが細やかで信頼されます。自分の気持ちも遠慮なく伝えて。","ペガサス":"翼を広げるように自由に発想し、ひらめきで動くタイプ。型にはまらない感性が魅力です。気分が乗る環境を選ぶと、才能がのびのび育ちます。","黒ひょう":"しなやかで洗練された雰囲気と、美意識の高さを持つタイプです。新しいものへの感度も抜群。プライドが傷ついたら、ひと息ついてから動いて。","たぬき":"人なつっこく、誰とでも打ち解けられる愛されタイプ。経験から学ぶ知恵があり、場の空気を和ませます。頼まれごとの引き受けすぎには注意を。"},"acolor":{"レッド":"レッドが加わると、情熱と行動力がいっそう表に出て、周りを元気づける力が強まります。","ゴールド":"ゴールドの輝きが重なり、華やかさと自信が増します。人を引き寄せ、豊かさを呼び込む力も高まるでしょう。","グリーン":"グリーンが添えるのは、落ち着きと調和の空気。人との和をはぐくみ、長く安定して力を出せます。","ブルー":"ブルーの冷静さが加わり、物事を客観的に見る力が増します。感情に流されにくく、判断も安定します。","パープル":"パープルの神秘的な色合いが重なって、感性と直感が深まります。独自の世界観が魅力として光ります。"}}};

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
  function red(n){while(n>9)n=sumd(n);return n;}
  function pDay(m,d){return red(red(PY+m)+d);}
  function dayKanshi(y,m,d){var i=mod(10+(jdn(y,m,d)-jdn(1900,1,1)),60);return {s:STEM[i%10],b:BR[i%12],si:i%10,bi:i%12};}
  var STEM_EL=['木','木','火','火','土','土','金','金','水','水'];
  /* 五行：AからBを見た関係（knowledge/05 の3-1） */
  function rel(a,b){if(a===b)return 'same';if(GENR[b]===a)return 'helped';if(GENR[a]===b)return 'give';if(CTL[a]===b)return 'rule';return 'pressed';}
  /* 地支どうし（knowledge/05 の3-7）：支合・三合・冲 */
  var GO={0:1,1:0,2:11,11:2,3:10,10:3,4:9,9:4,5:8,8:5,6:7,7:6};
  function brRel(a,b){if(a===b)return 'same';if(GO[a]===b)return 'go';if(mod(a-b,12)===6)return 'chu';if(mod(a-b,12)===4||mod(a-b,12)===8)return 'san';return 'none';}
  function pickv(arr,seed){return arr[mod(seed,arr.length)];}
  var PD_TIP={1:['新しいことを一つだけ始めてみて。','迷っていたことに、今日は答えを出してみて。'],2:['返事は少しゆっくりめに、言葉は丁寧に。','一人で決めず、誰かに相談すると話がまとまりやすい日。'],3:['楽しいと思うことを、まず自分に許してあげて。','気軽な連絡や雑談から、いい話が転がり込みそう。'],4:['机の上や予定表を整えると、気持ちも落ち着きます。','派手さより、決めたことを一つずつ。'],5:['いつもと違う道や店を選ぶと、小さな発見があります。','予定が変わっても、それを楽しむくらいでちょうどいい日。'],6:['家族や身近な人に「ありがとう」を伝えてみて。','頼まれごとを気持ちよく引き受けると、運が巡ります。'],7:['ひとりで考える時間を少しだけ確保して。','調べものや読書に向く日。無理に人に合わせなくて大丈夫。'],8:['先送りにしていた仕事や手続きを片づけるチャンス。','数字やお金のことを、今日のうちに確かめておくと安心。'],9:['使わない物を一つ手放すと、気持ちが軽くなります。','誰かのために動くと、自分にもいい流れが返ってきます。']};
  var EL_TXT={helped:['日の干支「{k}」は、あなたの「{me}」を育てる「{el}」の気。周りの助けを受け取りやすい日です。','「{k}」の日は、{el}の気があなたの{me}を後押し。人の厚意は素直に受け取って。'],same:['「{k}」の日は、あなたと同じ「{el}」の気。自分らしさを出しやすく、勢いもつきます。','日の干支「{k}」はあなたと同じ{el}の気。得意なことで力を発揮しやすい日です。'],give:['「{k}」の日は、あなたの{me}が「{el}」を生む関係。人に何かを与えると喜ばれる日です。','日の干支「{k}」は、あなたが力を注ぐ側に回る組み合わせ。張り切りすぎには気をつけて。'],rule:['「{k}」の日は、あなたの{me}が「{el}」をおさえる関係。主導権を握りやすい反面、言い方はやわらかく。','日の干支「{k}」とは、あなたがリードする組み合わせ。仕切る場面で力が出ます。'],pressed:['「{k}」の日は、「{el}」の気があなたの{me}をおさえる関係。予定は詰め込みすぎずに。','日の干支「{k}」は少しプレッシャーを感じやすい組み合わせ。早めに休むのが吉です。']};
  var BR_TXT={go:'生まれた日の「{b}」と今日の「{t}」は引き合う関係（支合）。人との縁が結ばれやすい日です。',san:'生まれた日の「{b}」と今日の「{t}」は仲間の関係（三合）。協力すると物事が進みます。',chu:'生まれた日の「{b}」と今日の「{t}」は向かい合う関係（冲）。予定の変更や行き違いに気をつけて。',same:'今日は生まれた日と同じ「{t}」の日。原点に返るような出来事がありそうです。',none:''};
  var VERD=[['ゆっくり休む日','無理をせず、体と心を休めることを優先して。'],['ひと息つく日','大きな決断は別の日に回し、身の回りを整える日に。'],['ふつうの日','いつものペースを大切に。小さな楽しみを一つ見つけて。'],['いい流れの日','気になっていたことに手をつけるのに向いています。'],['追い風の日','大切な予定や、人に会う用事を入れるのに向く日です。']];
  function fill(t,o){return t.replace(/\{(\w+)\}/g,function(_,k){return o[k]});}
  function dayFortune(m,d){
    var y=state.year,pd=pDay(m,d),kd=dayKanshi(2027,m,d),seed=m*31+d,score=2,lines=[];
    var me=GOGYO,label='星座の五行',ke=STEM_EL[kd.si];
    if(y){var bp=pillars(y,M,D),bsi=STEM.indexOf(bp.day.charAt(0)),bbi=BR.indexOf(bp.day.charAt(1));me=STEM_EL[bsi];label='生まれた日の日干「'+bp.day.charAt(0)+'」';}
    if(pd===1||pd===3||pd===8)score+=.5;if(pd===7||pd===9)score-=.25;
    lines.push(['日の数 '+pd,'「'+(GEN.pdKw[pd]||'')+'」。'+pickv(PD_TIP[pd],seed)]);
    var r=rel(me,ke);score+={helped:1,same:.5,give:0,rule:.25,pressed:-.75}[r];
    lines.push(['日の干支 '+kd.s+kd.b,fill(pickv(EL_TXT[r],seed+d),{k:kd.s+kd.b,me:me,el:ke})+'（あなたの五行は'+label+'の「'+me+'」で見ています）']);
    if(y){var br=brRel(bbi,kd.bi);if(BR_TXT[br]){lines.push(['生まれた日との関係',fill(BR_TXT[br],{b:BR[bbi],t:kd.b})]);}score+={go:1,san:.5,chu:-1,same:.25,none:0}[br];
      var k=jdn(2027,m,d)-jdn(y,M,D);
      if(!born(k))lines.push(['バイオリズム','まだ生まれる前の日なので、バイオリズムは出しません。']);
      else{var v=bioAt(k),av=(v[0]+v[1]+v[2])/3,g=bioGood(k),c=bioCare(k);
        lines.push(['バイオリズム','身体'+bioMark(v[0])[0]+'・感情'+bioMark(v[1])[0]+'・知性'+bioMark(v[2])[0]+'。'+(g?'3つの波がそろって高い「好調日」です。':c?'波が切り替わる「注意日」。うっかりミスに気をつけて。':av>.2?'波は上向きで、動きやすい日。':av<-.2?'波は低めなので、ペースを落として。':'波はおだやかな日です。')]);
        score+=g?1:c?-.75:av>.2?.5:av<-.2?-.5:0;}}
    var vi=Math.max(0,Math.min(4,Math.round(score)));
    var W='日月火水木金土'.charAt(new Date(2027,m-1,d).getDay());
    var h='<div class="fh-b27-dayhead"><b>2027年'+m+'月'+d+'日（'+W+'）</b><span class="fh-b27-verd fh-b27-v'+vi+'">'+VERD[vi][0]+'</span></div>';
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
    for(var d=1;d<=n;d++){var cls='fh-b27-cday',mk='',sub='';
      if(b!==null){var k=jdn(2027,m,d)-b;if(born(k)){var v=bioAt(k);mk=bioMark((v[0]+v[1]+v[2])/3)[0];if(bioGood(k))cls+=' fh-b27-cg';else if(bioCare(k))cls+=' fh-b27-cc';}else mk='·';}
      sub=mk||String(pDay(m,d));
      if(state.pick&&state.pick.m===m&&state.pick.d===d)cls+=' fh-b27-csel';
      if(m===BD[0]&&d===BD[1])cls+=' fh-b27-cbd';
      h+='<button type="button" class="'+cls+'" data-d="'+d+'" aria-label="'+m+'月'+d+'日'+(mk?'（'+mk+'）':'')+'"><b>'+d+'</b><small>'+sub+'</small></button>';}
    box.innerHTML=h+'</div><p class="fh-b27-small">'+(b!==null?'日付の下の印は3本の平均（★◎〇△▽）。金色＝好調日、灰色＝注意日。':'日付の下の数字は、その日の数（数秘）です。')+'誕生日は点線の枠。</p>';
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
