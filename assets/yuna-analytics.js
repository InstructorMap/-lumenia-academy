/* YUNA Academy: first-party, privacy-minimal analytics. No cookies or personal identifiers. */
(()=>{"use strict";
const endpoint="https://ejfdwwolmwwrvaxvkdlw.supabase.co/rest/v1/rpc/yuna_track_event";
const key="sb_publishable_SngMHi2Yz6AxdiLVEvQkUA_iOkMwe3i";
let visitor;
try{visitor=sessionStorage.getItem("yuna_visitor_token");if(!visitor||!/^[0-9a-f-]{36}$/i.test(visitor)){visitor=crypto.randomUUID();sessionStorage.setItem("yuna_visitor_token",visitor)}}catch{visitor=crypto.randomUUID()}
const params=new URLSearchParams(location.search);
function send(event){
 if(!visitor)return;
 const payload={p_event:event,p_page:location.pathname,p_visitor:visitor,p_course:null,p_campaign:params.get("utm_campaign"),p_source:params.get("utm_source"),p_medium:params.get("utm_medium")};
 fetch(endpoint,{method:"POST",headers:{"Content-Type":"application/json","apikey":key},body:JSON.stringify(payload),keepalive:true}).then(async r=>{if(!r.ok)console.warn("YUNA Analytics: evento no registrado",r.status,await r.text())}).catch(e=>console.warn("YUNA Analytics: error de red",e));
}
send("page_view");
document.addEventListener("click",e=>{const target=e.target.closest("a,button");if(!target)return;const text=((target.textContent||"")+" "+(target.getAttribute("aria-label")||"")).toLowerCase();const href=target.getAttribute("href")||"";const id=target.id||"";if(["whatsapp","native","copy"].includes(id)||/compartir|recomendar|copiar enlace/.test(text))send("share_click");if(id==="pay"||/mpago\.la|mercadopago/.test(href)||/pagar|inscribirme ahora/.test(text))send("checkout_click")},true);
})();