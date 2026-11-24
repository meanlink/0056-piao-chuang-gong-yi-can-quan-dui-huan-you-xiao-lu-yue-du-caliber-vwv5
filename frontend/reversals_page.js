import {intro,table} from './readout.js';
import {feedback,onSubmit,options} from './submit.js';
import {receipts,reverse} from './voucher_client.js';

const today = () => new Date().toISOString().slice(0,10);

export async function render(outlet,user) {
  const rows=await receipts();
  outlet.innerHTML=`${intro('错录冲回','复核员凭原始柜台流水冲回误录。封账后才发现的错核销，按实际冲回日在补记月份的原兑付点补扣一笔；已冻结月报仍照原数归档查阅，净核销可以为负。补记月份若已封账则无法补记，券维持已核销。')}
    <section class="split"><div class="history band"></div>${user.role==='reviewer'?`<form class="entry"><h2>核对后冲回 / 封账后补记</h2>
      <label>未冲回凭证<select name="id" required></select></label>
      <label>实际冲回日<input name="reversed_on" type="date" value="${today()}"></label>
      <p class="field-hint">按实际冲回日归属补记月份；清空则取今天。原月份已封账时，将在补记月份的原兑付点扣一笔。</p>
      <label>复核备注<textarea name="reason" minlength="4" required placeholder="注明原始柜台流水及误录原因"></textarea></label>
      <button>批准冲回</button>${feedback}</form>`:'<aside class="callout">查看冲回原因、实际冲回日与补记月份，并与先前凭条对照。</aside>'}</section>`;
  function draw(data) {
    const active=outlet.querySelector('select');
    if (active) active.innerHTML=options(data.filter(r=>!r.reason).map(r=>[r.id,r.receipt+' · '+r.voucher]));
    outlet.querySelector('.history').innerHTML=table(
      '冲回记录 / 封账补记',
      ['原流水','券码','兑付点','核销日','冲回日','补记月份','原月份','备注','复核员'],
      data.filter(r=>r.reason).map(r=>[
        r.receipt,
        r.voucher,
        r.counter,
        r.used_on,
        r.reversed_on ?? '',
        (r.deduction_month ?? r.reversal_month) ? String(r.deduction_month ?? r.reversal_month).slice(0,10) : '',
        r.original_month ? String(r.original_month).slice(0,10)
          : (r.used_on ? String(r.used_on).slice(0,8)+'01' : ''),
        r.reason,
        r.approved_by,
      ]));
  }
  draw(rows);
  onSubmit(outlet.querySelector('form'),async(form)=>{
    const payload={reason:form.reason};
    if (form.reversed_on) payload.reversed_on=form.reversed_on;
    const result=await reverse(form.id,payload);
    draw(await receipts());
    return result?.late
      ? '已冲回并在补记月份原兑付点扣减一笔，券恢复可核销；同一笔重试不会重复扣减。'
      : '已冲回，券恢复可核销';
  });
}
