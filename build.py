from pathlib import Path
import json,re,html,hashlib
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'dist';OUT.mkdir(exist_ok=True)
pages=json.loads((ROOT/'pdf-extracted.json').read_text(encoding='utf-8')) if (ROOT/'pdf-extracted.json').exists() else json.loads((ROOT/'reference-text.json').read_text(encoding='utf8'))
def clean(s):
    return re.sub(r'^\s*\d+\s*\n','',s).strip()
def span(a,b):return '\n\n'.join(clean(p) for p in pages[a-1:b])
E=html.escape
CCI='https://ccifellowship.org/books/book-of-praise/'
documents=[('apostles','使徒信经',span(4,4).split('我信神，全能的父')[1],CCI+'creeds/apostles-creed'),('nicene','尼西亚信经',span(5,6),CCI+'creeds/nicene-creed'),('athanasian','亚他那修信经',span(7,9),CCI+'creeds/athanasian-creed'),('belgic','比利时信条',span(10,46),CCI+'confessions'),('heidelberg','海德堡要理问答',span(47,93),CCI+'confessions/heidelberg-catechism'),('dort','多特信经',span(94,137),CCI+'confessions/canons-of-dort')]
documents[0]=(documents[0][0],documents[0][1],'我信神，全能的父'+documents[0][2],documents[0][3])
documents[1]=(documents[1][0],documents[1][1],documents[1][2][documents[1][2].index('我们信独一的神'):],documents[1][3])
documents[2]=(documents[2][0],documents[2][1],documents[2][2][documents[2][2].index('1) 所有'):],documents[2][3])
web_creeds=json.loads((ROOT/'cci-creeds.json').read_text(encoding='utf8'))
documents=[(slug,title,web_creeds.get(slug,text),url) for slug,title,text,url in documents]
# 原始提取留存于本地；展示版仅消除 PDF 物理换行，不改标点、字词。
def paras(text):
    blocks=re.split(r'\n\s*\n',text)
    return ''.join('<p>'+E(re.sub(r'\s*\n\s*','',x).strip())+'</p>' for x in blocks if x.strip())
