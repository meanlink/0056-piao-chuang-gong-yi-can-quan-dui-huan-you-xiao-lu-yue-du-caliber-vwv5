import {intro,table} from './readout.js';
import {feedback,onSubmit,options} from './submit.js';
import {receipts,reverse} from './voucher_client.js';
export async function render(outlet,user) {
  const rows=await receipts();
  outlet.innerHTML=`${intro('错录冲回','复核员应凭原始柜台流水冲回误录，再由录入员重开核销。月报冻结后原始流水与冲回同时锁定。')}
    <section class="split"><div class="history band"></div>${user.role==='reviewer'?`<form class="entry"><h2>核对后冲回</h2>
      <label>未冲回凭证<select name="id" required></select></label>
      <label>复核备注<textarea name="reason" minlength="4" required placeholder="注明原始柜台流水及误录原因"></textarea></label>
      <button>批准冲回</button>${feedback}</form>`:'<aside class="callout">查看冲回原因，并与先前凭条对照。</aside>'}</section>`;
  function draw(data) {
    const active=outlet.querySelector('select');
    if (active) active.innerHTML=options(data.filter(r=>!r.reason).map(r=>[r.id,r.receipt+' · '+r.voucher]));
    outlet.querySelector('.history').innerHTML=table('冲回记录',['原流水','券码','备注','复核员'],data.filter(r=>r.reason).map(r=>[r.receipt,r.voucher,r.reason,r.approved_by]));
  }
  draw(rows);
  onSubmit(outlet.querySelector('form'),async({id,reason})=>{await reverse(id,{reason});draw(await receipts());return '已冲回，券恢复可核销';});
}
