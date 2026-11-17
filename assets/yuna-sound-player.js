/* YUNA Sound Holistic — shared ambient player. Browser autoplay restrictions apply. */
(()=>{'use strict';
if(document.getElementById('yuna-sound-player'))return;
const tracks=[
{title:'Sakura Dreams',url:'https://ai-music-tracks.s3.us-east-1.amazonaws.com/5195c175-1edf-40e8-8bf9-b7b6bc5192da/5e8dcc19-584f-4020-aebc-83fc20a22643.wav',youtube:'https://www.youtube.com/watch?v=kr9HeD5tv88'},
{title:'Moonlight Kyoto',url:'https://ai-music-tracks.s3.us-east-1.amazonaws.com/4b0ccbf8-3738-4a0b-b21f-4fb754452073/a740a555-e0b9-41bf-87b4-bddcbf988714.wav',youtube:'https://www.youtube.com/watch?v=N476hy64LFc'}];
const key='yuna-sound-v1',resumeKey='yuna-sound-position';
let prefs={volume:.28,muted:false,track:0};try{Object.assign(prefs,JSON.parse(localStorage.getItem(key)||'{}'))}catch{}
prefs.track=Math.max(0,Math.min(tracks.length-1,Number(prefs.track)||0));
const audio=new Audio();audio.preload='auto';audio.loop=false;audio.volume=Math.max(0,Math.min(1,Number(prefs.volume)||0));audio.muted=!!prefs.muted;audio.src=tracks[prefs.track].url;
const css=document.createElement('style');css.textContent=`
#yuna-sound-player{position:fixed;left:12px;bottom:12px;z-index:9999;width:min(290px,calc(100vw - 24px));box-sizing:border-box;background:#182b3bf2;color:#fff;border:1px solid #d6b87e99;border-radius:999px;padding:8px 12px;box-shadow:0 5px 20px #09162344;font:12px system-ui;backdrop-filter:blur(12px);display:flex;align-items:center;gap:9px}
#yuna-sound-player .ys-title{font-weight:700;white-space:nowrap;font-size:11px}
#yuna-sound-player .ys-controls{display:flex;align-items:center;gap:8px;min-width:0;flex:1}
#yuna-sound-player button{background:#e6c98c;color:#1e2934;border:0;border-radius:50%;width:34px;height:34px;flex:0 0 34px;cursor:pointer;font-size:16px;line-height:1}
#yuna-sound-player button:focus-visible,#yuna-sound-player input:focus-visible{outline:2px solid white;outline-offset:2px}
#yuna-sound-player input{width:100%;min-width:45px;accent-color:#e6c98c;margin:0}
#yuna-sound-player .ys-status{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap}
@media(max-width:600px){#yuna-sound-player{left:8px;bottom:9px;width:174px;max-width:calc(100vw - 165px);min-width:140px;padding:5px 8px;gap:6px;box-shadow:0 3px 12px #09162333}#yuna-sound-player .ys-title{display:none}#yuna-sound-player button{width:32px;height:32px;flex-basis:32px}#yuna-sound-player .ys-controls{gap:7px}}
`;document.head.append(css);
const wrap=document.createElement('aside');wrap.id='yuna-sound-player';wrap.setAttribute('aria-label','Música ambiental Yuna Sound Holistic');
wrap.innerHTML='<span class="ys-title">♫ YUNA Sound</span><div class="ys-controls"><button type="button" id="ys-mute" aria-label="Silenciar música" title="Silenciar o activar sonido">♫</button><input id="ys-volume" type="range" min="0" max="100" step="1" aria-label="Volumen de música" /></div><span class="ys-status" id="ys-status" aria-live="polite"></span>';
document.body.append(wrap);
const $=id=>document.getElementById(id),status=$('ys-status'),volume=$('ys-volume'),mute=$('ys-mute');
function save(){try{localStorage.setItem(key,JSON.stringify(prefs))}catch{}}
function render(){volume.value=Math.round(audio.volume*100);mute.textContent=audio.muted?'♩':'♫';mute.setAttribute('aria-label',audio.muted?'Activar sonido':'Silenciar música');wrap.title='YUNA Sound Holistic · '+tracks[prefs.track].title}
let pending=false;function attempt(){if(pending||!audio.paused)return;pending=true;const p=audio.play();if(p&&p.then)p.then(()=>{status.textContent='Reproduciendo'}).catch(()=>{status.textContent='El navegador requiere una interacción para activar el sonido';}).finally(()=>{pending=false});else pending=false;}
function select(i){prefs.track=(i+tracks.length)%tracks.length;save();audio.src=tracks[prefs.track].url;render();attempt()}
audio.addEventListener('ended',()=>select(prefs.track+1));
audio.addEventListener('error',()=>{status.textContent='Reintentando música ambiental';setTimeout(()=>select(prefs.track+1),2500)});
mute.addEventListener('click',()=>{audio.muted=!audio.muted;prefs.muted=audio.muted;save();render();attempt()});
volume.addEventListener('input',()=>{audio.volume=Number(volume.value)/100;prefs.volume=audio.volume;save();render();attempt()});

try{const old=JSON.parse(sessionStorage.getItem(resumeKey)||'null');if(old&&old.track===prefs.track&&Date.now()-old.at<60000&&old.time>0)audio.addEventListener('loadedmetadata',()=>{audio.currentTime=Math.min(old.time,Math.max(0,audio.duration-1))},{once:true})}catch{}
function checkpoint(){try{sessionStorage.setItem(resumeKey,JSON.stringify({track:prefs.track,time:audio.currentTime,at:Date.now()}))}catch{}}
setInterval(checkpoint,2000);window.addEventListener('pagehide',checkpoint);
let lastUnlock=0;
function unlock(){if(!audio.paused)return;const now=Date.now();if(now-lastUnlock<1200)return;lastUnlock=now;attempt();}
['pointerdown','touchstart','touchend','click','keydown','wheel','scroll'].forEach(event=>document.addEventListener(event,unlock,{passive:true,capture:event==='scroll'}));
window.addEventListener('scroll',unlock,{passive:true});
render();attempt();
})();