import {api} from './base.js';
export const desk = () => api('/api/issuer');
export const issue = data => api('/api/issuer/vouchers','POST',data);
export const receipts = () => api('/api/counter/receipts');
export const redeem = data => api('/api/counter/receipts','POST',data);
export const reverse = (id,data) => api(`/api/counter/receipts/${id}/reversal`,'POST',data);
export const month = day => api(`/api/voucher-months/${day}`);
export const close = day => api(`/api/voucher-months/${day}/close`,'POST');
