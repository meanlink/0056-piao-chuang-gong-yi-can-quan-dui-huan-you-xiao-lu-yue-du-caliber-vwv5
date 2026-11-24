import {table} from './readout.js';
export function receiptTable(rows) {
  return table('柜台凭证',['凭据','券码','兑付点','核销日','状态'],rows.map(r=>[r.receipt,r.voucher,r.counter,r.used_on,r.reason?'已冲回 · '+r.reason:'有效']));
}
