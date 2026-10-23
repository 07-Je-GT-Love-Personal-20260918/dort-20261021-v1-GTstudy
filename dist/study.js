/* Shared native reading navigation and local annotations; no third-party code. */
(()=>{'use strict';
 const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)],body=document.body;
 const reduced=matchMedia('(prefers-reduced-motion: reduce)'),page=location.pathname.split('/').pop()||'index.html',KEY='dort-annotations-v2';
 const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const get=(k,fallback)=>{try{return JSON.parse(localStorage.getItem(k))??fallback}catch{return fallback}};
 const put=(k,v)=>{try{localStorage.setItem(k,JSON.stringify(v));return true}catch{return false}};
 function toast(text){$('#study-toast').textContent=text;$('#study-toast').classList.add('visible');clearTimeout(toast.timer);toast.timer=setTimeout(()=>$('#study-toast').classList.remove('visible'),3400)}
 const icons={back:'M14 5l-7 7 7 7',forward:'M10 5l7 7-7 7',top:'M5 5h14M7 14l5-5 5 5M12 9v12',bottom:'M5 19h14M7 10l5 5 5-5M12 3v12',home:'M3 11l9-8 9 8M6 10v11h12V10M10 21v-7h4v7',notes:'M5 3h14v18H5zM8 7h8M8 11h8M8 15h4',mark:'M4 16l10-12 6 5-10 12H4zM3 22h18',more:'M5 12h.01M12 12h.01M19 12h.01'};
 const svg=k=>`<svg viewBox="0 0 24 24" aria-hidden="true"><path d="${icons[k]}"/></svg>`;
 body.insertAdjacentHTML('beforeend',`<div id="study-toast" role="status" aria-live="polite"></div><nav class="reading-dock" aria-label="阅读快捷导航"><div class="dock-extra" id="dock-extra" hidden><button data-nav="back" title="返回上一页" aria-label="返回上一页">${svg('back')}<span>返回</span></button><button data-nav="forward" title="前进一页" aria-label="前进一页">${svg('forward')}<span>前进</span></button><a href="index.html" title="研读主页" aria-label="研读主页">${svg('home')}<span>主页</span></a><a href="atlas.html" title="历史文化图谱" aria-label="历史文化图谱">◎<span>图谱</span></a><button data-nav="mark" title="开启段落标记模式" aria-label="开启段落标记模式" aria-pressed="false">${svg('mark')}<span>标记</span></button><button data-open-notebook title="我的笔记" aria-label="我的笔记">${svg('notes')}<span>笔记</span></button></div><div class="dock-rail"><button data-nav="top" title="到页面顶部" aria-label="到页面顶部">${svg('top')}</button><button id="dock-toggle" title="展开阅读导航" aria-label="展开阅读导航" aria-expanded="false" aria-controls="dock-extra">${svg('more')}</button><button data-nav="bottom" title="到页面底部" aria-label="到页面底部">${svg('bottom')}</button></div></nav><div id="annotation-toolbar" class="annotation-toolbar" role="dialog" aria-label="文字重点标记" hidden><div class="annotation-title"><span id="annotation-caption">标记选中文字</span><button id="annotation-close" aria-label="关闭标记工具">×</button></div><div class="annotation-styles"><button data-style="yellow" class="swatch yellow" aria-label="金色底纹" title="金色：核心">核</button><button data-style="green" class="swatch green" aria-label="绿色底纹" title="绿色：应用">用</button><button data-style="blue" class="swatch blue" aria-label="蓝色字体" title="蓝色：经文联系">经</button><button data-style="rose" class="swatch rose" aria-label="玫红底纹" title="玫红：难点">疑</button><button data-style="underline" class="swatch underline" aria-label="橙色实线" title="橙色实线">实线</button><button data-style="dashed" class="swatch dashed" aria-label="紫色虚线" title="紫色虚线">虚线</button><button data-style="bold" class="swatch bold" aria-label="加粗标记" title="加粗">B</button><button data-style="block" class="swatch block" aria-label="绿色区块" title="绿色区块">区块</button></div><label class="annotation-note-label">旁注（可选）<input id="annotation-note" maxlength="2000" placeholder="为什么重要？与哪节经文相连？"></label><div class="annotation-actions"><button id="annotation-save-note">仅保存旁注</button><button id="annotation-notebook">查看笔记</button></div></div><div id="notebook-shade" hidden></div><aside id="study-notebook" class="study-notebook" role="dialog" aria-modal="true" aria-label="我的研读笔记" inert><header><div><small>MY READING NOTES</small><h2>留下理解的痕迹</h2></div><button id="notebook-close" aria-label="关闭笔记">×</button></header><p class="notebook-help">划选正文可直接标记；开启“标记模式”后，也可点按整段。自动保存在此浏览器，不上传。</p><div class="notebook-filters"><label>范围<select id="notebook-scope"><option value="all">全部页面</option><option value="page">当前页面</option></select></label><label>查找<input id="notebook-search" type="search" placeholder="原句或旁注"></label></div><div class="notebook-actions"><button id="notes-export-json">备份 JSON</button><button id="notes-export-md">导出 Markdown</button><label class="button" for="notes-import">导入备份</label><input id="notes-import" type="file" accept="application/json,.json" hidden></div><p id="notebook-summary" role="status"></p><div id="notebook-list"></div><footer>不同域名、浏览器的笔记不会自动互通。可用“备份 JSON → 导入备份”迁移；旧版自由笔记仍保留于主页。</footer></aside>`);
 if(!$('#theme')){try{if(localStorage.getItem('dort-theme')==='dark')body.classList.add('dark')}catch{}}
 let dockOpen=false;
 $('#dock-toggle').onclick=()=>{dockOpen=!dockOpen;$('#dock-extra').hidden=!dockOpen;$('#dock-toggle').setAttribute('aria-expanded',String(dockOpen))};
 function closeDock(){dockOpen=false;$('#dock-extra').hidden=true;$('#dock-toggle').setAttribute('aria-expanded','false')}
 $$('[data-nav]').forEach(b=>b.onclick=()=>{
  const a=b.dataset.nav,behavior=reduced.matches?'instant':'smooth';
  if(a==='top')window.scrollTo({top:0,behavior});
  if(a==='bottom')window.scrollTo({top:document.documentElement.scrollHeight,behavior});
  if(a==='back'){if(history.length>1)history.back();else location.href='index.html'}
  if(a==='forward')history.forward();
  if(a==='mark'){const on=body.classList.toggle('annot-mode');b.setAttribute('aria-pressed',String(on));b.setAttribute('aria-label',on?'关闭段落标记模式':'开启段落标记模式');toast(on?'标记模式已开启：点按正文段落，或划选一段文字。':'已退出段落标记模式');closeDock()}
 });
 const allowed=new Set(['yellow','green','blue','rose','underline','dashed','bold','block','note']);
 let records=get(KEY,[]);if(!Array.isArray(records))records=[];
 records=records.filter(x=>x&&typeof x.id==='string'&&typeof x.block==='string'&&typeof x.quote==='string'&&allowed.has(x.style));
 const blocks=new Map(),duplicates=new Map();
 const hash=s=>{let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return (h>>>0).toString(36)};
 const candidates=$$('main p, main li').filter(el=>!el.querySelector('p')&&!el.closest('.live-panel,.source,.notebook-list')&&el.textContent.trim().length>=8);
 candidates.forEach((el,i)=>{const h=hash(el.textContent),occurrence=duplicates.get(h)||0;duplicates.set(h,occurrence+1);const id=`read-${h}-${occurrence}`;el.dataset.annotBlock=id;if(!el.id)el.id=id;el.tabIndex=-1;blocks.set(id,el)});
 function unwrap(el){el.querySelectorAll('mark[data-user-mark]').forEach(m=>m.replaceWith(...m.childNodes));el.normalize();el.classList.remove('has-user-note','has-block-mark');delete el.dataset.noteCount}
 function wrapOffsets(el,start,end,style,id){
  const walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);let n,offset=0,parts=[];
  while((n=walker.nextNode())){const next=offset+n.length;if(next>start&&offset<end)parts.push({n,start:Math.max(0,start-offset),end:Math.min(n.length,end-offset)});offset=next}
  parts.reverse().forEach(p=>{const range=document.createRange();range.setStart(p.n,p.start);range.setEnd(p.n,p.end);const mark=document.createElement('mark');mark.dataset.userMark=id;mark.className='user-mark user-'+style;range.surroundContents(mark)})
 }
 function renderBlock(id){const el=blocks.get(id);if(!el)return;unwrap(el);const rs=records.filter(r=>r.page===page&&r.block===id);let count=0;rs.forEach(r=>{if(el.textContent.slice(r.start,r.end)!==r.quote)return;if(r.style!=='note')wrapOffsets(el,r.start,r.end,r.style,r.id);if(r.note)count++;if(r.style==='block')el.classList.add('has-block-mark')});if(count){el.classList.add('has-user-note');el.dataset.noteCount=String(count)}}
 function renderAll(){for(const id of blocks.keys())if(records.some(r=>r.page===page&&r.block===id))renderBlock(id)}
 renderAll();let pending=null,lastFocused=null;
 function hideToolbar(){$('#annotation-toolbar').hidden=true;pending=null;body.classList.remove('annotation-active')}
 function showToolbar(p){pending=p;$('#annotation-toolbar').hidden=false;body.classList.add('annotation-active');$('#annotation-caption').textContent=(p.whole?'整段标记 · ':'已选文字 · ')+p.quote.slice(0,24)+(p.quote.length>24?'…':'');$('#annotation-note').value=''}
 function selection(){
  const sel=window.getSelection();if(!sel||sel.isCollapsed||!sel.rangeCount)return;
  const range=sel.getRangeAt(0),node=range.commonAncestorContainer,el=(node.nodeType===1?node:node.parentElement)?.closest('[data-annot-block]');
  if(!el||!el.contains(range.startContainer)||!el.contains(range.endContainer))return;
  const prefix=document.createRange();prefix.selectNodeContents(el);prefix.setEnd(range.startContainer,range.startOffset);const start=prefix.toString().length,quote=range.toString();if(!quote.trim()||quote.length>6000)return;
  showToolbar({block:el.dataset.annotBlock,start,end:start+quote.length,quote,whole:false});
 }
 let selectionTimer;document.addEventListener('selectionchange',()=>{if(document.activeElement?.closest('#annotation-toolbar,#study-notebook'))return;clearTimeout(selectionTimer);selectionTimer=setTimeout(selection,180)});
 document.addEventListener('pointerup',e=>{if(!e.target.closest('#annotation-toolbar,#study-notebook'))setTimeout(selection,10)});
 document.querySelector('main')?.addEventListener('click',e=>{if(!body.classList.contains('annot-mode')||e.target.closest('a,button,summary,select,input,textarea,.live-map'))return;const el=e.target.closest('[data-annot-block]');if(!el||window.getSelection()?.toString().trim())return;showToolbar({block:el.dataset.annotBlock,start:0,end:el.textContent.length,quote:el.textContent,whole:true})});
 $('#annotation-toolbar').addEventListener('pointerdown',e=>{if(e.target.closest('button'))e.preventDefault()});
 function save(style){
  if(!pending)return;const p=pending,note=$('#annotation-note').value.trim();if(style==='note'&&!note){$('#annotation-note').focus();return}
  const removed=records.filter(r=>r.page===page&&r.block===p.block&&r.start<p.end&&r.end>p.start);
  records=records.filter(r=>!removed.includes(r));
  const text=blocks.get(p.block).textContent;
  removed.forEach(r=>{
   if(r.start<p.start)records.push({...r,id:r.id+'-l',end:p.start,quote:text.slice(r.start,p.start)});
   if(r.end>p.end)records.push({...r,id:r.id+'-r',start:p.end,quote:text.slice(p.end,r.end),note:r.start<p.start?'':r.note});
  });
  const keptNote=note||removed.filter(r=>r.start>=p.start&&r.end<=p.end).map(r=>r.note).filter(Boolean).join('\n');
  records.push({id:crypto.randomUUID?crypto.randomUUID():Date.now().toString(36)+Math.random().toString(36).slice(2),page,title:document.title,block:p.block,start:p.start,end:p.end,quote:p.quote,style,note:keptNote,created:new Date().toISOString()});
  const stored=put(KEY,records);renderBlock(p.block);hideToolbar();window.getSelection()?.removeAllRanges();toast(stored?'重点已保存。可在右下角“笔记”中回看。':'已标记，但此浏览器暂无法持久保存，请导出备份。');if($('#study-notebook').classList.contains('open'))renderNotebook()
 }
 $$('[data-style]').forEach(b=>b.onclick=()=>save(b.dataset.style));$('#annotation-save-note').onclick=()=>save('note');$('#annotation-close').onclick=hideToolbar;
 function renderNotebook(){
  const scope=$('#notebook-scope').value,q=$('#notebook-search').value.trim().toLowerCase();const rows=records.filter(r=>(scope==='all'||r.page===page)&&(!q||(r.quote+' '+r.note+' '+r.title).toLowerCase().includes(q))).slice().reverse();
  $('#notebook-summary').textContent=`共 ${records.length} 条笔记 · 当前显示 ${rows.length} 条`;
  const list=$('#notebook-list');list.replaceChildren();if(!rows.length){list.innerHTML='<div class="notes-empty">✧<h3>读到心里，也记在这里</h3><p>在正文划选文字，选择底纹、字体或线条；也可开启标记模式后点按整段。</p></div>';return}
  rows.forEach(r=>{const article=document.createElement('article');article.className='saved-note';article.innerHTML=`<small>${escape(r.title)} · <span class="note-type type-${r.style}">${escape({yellow:'核心',green:'应用',blue:'经文',rose:'难点',underline:'实线',dashed:'虚线',bold:'加粗',block:'区块',note:'旁注'}[r.style])}</span></small><blockquote>${escape(r.quote)}</blockquote>${r.note?'<p class="saved-note-text">'+escape(r.note)+'</p>':''}<div><button data-jump>定位原文 ↗</button><button data-delete aria-label="删除这条笔记">移除</button></div>`;
   article.querySelector('[data-jump]').onclick=()=>{closeNotebook();if(r.page!==page){location.href=r.page+'#'+encodeURIComponent(r.block);return}jump(r.block)};
   article.querySelector('[data-delete]').onclick=()=>{records=records.filter(x=>x.id!==r.id);put(KEY,records);renderBlock(r.block);renderNotebook();toast('已移除此条标记。')};list.append(article)
  })
 }
 function openNotebook(){lastFocused=document.activeElement;hideToolbar();closeDock();$('#study-notebook').classList.add('open');$('#study-notebook').inert=false;$('#notebook-shade').hidden=false;body.classList.add('notebook-open');renderNotebook();$('#notebook-close').focus()}
 function closeNotebook(){$('#study-notebook').classList.remove('open');$('#study-notebook').inert=true;$('#notebook-shade').hidden=true;body.classList.remove('notebook-open');lastFocused?.focus?.()}
 $$('[data-open-notebook]').forEach(b=>b.onclick=openNotebook);$('#annotation-notebook').onclick=openNotebook;$('#notebook-close').onclick=closeNotebook;$('#notebook-shade').onclick=closeNotebook;$('#notebook-search').oninput=renderNotebook;$('#notebook-scope').onchange=renderNotebook;
 function download(name,content,type){const url=URL.createObjectURL(new Blob([content],{type})),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1500)}
 $('#notes-export-json').onclick=()=>{let legacy='';try{legacy=localStorage.getItem('dort-notes')||''}catch{}download('多特研读-笔记备份.json',JSON.stringify({format:'dort-study-notes',version:2,exported:new Date().toISOString(),annotations:records,legacyNotes:legacy},null,2),'application/json')};
 $('#notes-export-md').onclick=()=>download('多特研读-重点笔记.md','# 多特信经 · 我的重点笔记\n\n'+records.map(r=>`## ${r.title}\n\n> ${r.quote.replace(/\n/g,'\n> ')}\n\n${r.note||''}\n\n[定位原文](${r.page}#${r.block})\n`).join('\n'),'text/markdown;charset=utf-8');
 $('#notes-import').onchange=async e=>{
  const file=e.target.files[0];if(!file)return;
  try{if(file.size>4*1024*1024)throw Error('size');const data=JSON.parse(await file.text());if(data.format!=='dort-study-notes'||!Array.isArray(data.annotations))throw Error('format');const valid=data.annotations.filter(r=>r&&typeof r.id==='string'&&r.id.length<160&&/^(index|atlas|apostles|nicene|athanasian|belgic|heidelberg|dort)\.html$/.test(r.page)&&/^read-[a-z0-9]+-\d+$/.test(r.block)&&typeof r.quote==='string'&&r.quote.length<=6000&&typeof r.note==='string'&&r.note.length<=2000&&Number.isInteger(r.start)&&Number.isInteger(r.end)&&r.start>=0&&r.end>r.start&&r.end-r.start===r.quote.length&&allowed.has(r.style));const before=records.slice();let n=0;valid.forEach(r=>{if(!records.some(x=>x.id===r.id)){records.push({...r,title:String(r.title||'研读笔记').slice(0,180)});n++}});if(!put(KEY,records)){records=before;throw Error('storage')}if(typeof data.legacyNotes==='string'&&data.legacyNotes.trim()){try{const old=localStorage.getItem('dort-notes')||'',incoming=data.legacyNotes.slice(0,200000);if(!old.includes(incoming)){const merged=old?old+'\n\n--- Imported notes ---\n'+incoming:incoming;localStorage.setItem('dort-notes',merged);document.querySelectorAll('textarea').forEach(box=>{if(box.id==='personalNotes')box.value=merged})}}catch{}}renderAll();renderNotebook();toast(`已合并 ${n} 条笔记；现有笔记保留。`)}catch{toast('未能导入。请使用本站导出的 JSON 备份文件（不超过4MB）。')}finally{e.target.value=''}
 };
 function jump(id){const el=blocks.get(id);if(!el){toast('此处文字可能已修订；原句仍保存在笔记中。');return}el.closest('details')?.setAttribute('open','');el.scrollIntoView({behavior:reduced.matches?'instant':'smooth',block:'center'});el.classList.add('note-jump');setTimeout(()=>el.classList.remove('note-jump'),1800)}
 if(location.hash.startsWith('#read-'))setTimeout(()=>jump(decodeURIComponent(location.hash.slice(1))),120);
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){hideToolbar();closeDock();if($('#study-notebook').classList.contains('open'))closeNotebook()}if(e.key==='Tab'&&$('#study-notebook').classList.contains('open')){const f=$$('#study-notebook button,#study-notebook input:not([hidden]),#study-notebook select,#study-notebook a').filter(el=>el.getClientRects().length);if(e.shiftKey&&document.activeElement===f[0]){e.preventDefault();f.at(-1)?.focus()}else if(!e.shiftKey&&document.activeElement===f.at(-1)){e.preventDefault();f[0]?.focus()}}});
 // Paint progress without layout writes on every scroll. Observer pauses off-screen animations.
 const progress=$('#progress');let height=1,scheduled=false;
 const measure=()=>{height=Math.max(1,document.documentElement.scrollHeight-innerHeight)};
 function paint(){scheduled=false;if(progress)progress.style.transform=`scaleX(${Math.min(1,scrollY/height)})`}
 const schedule=()=>{if(!scheduled){scheduled=true;requestAnimationFrame(paint)}};measure();schedule();
 document.addEventListener('scroll',schedule,{passive:true});window.addEventListener('resize',()=>{measure();schedule()},{passive:true});new ResizeObserver(()=>{measure();schedule()}).observe($('main'));
 const motion=new IntersectionObserver(entries=>entries.forEach(e=>e.target.classList.toggle('is-inview',e.isIntersecting)),{rootMargin:'80px'});$$('.hero-art,.atlas-workbench,.cause-grid').forEach(el=>motion.observe(el));
 document.addEventListener('visibilitychange',()=>body.classList.toggle('page-hidden',document.hidden));
})();
