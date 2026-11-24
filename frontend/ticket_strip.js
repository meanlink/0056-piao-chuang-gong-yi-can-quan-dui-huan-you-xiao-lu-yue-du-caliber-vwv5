import {badge,h} from './base.js';
export const ticket = ({code,counter_name,issued_on,expires_on,redeemed}) =>
  `<article class="ticket"><div><strong>${h(code)}</strong><small>${h(issued_on)} 至 ${h(expires_on)}</small></div><div>${h(counter_name)}　${badge(redeemed?'已兑付':'未兑付')}</div></article>`;
