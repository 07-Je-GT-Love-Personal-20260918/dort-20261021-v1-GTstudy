/* Local illustration + lazy online cartography. No remote JS/CDN dependency. */
(()=>{'use strict';
 const data=document.querySelector('#atlas-data');if(!data)return;
 const places=JSON.parse(data.textContent),box=document.querySelector('#live-map'),status=document.querySelector('#map-status');
 const reduced=matchMedia('(prefers-reduced-motion: reduce)'),esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 let context=null,selected=places[0],map=null,layer=null,starting=false,provider='imagery',timer=null,loaded=0,failed=0,tour=null,pausedByPage=false;
 const markers=new Map(),tried=new Set();
 const providers={
  imagery:{label:'Esri 卫星影像',url:'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',attribution:'Tiles © Esri — Source: Esri, Vantor, Earthstar Geographics, and the GIS User Community',maxZoom:18},
  topo:{label:'Esri 地形街道',url:'https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',attribution:'Tiles © Esri — Esri, HERE, Garmin, FAO, NOAA, USGS, © OpenStreetMap contributors, and the GIS User Community',maxZoom:17},
  opentopo:{label:'OpenTopoMap 备用',url:'https://tile.opentopomap.org/{z}/{x}/{y}.png',attribution:'Map data © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, SRTM | Map style © <a href="https://opentopomap.org">OpenTopoMap</a> (CC-BY-SA)',maxZoom:17}
 };
 function detail(){
  const p=selected,c=context?.places.find(x=>x.id===p.id),sources=c?.sources||[];
  document.querySelector('#place-detail').innerHTML=`<div class="place-title"><span class="place-icon">${p.icon}</span><div><small>${esc(p.year)} · ${esc(p.latin)}</small><h3>${esc(p.name)} <span>${esc(p.role)}</span></h3></div><a class="button tiny" href="atlas.html#culture-${p.id}">文化背景 ↗</a></div><p class="place-core">${esc(p.core)}</p>${c?`<div class="place-facts"><p><span class="fact-label">史实</span>${esc(c.fact)}</p><p><span class="meaning-label">解读</span>${esc(c.interpretation)}</p></div><div class="source">${sources.map(s=>`<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title)} ↗</a>`).join(' · ')}</div>`:''}`;
  const q=encodeURIComponent(`${p.lat},${p.lon}`);
  document.querySelector('#map-external').innerHTML=`<a href="https://www.google.com/maps/search/?api=1&query=${q}" target="_blank" rel="noopener">Google Maps ↗</a><a href="https://www.bing.com/maps?cp=${p.lat}~${p.lon}&lvl=12" target="_blank" rel="noopener">Bing Maps ↗</a><small>${p.lat.toFixed(4)}°N · ${p.lon.toFixed(4)}°E</small>`;
 }
 function choose(id,move=true){
  const p=places.find(x=>x.id===id);if(!p)return;selected=p;
  document.querySelectorAll('[data-place]').forEach(n=>{const active=n.dataset.place===id;n.classList.toggle('is-active',active);n.setAttribute('aria-pressed',String(active))});
  markers.forEach((m,k)=>m.getElement()?.classList.toggle('active-pin',k===id));detail();
  if(map&&move){map.stop();map.flyTo([p.lat,p.lon],11,{duration:reduced.matches?0:.7,animate:!reduced.matches})}
 }
 document.querySelectorAll('[data-place]').forEach(n=>{n.addEventListener('click',()=>choose(n.dataset.place));if(n.tagName.toLowerCase()==='g')n.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();choose(n.dataset.place)}})});
 choose(selected.id,false);
 fetch('atlas-context.json').then(r=>{if(!r.ok)throw Error('context');return r.json()}).then(x=>{context=x;detail()}).catch(()=>{document.querySelector('#place-detail').insertAdjacentHTML('beforeend','<p class="source">文化详解见历史图谱页；本地资料暂未载入。</p>')});
 function fallback(){
  clearTimeout(timer);if(loaded)return;
  const next=Object.keys(providers).find(k=>!tried.has(k));
  if(next){status.textContent='此底图响应较慢，正在换用 '+providers[next].label+'…';setLayer(next,false)}
  else {status.textContent='在线底图暂不可用。请使用左侧示意图，或下方独立地图入口；也可点击“重试地图”。';document.querySelector('#map-load').textContent='重试地图';box.classList.add('map-unavailable')}
 }
 function setLayer(key,manual=true){
  provider=key;document.querySelector('#map-provider').value=key;if(!map)return;
  map.stop();clearTimeout(timer);if(manual)tried.clear();tried.add(key);loaded=0;failed=0;box.classList.remove('map-unavailable');
  if(layer){map.removeLayer(layer);layer.off()}
  const p=providers[key];layer=L.tileLayer(p.url,{attribution:p.attribution,maxZoom:p.maxZoom,updateWhenIdle:true,updateWhenZooming:false,keepBuffer:1,detectRetina:false});
  layer.on('tileload',()=>{loaded++;clearTimeout(timer);status.textContent=p.label+'已显示 · 拖动地图；使用 ＋ / − 或双指缩放。';document.querySelector('#map-load').textContent='重新载入'});
  layer.on('tileerror',()=>{failed++;if(failed>=3&&!loaded)fallback()});
  status.textContent='正在载入 '+p.label+'…';layer.addTo(map);timer=setTimeout(fallback,10000);
 }
 function localLeaflet(){return new Promise((resolve,reject)=>{
  if(window.L){resolve();return}const css=document.createElement('link');css.rel='stylesheet';css.href='vendor/leaflet/leaflet.css';document.head.append(css);
  const script=document.createElement('script');script.src='vendor/leaflet/leaflet.js';script.onload=resolve;script.onerror=reject;document.head.append(script);
 })}
 async function start(){
  if(map){setLayer(provider);return}if(starting)return;starting=true;status.textContent='正在准备地图…';
  try{
   await localLeaflet();box.replaceChildren();map=L.map(box,{scrollWheelZoom:false,zoomAnimation:false,fadeAnimation:false,preferCanvas:true,inertia:true,inertiaDeceleration:2400}).setView([selected.lat,selected.lon],10);
   places.forEach(p=>{const icon=L.divIcon({className:'history-pin',html:`<span>${p.icon}</span>`,iconSize:[34,34],iconAnchor:[17,17]});const marker=L.marker([p.lat,p.lon],{icon,title:p.name}).addTo(map).bindTooltip(p.name,{direction:'top',offset:[0,-14]});marker.on('click',()=>choose(p.id,false));markers.set(p.id,marker)});
   new ResizeObserver(()=>{if(document.visibilityState==='visible')map.invalidateSize({pan:false})}).observe(box);
   setLayer(provider);choose(selected.id,false);
  }catch{status.textContent='地图组件暂未载入。历史示意图和独立地图入口仍可使用。';document.querySelector('#map-load').textContent='重试地图'}finally{starting=false}
 }
 document.querySelector('#map-load').onclick=start;
 document.querySelector('#map-provider').onchange=e=>{provider=e.target.value;if(map)setLayer(provider);else start()};
 document.querySelector('#map-overview').onclick=()=>{if(!map){start().then(()=>map?.fitBounds(places.map(p=>[p.lat,p.lon]),{padding:[25,25],animate:false}));return}map.stop();map.fitBounds(places.map(p=>[p.lat,p.lon]),{padding:[25,25],animate:false})};
 const lazy=new IntersectionObserver(entries=>{if(entries.some(e=>e.isIntersecting)){lazy.disconnect();start()}},{rootMargin:'180px'});lazy.observe(box);
 function stopTour(){clearInterval(tour);tour=null;document.querySelector('.atlas-workbench')?.classList.remove('tour-active');const b=document.querySelector('#tour-play');if(b)b.textContent='▷ 播放思想路线'}
 document.querySelector('#tour-play')?.addEventListener('click',()=>{
  if(tour){stopTour();return}let i=places.findIndex(x=>x.id===selected.id);document.querySelector('.atlas-workbench').classList.add('tour-active');document.querySelector('#tour-play').textContent='■ 结束播放';
  const step=()=>{choose(places[i%places.length].id);document.querySelector('#tour-state').textContent=`${i%places.length+1} / ${places.length} · ${selected.name}：${selected.core}`;i++};step();tour=setInterval(step,6500)
 });
 document.querySelector('#tour-stop')?.addEventListener('click',stopTour);
 const inView=new IntersectionObserver(entries=>{if(entries.every(e=>!e.isIntersecting)){stopTour();map?.stop()}},{threshold:0});inView.observe(document.querySelector('.atlas-workbench'));
 document.addEventListener('visibilitychange',()=>{if(document.hidden){stopTour();map?.stop()}});
 window.addEventListener('pagehide',()=>{stopTour();clearTimeout(timer)});
})();
