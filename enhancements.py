"""v1.1: geography, source-backed cultural context, native reading tools."""
from pathlib import Path
import re,json,html
E=html.escape
ROOT=Path(__file__).resolve().parent
PLACES=[
 {'id':'dordrecht','name':'多德雷赫特','latin':'Dordrecht','lat':51.8133,'lon':4.6901,'icon':'⚓','year':'1618—1619','role':'河港 · 代表会议','core':'谁在救恩中作决定性的工作？','x':352,'y':188},
 {'id':'leiden','name':'莱顿','latin':'Leiden','lat':52.1601,'lon':4.4970,'icon':'🎓','year':'1575 / 1603','role':'大学 · 牧者培养','core':'课堂中的释经，终会进入讲台与人的良心。','x':348,'y':135},
 {'id':'the-hague','name':'海牙','latin':'Den Haag','lat':52.0705,'lon':4.3007,'icon':'⚖','year':'1618—1619','role':'省权 · 联省权力','core':'政治解释会议处境，不能替代圣经论证。','x':290,'y':159},
 {'id':'southern-netherlands','name':'安特卫普','latin':'Antwerpen','lat':51.2194,'lon':4.4025,'icon':'📚','year':'1561 / 1585','role':'流亡 · 印刷网络','core':'人带着教会关系迁移，书带着认信跨境。','x':342,'y':280},
 {'id':'heidelberg','name':'海德堡','latin':'Heidelberg','lat':49.3988,'lon':8.6724,'icon':'🏡','year':'1563','role':'学校 · 家庭教理','core':'教理问答让共同信仰成为反复学习的语言。','x':596,'y':359},
 {'id':'geneva','name':'日内瓦','latin':'Genève','lat':46.2044,'lon':6.1432,'icon':'♪','year':'1536 / 1562','role':'难民 · 诗篇歌唱','core':'共同的书与歌，连接分散的信仰群体。','x':438,'y':478}
]
def concept():
    nodes=''
    for p in PLACES:
        x,y=p['x'],p['y'];nodes+=f'<g class="map-node" data-place="{p["id"]}" tabindex="0" role="button" aria-label="选择{p["name"]}" aria-pressed="false"><circle class="node-halo" cx="{x}" cy="{y}" r="20"/><circle class="node-dot" cx="{x}" cy="{y}" r="8"/><text x="{x+16}" y="{y+6}">{p["name"]}</text></g>'
    return '''<svg class="concept-map" viewBox="0 0 780 540" role="group" aria-label="西欧思想网络示意图，节点可选择；位置为示意，不用于测量"><defs><pattern id="sea-grid" width="36" height="36" patternUnits="userSpaceOnUse"><path d="M36 0H0V36" fill="none" stroke="#fff" stroke-opacity=".06"/></pattern><linearGradient id="sea" x2="1" y2="1"><stop stop-color="#153f53"/><stop offset="1" stop-color="#235e68"/></linearGradient></defs><rect width="780" height="540" rx="24" fill="url(#sea)"/><rect width="780" height="540" fill="url(#sea-grid)"/><path class="land" d="M154 45L188 74 175 111 206 143 196 180 227 209 216 248 173 270 126 245 142 212 123 180 146 140 136 97Z M81 120L112 132 100 190 75 215 55 183Z M365 20L405 62 392 105 428 134 483 119 505 150 562 165 624 193 675 228 727 278 766 313 766 520 534 520 482 476 433 463 358 472 310 426 278 371 253 325 288 283 319 269 328 224 342 181 355 148 347 111Z"/><g class="network-lines" fill="none" stroke-width="2"><path d="M438 478Q410 310 352 188"/><path d="M596 359Q454 330 342 280Q340 230 352 188"/><path d="M290 159Q312 168 352 188L348 135"/></g><text x="166" y="314" class="sea-label">北 海</text><text x="49" y="395" class="sea-label">大 西 洋</text>'''+nodes+'''<g class="map-key"><circle cx="29" cy="504" r="5"/><text x="43" y="509">节点示意 · 连线表示思想网络，非实测行程或1618年国界</text></g></svg>'''
def atlas_component():
    return '''<div class="atlas-intro"><p class="lead"><strong>河港使代表相聚，大学使争论扩散，印刷使告白跨境。</strong>文化说明真理如何被传递；圣经决定所传的是否为真。</p><div class="map-legend"><span>🔵 蓝：地点与史料</span><span>🟠 橙：制度与冲突</span><span>🟢 绿：信条与生活</span></div></div><div class="atlas-workbench"><article class="atlas-panel"><div class="panel-caption"><span>✧ 思想网络 / 无需联网</span><small>点击节点联动定位</small></div>'''+concept()+'''<div class="place-pills" aria-label="选择历史地点">'''+''.join(f'<button data-place="{p["id"]}" aria-pressed="false">{p["icon"]} {p["name"]}</button>' for p in PLACES)+'''</div></article><article class="atlas-panel live-panel"><div class="panel-caption"><span>◎ 今日地理 / 在线底图</span><button class="tiny" id="map-load">载入地图</button></div><div class="map-toolbar"><label>底图<select id="map-provider"><option value="imagery">Esri 卫星影像</option><option value="topo">Esri 地形街道</option><option value="opentopo">OpenTopoMap 备用</option></select></label><button id="map-overview" class="tiny">⌖ 西欧全景</button></div><div id="live-map" class="live-map" role="region" aria-label="可交互的现代地理地图"><div class="map-placeholder"><span>🌍</span><b>与历史节点对照今日地理</b><p>靠近此处时按需载入；双指缩放，拖动探索。</p></div></div><p id="map-status" class="map-status" role="status">尚未请求在线底图。示意图始终可用。</p><div id="map-external" class="map-external"></div><small class="map-disclosure">在线底图不是1618年疆界；卫星影像并非实时拍摄。底图服务受当地网络影响，可切换来源。</small></article></div><article id="place-detail" class="place-detail" aria-live="polite"></article><script id="atlas-data" type="application/json">'''+json.dumps(PLACES,ensure_ascii=False)+'''</script>'''
