'use strict';
let font=1.08,utterance=null;
document.querySelector('#mask').onclick=()=>document.body.classList.toggle('masked');document.querySelectorAll('#reading p').forEach(p=>p.onclick=()=>p.classList.toggle('revealed'));
document.querySelector('#size').onclick=()=>{font=font>=1.55?1.08:font+.12;document.querySelector('#reading').style.fontSize=font+'rem'};
const button=document.querySelector('#speak');
if(!('speechSynthesis' in window)){button.disabled=true;button.textContent='此设备不支持朗读'}else{button.onclick=()=>{if(speechSynthesis.speaking){speechSynthesis.cancel();button.textContent='朗读 / 暂停';return}utterance=new SpeechSynthesisUtterance(document.querySelector('#reading').textContent);utterance.lang='zh-CN';utterance.rate=.85;utterance.onend=()=>button.textContent='朗读 / 暂停';utterance.onerror=()=>button.textContent='朗读未完成，可重试';speechSynthesis.speak(utterance);button.textContent='停止朗读'};window.addEventListener('pagehide',()=>speechSynthesis.cancel())}
try{if(localStorage.getItem('dort-theme')==='dark')document.body.classList.add('dark')}catch{}
