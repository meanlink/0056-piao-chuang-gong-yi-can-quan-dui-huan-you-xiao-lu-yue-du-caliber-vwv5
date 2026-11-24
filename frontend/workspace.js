import {mount} from './base.js';
import {render as issued} from './issued_page.js';
import {render as counter} from './counter_page.js';
import {render as reversals} from './reversals_page.js';
import {render as month} from './month_page.js';
const pages = {"issued": "发行券簿", "counter": "兑付柜台", "reversals": "错录冲回", "month": "券日月报"};
const screens = {issued, counter, reversals, month};
mount({title: "票窗 · 公益餐券兑换有效率月度口径", kicker: "公益餐站 / 核销月结", pages, render: (page, outlet, user) => screens[page](outlet, user)});