for slug,title,text,url in documents:
    source_note='来源：CCI网站对应信经正文，2026-10-21录入核对，保留该页字词、标点与编号；排版空白已整理。中文译文不是古代原语言文本。' if slug in web_creeds else '来源：您提供的《中国改革宗教会敬拜手册》（2015）。仅整理物理换行，未擅自修正文句；此版尚未完成与网站全文逐字比对，不标称网站逐字校定本。中文译文不是古代原语言文本。'
    (OUT/(slug+'.html')).write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'''+title+''' · 净读</title><link rel="stylesheet" href="style.css"><body class="reader"><header><a href="index.html#library">← 返回研读</a><button onclick="window.print()">打印 / 保存 PDF</button><button id="mask">背诵遮罩</button><button id="speak">朗读 / 暂停</button><button id="size">字号 ＋</button></header><main><small>中文信经信条 · 来源见下方说明 · 净读版</small><h1>'''+title+'''</h1><p class="notice">'''+source_note+'''<a href="'''+url+'''" target="_blank" rel="noopener">前往 CCI 来源核对 ↗</a></p><article id="reading">'''+paras(text)+'''</article><footer>译本版权归原出版委员会；此学习重排不主张原文版权。研读释义与信条文本须加以区分。</footer></main><script src="reader.js"></script></body></html>''',encoding='utf-8')
dort=span(95,137)
headpat=r'第(?:一|二|三、四|三/四|三和四|三及四|三与四|三、第四|五)项教义'
# 以正文标题的真实位置切分，不把简介或条内交叉引用算作标题。
heads=list(re.finditer(r'(?m)^第(?:一|二|三、四|五)项教义[^\n]*',dort))
assert len(heads)==4,[m.group() for m in heads]
parsed={}
for j,key in enumerate(['I','II','IIIIV','V']):
    txt=dort[heads[j].end():heads[j+1].start() if j<3 else len(dort)]
    pos=txt.index('错谬反驳');positive,negative=txt[:pos],txt[pos:]
    matches=list(re.finditer(r'(?m)^第[一二三四五六七八九十]+条[^\n]*',positive))
    arts=[]
    for k,m in enumerate(matches):arts.append({'n':k+1,'title':m.group(),'text':positive[m.end():matches[k+1].start() if k+1<len(matches) else len(positive)].strip()})
    errs=list(re.finditer(r'错谬[一二三四五六七八九]+[：:]',negative))
    er=[{'n':k+1,'text':negative[m.start():errs[k+1].start() if k+1<len(errs) else len(negative)].strip()} for k,m in enumerate(errs)]
    parsed[key]={'articles':arts,'errors':er}
assert [len(parsed[k]['articles']) for k in parsed]==[18,9,17,15]
assert [len(parsed[k]['errors']) for k in parsed]==[9,7,9,9]
(ROOT/'parsed-dort.json').write_text(json.dumps(parsed,ensure_ascii=False,indent=2),encoding='utf8')
sections=[]
def section(id,kicker,title,body):
    sections.append((id,title));return f'<section id="{id}"><div class="eyebrow">{kicker}</div><h2>{title}</h2>{body}</section>'
def cards(items):return '<div class="cards">'+''.join(f'<article class="card"><h3>{a}</h3><p>{b}</p></article>' for a,b in items)+'</div>'
def table(headers,rows):return '<div class="tablewrap"><table><thead><tr>'+''.join('<th>'+x+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+x+'</td>' for x in r)+'</tr>' for r in rows)+'</tbody></table></div>'
body=section('vision','01 / THE WHOLE BIBLE','先见森林：三一神恢复他的创造', '''<p class="lead">《多特信经》的中心不是给人一张猜测永恒名册的地图，而是宣认：<mark>父在基督里施恩，子以自己的血实际救赎，圣灵使死人活过来，并保守他们走到终点。</mark>救恩从恩典起始，也由恩典完成；得救的人因此真正相信、悔改、顺服、祷告。</p><p>先从创世记到启示录读，再回到五项教义。圣经的主轴是神的荣耀、他的国度与圣约在耶稣基督里的成全；多特只是在一个具体争端中，守护这宏大叙事里的救恩真理。它既非整部神学的替代品，也非凌驾圣经的系统。信条是服从圣经的教会见证，圣经才是最高准则。</p><div class="flow"><b>🌿 创造<br><small>形象 · 使命 · 安息</small></b><i>→</i><b>🍂 堕落<br><small>罪责 · 败坏 · 死亡</small></b><i>→</i><b>🌅 应许<br><small>后裔 · 圣约 · 国度</small></b><i>→</i><b>✝ 基督<br><small>成全 · 代赎 · 复活</small></b><i>→</i><b>🕊 圣灵<br><small>联合 · 信心 · 成圣</small></b><i>→</i><b>✨ 新创造<br><small>复活 · 同住 · 荣耀</small></b></div>'''+table(['圣经进程','真实处境与神学重点','与多特相遇'],[
['创1—3；罗5:12–21','人按神形象被造，亚当真实犯罪；罪不只是环境问题，也涉及归算与内在败坏。','I.1；III/IV.1–3：恩典回答有罪者的困境。'],
['创12、15、17；加3:6–29','神呼召亚伯拉罕，赐后裔与万国得福的应许；拣选不是族群优越。','I.8；II.9：旧新约一个救恩，福音临万族。'],
['出12、19—24；利16；来9—10','出埃及、祭司与赎罪日预表中保；献祭不能靠自身重复除罪。','II.1–4、8：基督一次满足公义、坚立新约。'],
['撒下7；耶31:31–34；结36:25–27','大卫后裔、赦罪、新心与圣灵的应许；不是靠外在律例修补死人。','III/IV.6、11–12：应许由圣灵实现。'],
['路22:20；约6、10、17；罗3—8','十字架不是试探性的救援；复活主赐生命、代求并招聚群羊。','II.8；V.8：成就与施行不能相互割裂。'],
['弗1—2；徒2；启5、21—22','教会跨越犹太人与外邦人的隔墙，走向羔羊的新创造。','I.7；II.9；V.15：目标是敬拜与圣洁群体。']
])+'''<div class="note"><b>读经方法</b>：先读整段、辨明体裁与救赎历史位置，再比较相关经文。罗马书9章不能脱离9—11章以色列与外邦人的问题；以弗所书1章的拣选，也不能脱离2章在基督里成为一家的结果。不要只把章节当作口号的脚注。</div>''')
body+=section('covenant','02 / COVENANT','圣约之窗：永恒旨意如何进入真实历史',cards([
('🧭 圣约不是第二套救法','创造中的顺服责任与亚当的代表性，常以“行为之约”作系统表达；三项联合信条承认其重要实质，却不都使用同一术语。恩典之约的救恩根基是基督的顺服与代赎，领受的工具是信心；信心不是新版本的功德。'),
('🩸 十架真正坚立新约','多特II.8及II驳谬2强调基督之血与新约；耶31、路22、来8—10共同说明：救恩不是神降低公义门槛，让不完全的信心顶替完全的义，而是中保实际满足公义并赐下赦罪。'),
('🌱 恩典先行，回应真实','约的应许、命令、警告都真实临到会众。主权恩典不把信仰变成消极旁观，反而产生认罪、信靠、顺服。重生在因果上使信心成为可能，不意味每个人都能辨认自己的重生时刻。'),
('👶 约民与蒙选不能简单画等号','圣约在历史中的施行包括信徒及其儿女，须严肃教导并呼召信心；不能从受洗推出每个人必已重生。I.17特别安慰敬虔父母关于早逝婴孩，不是对一切婴孩命运或每个受洗者结局的无限断言。')
])+'''<p>从亚当到基督，并非两个人各给一份道德榜样：罗5:12–21呈现两位代表及其结果。基督的主动顺服与受苦顺服属于同一救赎工作；多特聚焦其有效性，《比利时信条》22—23条更展开因信称义。《海德堡》问答60—64把白白称义与感恩善行连起来，防止“恩典”沦为放纵的借口。</p><p>荷兰传统内部对圣约成员、应许的表述、普遍恩典及福音呼召有真实争论。CanRC、URCNA、Heritage、PRCA共同认同三项联合信条，不表示每项后续神学表达都相同。本研读以公开信条为共同边界，不把某一宗派的全部立场强加于其他教会。威斯敏斯特信仰告白第7、10、17、18章可作结构对照，不能反过来替换多特文本。</p>''')
timeline=[('325 / 381','尼西亚与君士坦丁堡','面对基督神性与圣灵教义的争辩，教会公开辨认所敬拜的是谁。后来的西方文本加入“和子”；不可把它倒置为325年全文。'),('约六世纪','西方拉丁教会','《亚他那修信经》清晰区分三个位格与一个本质，并守护基督神人二性；不是亚他那修亲笔。'),('1561','尼德兰南部','德布利在逼迫中写《比利时信条》，表明改革宗信仰及教会生活，不是鼓吹无政府的团体；1567年殉道。'),('1563','普法尔茨 · 海德堡','腓德烈三世推动教理教育；要理问答把教义、安慰、诫命、祷告编织成全年牧养。'),('1568—1648','尼德兰起义与独立战争','北部共和国逐渐形成；宗教、城市自治、省权、军事权与国际外交相互牵连。现代荷兰、比利时国界不可原样投射到当时。'),('1603—1609','莱顿大学','阿米念任神学教授，与戈马鲁斯围绕预定等问题争辩；阿米念1609年去世，没有亲赴1618年大会。'),('1610 / 1611','抗辩与反抗辩','追随者提出五点抗辩，要求教会处理分歧；1611年的回应使双方界线更清楚。1610年第五点对最终失落尚保留研究态度，后续立场有发展。'),('1618-11-13','多德雷赫特开会','国内代表与外国代表在多特集会，博格曼任主席；拉丁文让跨国代表得以沟通。政治委员在场，绝非现代政教分离环境。'),('1619年春—5月','教义裁决与后续会议','多特文本形成并获通过；国际阶段与荷兰国内后续议程需区分。5月9日常用于国际阶段结束，全部会议延续到5月29日。'),('1619-05-13','海牙的政治悲剧','奥尔登巴内费尔特被国家司法处死；不能说是多特大会下令处死。神学判断必须由经文论证，也不应为政治暴力涂上圣洁色彩。'),('1637 → 今日','荷兰圣经与跨洋传承','大会推动的国家译本后来出版；三项联合信条在荷兰移民教会及多语言教会中继续使用。今天华人会众亦藉教理与圣礼承接这条传承。')]
body+=section('history','03 / TIME · STORY','时间线：从受逼迫的告白到恩典的争辩','<div class="timeline">'+''.join(f'<article><span>{a}</span><div><h3>{b}</h3><p>{c}</p></div></article>' for a,b,c in timeline)+'</div><p class="source">史料核验：<a href="https://www.hofvannederland.nl/collectie/synode-van-dordrecht/">多特本地博物馆</a> · <a href="https://collecties.kb.nl/en/collections/friendship-books/celebrities-friendship-books/album-amicorum-johannes-rufelaert">荷兰国家图书馆大会签名册</a> · <a href="https://www.nationaalarchief.nl/beleven/nieuws/johan-van-oldenbarnevelt-1619">荷兰国家档案馆</a></p>')
body+=section('geography','04 / PLACES & CULTURES','地图：不是孤立的荷兰争论','''<div class="mapgrid"><div><svg class="map" viewBox="0 0 760 510" role="img" aria-label="西欧研读地点示意图，现代经纬度投影，非1618年国界"><defs><pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#ffffff15"/></pattern></defs><rect width="760" height="510" rx="20" fill="#173b4b"/><rect width="760" height="510" fill="url(#grid)"/><path d="M165 55L190 80 181 126 205 154 190 194 225 224 202 256 156 269 116 243 145 205 122 177 151 137 140 99Z M88 128L117 137 104 192 78 216 60 186Z M354 36L388 62 382 102 425 134 471 121 495 155 560 173 638 194 698 246 735 300 721 480 505 480 458 443 412 426 353 445 303 412 264 350 243 317 274 286 313 276 325 239 337 200 355 168 348 130 362 96Z" fill="#38615f" stroke="#b9d7c277" stroke-width="2"/><text x="64" y="332" fill="#a8d7e5" font-size="18">大 西 洋</text><text x="220" y="110" fill="#a8d7e5">北海</text><g fill="none" stroke="#e9ba6b" stroke-width="2" stroke-dasharray="7 7"><path d="M167 239L350 237 361 216 M350 237L476 338 M350 237L445 428"/></g><g fill="#f4c987" stroke="#173b4b" stroke-width="3"><circle cx="350" cy="237" r="9"/><circle cx="361" cy="216" r="7"/><circle cx="167" cy="239" r="7"/><circle cx="476" cy="338" r="7"/><circle cx="445" cy="428" r="7"/><circle cx="345" cy="280" r="7"/></g><g fill="white" font-size="17"><text x="366" y="251">多德雷赫特</text><text x="377" y="212">莱顿</text><text x="92" y="268">伦敦</text><text x="485" y="359">海德堡</text><text x="455" y="449">日内瓦</text><text x="267" y="303">南尼德兰</text></g><text x="24" y="477" fill="#c4d6cf" font-size="13">教学示意 · 现代坐标近似定位 · 连线为思想交流，不代表实际行程</text></svg><p class="source">原创 SVG 示意图，地理形状简化；选择右侧地点可查看坐标及文化背景。</p></div><div id="places"></div></div>'''+table(['区域','文化制度与处境','对研读的帮助'],[
['北部尼德兰：荷兰省、城市共和国','港口、印刷、大学与多层政治权力并存；改革宗为公共教会，社会仍有不同宗教群体。','争论既涉及讲台，也触及国家与省、市谁有权召集会议。贸易繁荣不等于人人富足或自由平等。'],
['南部尼德兰：今比利时等地区','哈布斯堡统治下的宗教压迫、流亡网络与法语／荷语交织。','《比利时信条》的公共申诉与教会论，来自真实生存压力。'],
['德意志普法尔茨','神圣罗马帝国的领邦体制、大学与教会教育；改革宗与路德宗分歧需治理。','《海德堡》重视共同教导和个人安慰，不只是私人灵修。'],
['瑞士与日内瓦、英格兰和苏格兰','不同教会制度、君权处境与改革经验，经移民、书信和使节交流。','国际代表并不在每个问题上完全一致；共同裁决不等于所有细节只剩一种学术解释。']
]))
body+=section('story','05 / THE CENTRAL QUESTION','故事线：是谁使救恩的应许成为现实？','''<p>设想一位牧者面对惧怕失落的会众，一位教授努力说明神的公义，一位城市执政者担心内战。这是三个不同问题。若只讲抽象因果，就看不见人；若只讲政治斗争，就听不见真实的释经争执。</p><p>阿米念一方并非公开宣称人不需要恩典；争点在于：恩典是否最终、有效地产生使人得救的信心？拣选以神预见人的信为条件，还是信心出于在基督里的拣选？基督是否只提供一个可能被所有人拒绝的机会？真信徒能否最终完全失去救恩？多特的答复坚持，最终区分得救与不信者的，不是人独立于恩典的优越决定，而是神怜悯的有效施行。</p><div class="note"><b>公平理解争论</b>：1610年抗辩、后续抗辩派意见和现代不同阿民念传统不能压成同一段话。这里的驳谬对准大会所审理的具体命题。可以坚定不同意，同时准确转述对方。</div><div class="flow"><b>共同罪境</b><i>→</i><b>父白白拣选</b><i>→</i><b>子成就救赎</b><i>→</i><b>灵赐信心</b><i>→</i><b>蒙保守而坚忍</b><i>→</i><b>归荣耀于神</b></div><p>这张图表达逻辑关联，不是把三一神分为先后轮流工作的三个部门，也不是可以被我们看见的个体心理时间表。三一神对外工作不可分割；每个位格的独特工作，也不能被抹平。</p>''')
body+=section('architecture','06 / HOW TO READ','五项教义，四个篇章，双重论证',table(['篇章','正面陈述','驳谬','核心提问','记忆色'],[['I 拣选与弃绝','18条','9项','恩典的源头在哪里？','🟨 父的旨意'],['II 基督之死与救赎','9条','7项','十架实际成就了什么？','🟥 子的代赎'],['III/IV 败坏与归正','17条','9项','罪人如何真正归信？','🟦 灵的更新'],['V 圣徒恒忍','15条','9项','软弱者如何抵达终点？','🟩 约的信实']])+'''<p>合计<strong>59条正面陈述、34项驳谬</strong>。第三和第四项合并，因为“人为什么不能自救”与“神如何使人归正”必须一起说明。TULIP是后来的英语记忆缩写，不是大会原来的编排；它易记，也容易把福音宣讲、教会和蒙恩途径挤到画面以外。</p><p>下面各条<strong>先给原创解释，再给附件译文</strong>。字词与标点没有擅自修订，排版换行已整理；来源状态始终可见。默认平铺解释，原文可逐条展开，也可一键全部展开。</p><button id="expandAll">展开全部原文</button> <button id="collapseAll">收起全部原文</button>''')
notes=json.loads((ROOT/'commentary.json').read_text(encoding='utf8')) if (ROOT/'commentary.json').exists() else {}
for key,title,kicker in [('I','第一项 · 拣选与弃绝','07 / THE FATHER’S PURPOSE'),('II','第二项 · 基督之死与救赎','08 / THE SON’S ACCOMPLISHMENT'),('IIIIV','第三、四项 · 败坏与归正','09 / THE SPIRIT’S RENEWAL'),('V','第五项 · 圣徒恒忍','10 / PRESERVED TO PERSEVERE')]:
    content=''
    for art in parsed[key]['articles']:
        n=art['n'];note=next((x for x in notes.get(key,[]) if x['n']==n),{})
        content+=f'<article class="doctrine searchable" id="{key}-{n}"><div class="num">{key}.{n:02}</div><div><h3>{E(art["title"])}</h3><div class="interpretation"><span class="tag">释义</span><p>{E(note.get("point","释义整理中"))}</p><p class="bible">📖 {E(note.get("scripture",""))}</p><p class="apply">↳ {E(note.get("application",""))}</p></div><details class="original"><summary>2015 附件译文 · 展开核读</summary>{paras(art["text"])}</details></div></article>'
    content+='<h3 class="errorheading">🛡 对应驳谬：辨明具体分歧</h3>'
    for er in parsed[key]['errors']:
        note=next((x for x in notes.get('errors',{}).get(key,[]) if x['n']==er['n']),{})
        content+=f'<article class="error searchable"><h4>{key} · 驳谬 {er["n"]}</h4><p>{E(note.get("point",""))}</p><details class="original"><summary>查看被驳命题及原有反驳</summary>{paras(er["text"])}</details></article>'
    body+=section('head-'+key,kicker,title,content)
