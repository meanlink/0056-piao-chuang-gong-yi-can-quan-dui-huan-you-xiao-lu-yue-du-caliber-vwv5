import {intro} from './readout.js';
import {feedback,onSubmit,options} from './submit.js';
import {desk,receipts,redeem} from './voucher_client.js';
import {receiptTable} from './receipt_table.js';
export async function render(outlet,user) {
  const [{counters},rows]=await Promise.all([desk(),receipts()]);
  outlet.innerHTML=`${intro('兑付柜台','核销前核对指定餐站、券有效期及既有流水。一张券只能存在一笔有效核销。')}
    <section class="split"><div class="receipt-data band"></div>${user.role==='operator'?`<form class="entry"><h2>登记兑付凭证</h2>
      <label>券码<input name="voucher" required placeholder="QD-111"></label><label>站点<select name="counter">${options(counters.map(r=>[r.code,r.name]))}</select></label>
      <label>兑付日<input name="used_on" type="date" required></label><label>流水号<input name="receipt" required></label>
      <button>确认核销</button>${feedback}</form>`:'<aside class="callout">查阅员可以沿柜台流水核对各月分子。</aside>'}</section>`;
  const draw = data => outlet.querySelector('.receipt-data').innerHTML=receiptTable(data);
  draw(rows);
  onSubmit(outlet.querySelector('form'),async input=>{await redeem(input);draw(await receipts());return '已保存柜台凭证';});
}