def cultures(data):
    blocks=''
    for p in data['places']:
        src=' · '.join(f'<a href="{E(s["url"])}" target="_blank" rel="noopener">{E(s["title"])} ↗</a>' for s in p['sources'])
        blocks+=f'<article class="culture-card" id="culture-{p["id"]}"><h3>{E(p["title"])}</h3><p><span class="fact-label">史实</span>{E(p["fact"])}</p><p class="culture-meaning"><span class="meaning-label">要点</span>{E(p["interpretation"])}</p><div class="source">{src}</div></article>'
    return '<div class="culture-grid">'+blocks+'</div>'
def story(data):
    return '<div class="cause-grid">'+''.join(f'<article><span class="cause-no">0{x["step"]}</span><h3>{E(x["label"])}</h3><p>{E(x["text"])}</p></article>' for x in data['causalStory'])+'</div>'
def enhance(out):
    data=json.loads((ROOT/'history-culture.json').read_text(encoding='utf8'))
    p=out/'index.html';s=p.read_text(encoding='utf8')
    geo='<section id="geography"><div class="eyebrow">04 / HISTORY · MAPS · CULTURE</div><h2>从地图看见信仰的真实处境</h2>'+atlas_component()+'''<div class="atlas-link"><span>从“在哪里”继续追问“为什么”</span><a class="button primary" href="atlas.html">展开历史文化图谱 ↗</a></div><h3>四个环节，读懂一条因果线</h3>'''+story(data)+'''<div class="core-distinction"><b>关键分辨</b><span>地理与制度 → 解释传播和争议的处境</span><span>圣经与认信 → 检验教义主张的真伪</span></div></section>'''
    s=re.sub(r'<section id="geography">.*?</section>',lambda m:geo,s,flags=re.S)
    # Emphasis belongs to the commentary only, never the confession text.
    def emphasize(m):
        text=m.group(1);stop=text.find('。');end=stop+1 if 0<=stop<=65 else text.find('；')+1
        if end>0:text='<strong class="core-sentence">'+text[:end]+'</strong>'+text[end:]
        return '<div class="interpretation"><span class="tag">释义</span><p>'+text+'</p>'
    s=re.sub(r'<div class="interpretation"><span class="tag">释义</span><p>(.*?)</p>',emphasize,s)
    recalls={'I':'拣选是信心的源头；信心不是神拣选我的功德条件。','II':'十架价值无限，救赎实际成就，福音向万人真诚宣告。','IIIIV':'人不能自救；圣灵更新意志，使人甘心而真实地相信。','V':'神保守人，因此人真实坚忍；圣道、警告与圣礼都是途径。'}
    for key,text in recalls.items():
        s=re.sub(fr'(<section id="head-{key}">.*?</h2>)',lambda m:m.group(1)+f'<div class="chapter-core"><span>✦ 一句抓核心</span><p>{text}</p></div>',s,count=1,flags=re.S)
    s=s.replace('<link rel="stylesheet" href="style.css">','<link rel="stylesheet" href="style.css"><link rel="stylesheet" href="study.css">')
    s=s.replace('<script src="app.js"></script>','<script src="app.js" defer></script><script src="study.js" defer></script><script src="maps.js" defer></script>')
    s=s.replace('2026.10.21 / v1.0','2026.10.24 / v1.1').replace('v1.0 · 多特信经-20261021-v1-GTstudy','v1.1 · 多特信经-20261024-v1.1-GTstudy').replace('编写日期：<time>2026-10-21（Asia/Taipei）</time>','更新日期：<time>2026-10-24（Asia/Taipei）</time>')
    s=s.replace('<a class="button" href="#library">📖 净读</a>','<a class="button" href="atlas.html">🌍 图谱</a><a class="button" href="#library">📖 净读</a>')
    s=s.replace('class="hero-stats"','class="hero-stats"').replace('<button id="backTop" aria-label="回到顶部">↑</button>','')
    s=s.replace('</aside>','<a href="atlas.html"><span>↗</span>历史文化独立图谱</a></aside>',1)
    s=s.replace('20261021 · v1 · GTstudy','20261024 · v1.1 · GTstudy')
    s=s.replace('<h3>七日学习路径</h3>','<div class="note"><b>重点标记怎么用？</b>划选正文，可选核心金、应用绿、经文蓝、难点粉，或用加粗、实线、虚线、区块。手机上也可从右下角展开“标记”，再点按整段。旁注自动保存；进入“笔记”可定位、导出与导入。</div><h3>七日学习路径</h3>')
    p.write_text(s,encoding='utf8')
    # Atlas is a separate destination: the long reading page stays focused.
    dates=[x for x in data['dates'] if x['date'] in ['1563','1575-02-08','1585-08-13','1603','1610','1618-11-13','1619-05-06','1619-05-13','1637']]
    chronology='<div class="date-ribbon">'+''.join(f'<article><b>{E(x["date"])}</b><p>{E(x["event"])}</p><a href="{E(x["source"])}" target="_blank" rel="noopener">核对史料 ↗</a></article>' for x in dates)+'</div>'
    atlas='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#173d3b"><title>历史文化图谱 · 多特信经</title><link rel="stylesheet" href="style.css"><link rel="stylesheet" href="study.css"></head><body class="atlas-page"><div id="progress"></div><header class="topbar"><a class="brand" href="index.html">✦ <span>恩典的全景<small>历史 · 地图 · 文化</small></span></a><div class="tools"><a class="button" href="index.html#geography">← 返回研读</a><button data-open-notebook aria-label="打开笔记">▧ 笔记</button></div></header><main><section class="atlas-heading"><div class="eyebrow">THE PLACES BEHIND THE WORDS</div><h1>信仰有历史，<br>文字有来处。</h1><p class="lead">六座城市，四种制度，一份共同的告白。<br>把地点、事件和神学问题连成可以记住的图谱。</p><nav class="atlas-tabs"><a href="#atlas-explore">◎ 双地图</a><a href="#culture">📚 六城文化</a><a href="#causes">↗ 因果图</a><a href="#atlas-dates">◷ 关键时刻</a></nav></section><section id="atlas-explore"><div class="eyebrow">01 / EXPLORE</div><h2>一张思想网络，一张真实地理</h2>'''+atlas_component()+'''<div class="tour-controls"><button id="tour-play">▷ 播放思想路线</button><button id="tour-stop">Ⅱ 暂停</button><span id="tour-state" role="status">按节点逐城阅读，不把示意连线当作历史行程。</span></div></section><section id="culture"><div class="eyebrow">02 / CULTURAL CONTEXT</div><h2>文化如何进入讲台与人的良心</h2>'''+cultures(data)+'''<div class="note"><b>读背景，守边界。</b>不把印刷所一概称为改革宗据点，不把政治支持当作教义正确的证明，也不把1685年后的难民浪潮倒放进1618年的故事。</div></section><section id="causes"><div class="eyebrow">03 / CAUSE & CONSEQUENCE</div><h2>从场所到用途，抓住四个环节</h2>'''+story(data)+'''<div class="core-distinction"><b>从大处看</b><span>共同信仰 → 教理教育 → 争议裁决 → 会众安慰</span><span>三份信条各有任务；多特不是整部神学的替代品。</span></div></section><section id="atlas-dates"><div class="eyebrow">04 / CRITICAL MOMENTS</div><h2>少记日期，多记转折</h2>'''+chronology+'''<p class="source">日期注意：国际代表议程和本国后续会议须区分。整场会议在1619年5月结束；不同馆藏简介的结束日记载有差异。信经公开宣读、会议结束、海牙处决是三个不同事件。</p></section><section id="atlas-recall"><div class="eyebrow">05 / REMEMBER</div><h2>六城，六个记忆钩</h2><div class="memory-hooks">'''+''.join(f'<article><span>{p["icon"]}</span><h3>{p["name"]}</h3><b>{p["role"]}</b><p>{p["core"]}</p></article>' for p in PLACES)+'''</div><a class="button primary" href="index.html#head-I">带着背景，进入条文 ↗</a></section><footer><b>历史帮助定位，圣经决定真理。</b><p>v1.1 · 2026-10-24 · 史实与解释分栏，来源逐项可查。</p><a href="index.html">返回研读主页</a></footer></main><script src="study.js" defer></script><script src="maps.js" defer></script></body></html>'''
    (out/'atlas.html').write_text(atlas,encoding='utf8')
    (out/'atlas-context.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf8')
    for name in ['apostles','nicene','athanasian','belgic','heidelberg','dort']:
        p=out/(name+'.html');s=p.read_text(encoding='utf8');s=s.replace('<link rel="stylesheet" href="style.css">','<link rel="stylesheet" href="style.css"><link rel="stylesheet" href="study.css">');s=s.replace('<script src="reader.js"></script>','<script src="reader.js" defer></script><script src="study.js" defer></script>');p.write_text(s,encoding='utf8')
    for p in out.glob('*.html'):
        s=p.read_text(encoding='utf8')
        s=re.sub(r'((?:src|href)="[a-z-]+\.(?:css|js))"',r'\1?v=20261024.1"',s)
        p.write_text(s,encoding='utf8')
