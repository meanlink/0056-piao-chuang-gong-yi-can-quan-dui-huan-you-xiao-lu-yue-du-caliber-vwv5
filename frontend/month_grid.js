import {stats,table} from './readout.js';
export const monthStates={open:'预览',queued:'已冻结，存档中',closed:'已封账'};
export function grid({status,report}) {
  const {total,rows}=report;
  const number = r => r.per_hundred_days===null?'无券日':r.per_hundred_days;
  return stats([['月报状态',monthStates[status]],['有效券日',total.voucher_days],['有效核销 / 百券日',number(total)]])+
   table('兑付点透视',['站点','券日','有效核销','每百券日'],[...rows,total].map(r=>[r.site,r.voucher_days,r.redemptions,number(r)]));
}
