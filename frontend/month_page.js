import {waitJob} from './base.js';
import {intro} from './readout.js';
import {feedback,onSubmit} from './submit.js';
import {month,close} from './voucher_client.js';
import {grid} from './month_grid.js';
export async function render(outlet,user) {
  outlet.innerHTML=`${intro('券日月报','分母以券有效期与月份重叠的日数计算；已冲回的流水从分子剔除。')}
    <form class="toolrow"><label>业务月份<input type="month" value="2026-11" required></label>
    ${user.role==='reviewer'?'<button>封账并归档</button>':''}${feedback}</form><section class="monthly band"></section>`;
  const input=outlet.querySelector('input');
  const day=()=>input.value+'-01';
  async function refresh() {if(input.value) outlet.querySelector('.monthly').innerHTML=grid(await month(day()));}
  input.onchange=refresh;
  onSubmit(outlet.querySelector('form'),async()=>{const job=await close(day());await waitJob(job.job_id);await refresh();return '终版已保存';});
  await refresh();
}