body+=section('conclusion','11 / THE CONCLUSION','不要遗漏结语：教义也要求我们如何说话','''<p>附件的多特部分到第五项驳谬结束，未收录完整的大会结语。这里提供<strong>原创提要，非CCI译文，也非结语逐字翻译</strong>；完整参考可由<a href="https://threeforms.org/canons-of-dort/">URCNA所链接文本</a>阅读。</p><p>结语把教会的公开认信与外界的恶意指控分开：改革宗不认神为罪的作者，不宣称人是木石，不把得救者的信心视为无关紧要，也不教导任人放纵。不能摘取个别作者脱离语境的话，取代教会共同认可的告白。牧者应按圣经的界限教导，拒绝离开经文的揣测；教义的表达也要顾念听者，避免滋生误解与毁谤。</p><div class="note"><b>牧养上的验收标准</b>：读完以后，是否更敬拜神、更单单倚靠基督、更认真听道悔改、更温柔对待软弱者？如果只学会了用标签压倒别人，却不再祷告、传福音或爱教会，就把文本的用途读反了。</div>''')
body+=section('difficulties','12 / ESSENTIAL DISTINCTIONS','十个难点：用界线守护核心',table(['容易混淆','应当分辨','实际应用'],[
['神的主权 = 神制造罪？','神定旨、治理与人的真实罪责并存；I.5、15拒绝神是罪源。拣选赐信，定罪因罪，不是两个道德对称动作。','承认启示的界限，不以数学对称替代经文。'],
['全然败坏 = 人人坏到极点？','败坏遍及人的各方面，不等于每个人每时都犯最恶的罪；自然认识、外在秩序仍存在（III/IV.4）。','尊重邻舍的社会善举，同时不把它当作称义资本。'],
['无条件拣选 = 无须信？','不是以预见的信为拣选原因；神却定意藉信心使人得救（I.7、9）。','来信基督，不去找绕开基督的入场凭证。'],
['特定救赎 = 基督价值有限？','II.3–4论无限价值，II.8论确定救赎对象与果效，II.5论普遍宣告；三个层次不能互相取消。','向每位听者真诚宣讲凡信者必得救。'],
['不可抗拒 = 从没人抗拒神？','罪人确实抗拒；有效恩典改变刚硬的心，使人甘心相信，非暴力强迫仍厌恶基督的人。','不以操纵情绪制造“重生”，认真传道并求圣灵。'],
['信是礼物 = 不是我相信？','III/IV.12、16把神的更新与人的真实行动连在一起；人不是被替代的木石。','把信心付诸行动，并把荣耀归给赐恩者。'],
['永蒙保守 = 犯罪无所谓？','V.4–7承认重跌、忧伤与管教；神恢复真实悔改，使人继续坚忍。','劝勉远离罪，不以一次决志替代一生信靠。'],
['确据 = 感觉永不动摇？','V.9–11区分客观应许与主观体验；信徒确据有强弱，根基是神的信实。','先看基督应许，再看圣灵所结果子；不要循环检查自己到绝望。'],
['保守 = 不需途径？','III/IV.17、V.14把神的主权与圣道、圣礼、劝诫、警告连在一起。','参与教会生活，遵行警告；神以这些保守人。'],
['三项联合 = 全体欧陆宗派无差异？','共同文本不是后续争论全部解决；对普遍恩典、福音呈献和圣约的细节要标明宗派立场。','辨认共同认信和宗派解释，避免以少数代替整体。']
]))
body+=section('compare','13 / THREE FORMS OF UNITY','为什么是三份信条？同一信仰的三种任务',table(['维度','比利时信条','海德堡要理问答','多特信经'],[
['年代与处境','1561；逼迫中的公开见证','1563；领邦教会的教理教育','1618—1619；围绕五点争端的教会裁决'],
['表达方式','37条系统告白：“我们相信”','129问答、52主日；将真理化为信徒的回答','59条陈述＋34驳谬；辨明特定命题'],
['主线','启示 → 三一神 → 人与基督 → 救恩 → 教会圣礼 → 末世','唯一安慰；罪与愁苦 → 拯救 → 感恩','拣选 → 代赎 → 败坏与更新 → 保守'],
['直接用途','向社会及教会公开说明共同信仰，界定教会身份','儿童、家庭、慕道与全会众长期教导，连接教义与敬拜','澄清争议，保护纯正讲台，安慰良心并规范教导'],
['救恩同心','16、20—24条：恩典拣选、基督满足、信心、称义与成圣','20—21、60—64问：基督与信心，称义与感恩之果','I.7–9、II.8、III/IV.14、V.14：同一救恩的来源、成就、施行、保守'],
['圣约与教会','27—35条：教会、职分、洗礼与圣餐','65—82问：圣道圣礼与天国钥匙；74问关乎婴儿','I.17；II.8；III/IV.17；V.14：重点而非完整教会论'],
['不宜单独承担','不是按周设计的完整教学问答','不是逐一裁断1610年后争议的会议文献','不是完整神学百科，不能替代创造、三一、教会与末世的系统教导']
])+'''<p class="lead">记忆一句话：<strong>比利时说“我们所信”，海德堡问“我如何得安慰”，多特辨“为何全是恩典”。</strong></p><p>一份文件当然可以扩充得更长，但教会需要的不只是信息总量：有向外公开的见证，有向内代代教导的课程，也有争端中的共同判决。三份互相约束，使“系统的完整”“牧养的温度”“争辩的精度”同时留在教会里。这不是三种救恩，三者在三一神、基督中保与因信称义上共同见证圣经。</p><h3>与三大普世信经的关系</h3>'''+cards([('使徒信经 · 叙事骨架','创造、道成肉身、十架复活、圣灵、教会与永生构成入门认信的骨架。其名称表达使徒教训的总结，不是十二使徒各写一句的史实。'),('尼西亚信经 · 谁来救我们','与父同质的子不是高等受造物。若救主不是真神，就无法作为我们真正敬拜和永远得救的根基。381形态及后来的西方用语必须历史地区分。'),('亚他那修信经 · 既不混淆也不分割','三个位格而一个本质；基督一个位格而神人二性。其严肃救恩用语指向所信之神与救主的真实性，不是说会背一套术语本身使人称义。')])+'''<p>“普世”是改革宗对大公信仰传承的用语，并不意味着今天各基督教传统无差别接受这三份文本每一种历史版本。尤其《亚他那修信经》及“和子”措辞具有西方传统位置。三一神对外工作的合一，与基督二性的区分，为多特II.4所论代赎价值提供正统教义前提。</p>''')
body+=section('library','14 / THE READING ROOM','六份文本 · 独立净读与背诵', '''<p>前三份是按CCI网站正文录入的<strong>三大普世信经</strong>净读页，后三份是<strong>三项联合信条</strong>完整附件文本阅读页。三份“信经”与三份“信条”均保留独立入口，方便避免名词混淆。支持打印、放大字号、遮罩背诵和设备语音。</p><div class="cards library">'''+''.join(f'<a class="card" href="{slug}.html"><small>{"普世信经" if i<3 else "联合信条"}</small><h3>{title} ↗</h3><p>净读 · 背诵 · 打印 · 朗读</p></a>' for i,(slug,title,_,_) in enumerate(documents))+'''</div><div class="note"><b>版本校勘说明</b>：CCI《亚他那修信经》简介称第二部分至第43点，网页正文实际编号止于42；本文不凭其他译本补号。《尼西亚信经》的“和子”属于所采用的西方文本传统。PDF中疑似标点、排版或经文脚注错位，保持来源字样，不偷偷“修好”；读者应查经复核。三份普世信经采用已读取的CCI网页正文；三项联合信条仍为附件底本，不能宣称六份全文均已与网站完成逐字校定。</div>''')
body+=section('memory','15 / LEARN · RECALL · LIVE','记得住：五个动词，一条救恩线','''<div class="memoryline"><b>父拣选</b><b>子救赎</b><b>人败坏</b><b>灵更新</b><b>神保守</b></div><p>缩记是<strong>“选—赎—败—新—守”</strong>。原文次序是I、II、III/IV、V；背诵五词时，不要把“败坏”理解为在十架以后才发生。每个词都应连同“基督、福音、教会、感恩”一起记。</p><div id="flashcard" class="flashcard" tabindex="0" role="button" aria-label="点击翻开记忆卡"><small id="cardno"></small><h3 id="question"></h3><p id="answer" hidden></p><span>点击卡片 / Enter 查看答案</span></div><button id="prev">← 上一张</button> <button id="next">下一张 →</button><h3>七日学习路径</h3>'''+table(['天','读什么','闭卷自问'],[['1','总览＋圣约＋历史地图','为什么多特不能被缩成孤立五点？'],['2','I.1–18及驳谬','为何信是拣选果子，而不是选我的原因？'],['3','II.1–9及驳谬','怎样同时说明无限价值、特定果效与普遍宣讲？'],['4','III/IV.1–17及驳谬','有效恩典如何使人的意志甘心，而非消灭意志？'],['5','V.1–15及驳谬','跌倒、确据、恢复和蒙恩途径如何相连？'],['6','三份信条对比；三份普世信经净读','一份公开告白、一本教理与一份裁决各做什么？'],['7','结语＋难点；向别人复述十分钟','我怎样用这教义安慰忧伤者，又警告放纵者？']])+'''<p>建议第1、3、7、14、30天回顾，先尝试回忆再看答案。学习记录只存于此设备；“已读”是学习进度，不是信仰测验或得救证明。</p><div id="checklist"></div><button id="exportNotes">导出我的学习笔记</button><label class="notelabel">个人笔记<textarea id="personalNotes" rows="6" placeholder="记录问题、经文、祷告与下一步应用……"></textarea></label>''')
body+=section('practice','16 / PASTORAL APPLICATION','把教义带回真实生活',cards([
('🕯 “我怕我不是被拣选的”','不要先审阅隐藏名册。按I.16，把目光带回基督的应许，继续听道、祷告、求恩。忧伤的寻求者不是应被随意宣判为弃绝的人；软弱不等于没有信。'),
('🤲 “我又严重跌倒了”','不要用保守为罪辩护，也不凭跌倒断言恢复无望。V.5–7让人承认得罪神的严重性，向神认罪，并在教会牧养中归回；基督的代求是真实盼望。'),
('🌍 “既预定，为什么还传福音？”','I.3、II.5、III/IV.17说明神连途径也定下。我们不知道隐藏的名册，却清楚领受传福音的命令。向所有听者宣告真实应许，不先筛选谁“看起来像选民”。'),
('🧺 “信靠恩典，我还需要努力吗？”','神在内心动工，使人愿意并能行动（腓2:12–13）。努力不是买取救恩的代价，而是活在救恩里的回应；祷告、善行、婚姻责任和邻舍之爱都因此有位置。'),
('⛪ “这与主日敬拜有什么关系？”','恩典借圣道开始，借圣道圣礼坚固。宣召、认罪、赦罪应许、讲道、圣餐、感恩回应把救恩从理论带进群体生活；不是靠视觉或音乐强度制造得救确据。'),
('💬 “我该怎样与不同立场的人交谈？”','先准确复述对方，再分辨命题与经文。拒绝羞辱性标签，不把所有对手说成不用恩典。按结语的精神，让论证的内容与说话的方式共同服从基督。')
]))
body+=section('sources','17 / SOURCES & EDITORIAL NOTES','来源、版本与研读边界','''<p>编写日期：<time>2026-10-21（Asia/Taipei）</time>；版本：<strong>v1.0 · 多特信经-20261021-v1-GTstudy</strong>。本网站的说明、图解、应用与记忆材料为本次编写，非教会正式审定课程。信条译文与解释分栏标示，任何分歧须回到圣经及原始文本核验。</p><ol><li><b>用户提供的文本底本</b>：《中国改革宗教会敬拜手册》（2015），PDF共245页；书内印页5—10为三份普世信经、11—47为比利时信条、48—94为海德堡要理问答、95—138为多特信经。PDF物理页比这些印页少1页。三项联合信条以附件为底本，三份普世信经以网站正文为阅读版；未上传整部PDF。</li><li><b>CCI核对与延伸</b>：<a href="https://ccifellowship.org/books/book-of-praise">敬拜手册与版权页</a> · <a href="https://ccifellowship.org/books/book-of-praise/creeds/apostles-creed">使徒信经</a> · <a href="https://ccifellowship.org/books/book-of-praise/creeds/nicene-creed">尼西亚信经</a> · <a href="https://ccifellowship.org/books/book-of-praise/creeds/athanasian-creed">亚他那修信经</a> · <a href="https://ccifellowship.org/books/book-of-praise/confessions/canons-of-dort">多特信经介绍</a> · <a href="https://ccifellowship.org/books/book-of-praise/confessions/heidelberg-catechism">海德堡介绍</a>。网站部分页面直接访问超时；未能遍历全站，不能声称吸收“所有内容”。</li><li><b>CCI的解释材料</b>：<a href="https://ccifellowship.org/sermons/heidelberg-catechism/lord-day-20">主日20：圣灵的工作</a>帮助联结圣道与圣灵；<a href="https://ccifellowship.org/index.php/books/book-of-praise/liturgical-forms/4">圣餐仪文</a>将赎罪、圣约、确据与相交连在一起。本文吸收主题联系，未冒称其解释为信条正文。</li><li><b>欧陆改革宗交叉核验</b>：<a href="https://canrc.org/canons-of-dort">CanRC多特全文</a> · <a href="https://canrc.org/the-belgic-confession">比利时信条</a> · <a href="https://canrc.org/heidelberg-catechism">海德堡</a> · <a href="https://canrc.org/history">CanRC历史</a> · <a href="https://www.urcna.org/canons">URCNA多特文本入口</a>。这些用来核对结构和提供阅读路径；本站中文译文不混用这些英文版本。</li><li><b>真实历史</b>：<a href="https://www.hofvannederland.nl/collectie/synode-van-dordrecht/">Hof van Nederland大会馆藏</a> · <a href="https://collecties.kb.nl/en/collections/friendship-books/celebrities-friendship-books/album-amicorum-johannes-rufelaert">荷兰国家图书馆大会签名册</a> · <a href="https://www.nationaalarchief.nl/beleven/nieuws/johan-van-oldenbarnevelt-1619">国家档案馆政治背景</a>。历史不应只据某一阵营的简写来讲述。</li><li><b>中文教会实践</b>：<a href="https://www.ccreformed.org/">洛杉矶改革宗恩约教会</a>公开说明三项联合认信及圣约式敬拜，作为当代处境参考。</li><li><b>延伸资源，不表示已全文审读</b>：<a href="https://www.reformedbeginner.net/">改革宗初学者</a> · <a href="https://heritagereformed.com/">Heritage Reformed</a> · <a href="https://www.prca.org/">PRCA</a> · <a href="https://opc.org/">OPC</a> · <a href="https://canadianreformedseminary.ca/">Canadian Reformed Seminary</a> · <a href="https://crts.edu/">CRTS</a> · <a href="https://www.wts.edu/">Westminster</a>。这些机构不必在每项问题上拥有相同结论。</li></ol><div class="note"><b>关于“一字不差”</b>：三份普世信经按已读取的CCI网页正文录入；三项联合信条完成附件底本重排和全条目释义，尚不能称为CCI全站逐字校定版。疑似来源错字保留，不擅自用其他译本覆盖。若后续取得网站可核验完整文本，可制作字符级差异清单并发布v1.1校订版。全文状态如实标明，比提供未经核验的“精确原文”更可靠。</div>''')
nav=''.join(f'<a href="#{id}"><span>{i+1:02}</span>{title}</a>' for i,(id,title) in enumerate(sections))
template='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="多特信经完整研读：59条教义、34项驳谬、圣经与圣约、历史地图、三项联合信条对比及六份净读文本。"><meta name="theme-color" content="#123c3b"><title>恩典的全景 · 多特信经深度研读</title><link rel="stylesheet" href="style.css"></head><body><div id="progress"></div><header class="topbar"><a class="brand" href="#top">✦ <span>恩典的全景<small>DORT · 1618—1619</small></span></a><div class="tools"><button id="menu" aria-expanded="false" aria-controls="toc">☰ 目录</button><a class="button" href="#library">📖 净读</a><button id="theme" aria-label="切换深浅主题">◐</button><button id="print">打印</button></div></header><aside id="toc" inert><div class="tochead"><b>研读目录</b><button id="closeMenu" aria-label="关闭目录">×</button></div><label>搜索条文与释义<input id="search" type="search" placeholder="如：确据、圣约、I.17"></label><p id="searchStatus" aria-live="polite"></p>__NAV__</aside><div id="shade" hidden></div><main id="top"><section class="hero"><div class="hero-copy"><div class="eyebrow">CONTINENTAL REFORMED · STUDY ATLAS</div><h1>恩典的全景<span>《多特信经》深度研读</span></h1><p>从整本圣经进入，沿着历史与圣约前行。<br>看见救恩的源头、成就、施行与终局。</p><div class="hero-actions"><a class="primary button" href="#vision">开始研读 ↗</a><a class="button" href="#memory">✧ 进入记忆练习</a></div><div class="hero-stats"><div><strong>59</strong><span>教义条文</span></div><div><strong>34</strong><span>驳谬辨析</span></div><div><strong>06</strong><span>净读文本</span></div></div></div><div class="hero-art" aria-label="救恩的四重主题"><div class="orbit orbit1"></div><div class="orbit orbit2"></div><div class="art-center">✝<span>在基督里</span></div><b class="orb o1">父的旨意<small>拣选</small></b><b class="orb o2">子的救赎<small>成就</small></b><b class="orb o3">灵的更新<small>施行</small></b><b class="orb o4">约的信实<small>保守</small></b><small class="art-note">源于恩典 · 归于荣耀</small></div></section><div class="readingbar"><span>✦ 先总览 · 再逐条 · 最后记忆与实践</span><span>2026.10.21 / v1.0</span></div>__BODY__<footer><b>恩典的全景</b><p>读懂教义，为了更真实地敬拜、信靠与爱。</p><p>多特信经 · 20261021 · v1 · GTstudy</p><a href="#top">回到顶部 ↑</a></footer></main><button id="backTop" aria-label="回到顶部">↑</button><script src="app.js"></script></body></html>'''
(OUT/'index.html').write_text(template.replace('__NAV__',nav).replace('__BODY__',body),encoding='utf8')
print(json.dumps({'articles':59,'errors':34,'reader_pages':6,'sections':len(sections),'characters':len(body),'commentary_ready':bool(notes)},ensure_ascii=False))
