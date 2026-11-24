import {intro} from './readout.js';
import {feedback,onSubmit,options} from './submit.js';
import {desk,issue} from './voucher_client.js';
import {ticket} from './ticket_strip.js';
export async function render(outlet,user) {
  const data=await desk();
  outlet.innerHTML=`${intro('发行券簿','按赞助批次发行券码，每一张券绑定指定兑付点与开始和截止日。')}
    <section class="split"><div class="lineup"></div>${user.role==='operator'?`<form class="entry">
      <h2>登记新券</h2><label>券码<input name="code" required placeholder="QD-113"></label>
      <label>发行批次<select name="batch">${options(data.batches.map(r=>[r.code,r.code+' · '+r.sponsor]))}</select></label>
      <label>发行日<input name="issued_on" type="date" required></label><label>最后有效日<input name="expires_on" type="date" required></label>
      <button>登记有效期</button>${feedback}</form>`:'<aside class="callout">发行日在月末也只计实际有效券日。跨月券可分别进入两个月报。</aside>'}</section>`;
  const draw = rows => outlet.querySelector('.lineup').innerHTML=rows.map(ticket).join('');
  draw(data.vouchers);
  onSubmit(outlet.querySelector('form'),async input=>{await issue(input);draw((await desk()).vouchers);return '券码和有效期已登记';});
}
