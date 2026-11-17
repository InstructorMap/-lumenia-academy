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
#yuna-sound-player{position:fixed;left:14px;bottom:14px;z-index:99999;max-width:min(330px,calc(100vw - 28px));background:#182b3beF;color:#fff;border:1px solid #d6b87e;border-radius:18px;padding:12px 14px;box-shadow:0 12px 36px #09162355;font:13px system-ui;backdrop-filter:blur(15px)}
#yuna-sound-player .ys-head{display:flex;align-items:center;gap:8px;margin-bottom:8px}#yuna-sound-player .ys-head strong{flex:1;font-size:12px}
#yuna-sound-player button{background:#e6c98c;color:#1e2934;border:0;border-radius:9px;padding:7px 9px;cursor:pointer;font-weight:700}#yuna-sound-player button:focus-visible,#yuna-sound-player input:focus-visible{outline:3px solid white}
#yuna-sound-player .ys-controls{display:flex;align-items:center;gap:9px}#yuna-sound-player input{width:95px;accent-color:#e6c98c}#yuna-sound-player .ys-track{font-size:11px;opacity:.85;margin-top:7px}
#yuna-sound-player .ys-status{font-size:11px;color:#f5dfae;margin-top:5px}
@media(max-width:600px){#yuna-sound-player{left:8px;bottom:64px;padding:9px 11px}#yuna-sound-player input{width:75px}}`;document.head.append(css);
const wrap=document.createElement('aside');wrap.id='yuna-sound-player';wrap.setAttribute('aria-label','Música ambiental Yuna Sound Holistic');
wrap.innerHTML='<div class="ys-head"><span aria-hidden="true">♫</span><strong>YUNA Sound Holistic</strong></div><div class="ys-controls"><button type="button" id="ys-mute" aria-label="Silenciar música">Silenciar</button><label for="ys-volume">Vol.</label><input id="ys-volume" type="range" min="0" max="100" step="1" aria-label="Volumen de música" /></div><div class="ys-track" id="ys-track"></div><div class="ys-status" id="ys-status" aria-live="polite"></div>';
document.body.append(wrap);
const $=id=>document.getElementById(id),status=$('ys-status'),volume=$('ys-volume'),mute=$('ys-mute');
function save(){try{localStorage.setItem(key,JSON.stringify(prefs))}catch{}}
function render(){volume.value=Math.round(audio.volume*100);mute.textContent=audio.muted?'Activar sonido':'Silenciar';mute.setAttribute('aria-label',audio.muted?'Activar sonido':'Silenciar música');$('ys-track').textContent='♫ '+tracks[prefs.track].title+' · reproducción continua'}
function attempt(){const p=audio.play();if(p&&p.then)p.then(()=>{status.textContent='Reproduciendo'}).catch(()=>{status.textContent='Tocá la pantalla para activar la música';});}
function select(i){prefs.track=(i+tracks.length)%tracks.length;save();audio.src=tracks[prefs.track].url;render();attempt()}
audio.addEventListener('ended',()=>select(prefs.track+1));
audio.addEventListener('error',()=>{status.textContent='Reintentando música ambiental';setTimeout(()=>select(prefs.track+1),2500)});
mute.addEventListener('click',()=>{audio.muted=!audio.muted;prefs.muted=audio.muted;save();render();attempt()});
volume.addEventListener('input',()=>{audio.volume=Number(volume.value)/100;prefs.volume=audio.volume;save();render();attempt()});

try{const old=JSON.parse(sessionStorage.getItem(resumeKey)||'null');if(old&&old.track===prefs.track&&Date.now()-old.at<60000&&old.time>0)audio.addEventListener('loadedmetadata',()=>{audio.currentTime=Math.min(old.time,Math.max(0,audio.duration-1))},{once:true})}catch{}
function checkpoint(){try{sessionStorage.setItem(resumeKey,JSON.stringify({track:prefs.track,time:audio.currentTime,at:Date.now()}))}catch{}}
setInterval(checkpoint,2000);window.addEventListener('pagehide',checkpoint);
function unlock(){if(audio.paused)attempt();}
document.addEventListener('pointerdown',unlock,{passive:true});document.addEventListener('keydown',unlock);
render();attempt();
})();