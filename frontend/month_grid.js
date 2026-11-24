import {stats,table} from './readout.js';
export const monthStates={open:'预览',queued:'已冻结，存档中',closed:'已封账'};

const day10 = v => v ? String(v).slice(0,10) : '';

export function deductionTable(deductions) {
  if (!deductions?.length) return '';
  return table(
    '补记扣减明细（可追溯原核销与原月份）',
    ['实际冲回日','补记月份','兑付点','原核销凭据','券码','原核销日','原月份','复核备注','复核员'],
    deductions.map(d => [
      day10(d.reversed_on ?? d.deducted_on ?? d.posted_on),
      day10(d.supplement_month ?? d.month),
      d.site ?? d.counter_name ?? d.counter,
      `#${d.redemption_id} ${d.receipt ?? d.original_receipt ?? ''}`,
      d.voucher ?? d.voucher_code,
      day10(d.used_on ?? d.original_used_on),
      day10(d.original_month ?? d.source_month),
      d.reason,
      d.approved_by,
    ]),
  );
}

export function grid({status,report}) {
  const {total,rows}=report;
  const number = r => r.per_hundred_days===null||r.per_hundred_days===undefined?'无券日':r.per_hundred_days;
  const deductions = report.deductions ?? report.adjustments ?? [];
  const deductionCount = total.deductions ?? total.deduction_count ?? deductions.length;
  return stats([
      ['月报状态',monthStates[status]],
      ['有效券日',total.voucher_days],
      ['有效核销 / 百券日',number(total)],
      ['补记扣减（净核销可为负）',deductionCount],
    ])+
   table('兑付点透视（有效核销为净口径，含补记扣减，可为负）',
     ['站点','券日','有效核销','每百券日'],
     [...rows,total].map(r=>[r.site,r.voucher_days,r.redemptions,number(r)]))+
   deductionTable(deductions);
}
