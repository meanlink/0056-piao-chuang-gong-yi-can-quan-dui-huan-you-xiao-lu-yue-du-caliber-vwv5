# 票窗 · 公益餐券兑换有效率月度口径

从发行日、有效期和核销撤销中得到可复核的每百券日兑换次数。

**模拟客户**　惠邻公益餐站，仓前、桥东两个兑付点与三位月结同事

**现有流程**　餐站拿两份台账手工做月结。跨月发券被算进整月分母、兑付错门店后难作废、审批人无法复现上报时的表格。

**业务交接**　批次与券码来自社区项目组，柜台登记核销，统计员按券日发布已冻结的分站报表给两家合作厨房。

## 一日工作剧本

1. 09:00 核对桥东 QD-11 批次和已发券 QD-111。
2. 09:10 核实 QD-111 在 11 月只存续 10 个券日。
3. 09:20 餐站录入员登记 11 月 18 日兑付。跨批次兑付点尝试被拒绝。
4. 09:35 复核一笔录错的兑付并冲回，使券恢复可用。
5. 10:00 复核员按 2026-11 月报预览，桥东每 100 券日 5 笔。
6. 10:15 后台保存不可改的终版结果，查阅员对照历史月报。
7. 10:20 核对封账后禁止回填 11 月数据，次月业务继续。

## 算法和演示边界

以日期闭区间计算券有效期与月份的交集天数。分母为月内所有已发行券的券日。分子为发生在月内且未冲回的核销。每百券日=100×分子/分母，零分母返回空值。封账保存按站点透视及总计。

日期用业务所在地自然日登记。演示环境只管理发券和核销记录，餐食配送、支付及外部通知由餐站处理。

## 快速启动

```sh
cp .env.example .env
docker compose up -d --build --wait
docker compose exec -T backend python -m scripts.seed_demo
```

- 前端浏览器地址为 `http://127.0.0.1:18450`。
- FastAPI 文档地址为 `http://127.0.0.1:19450/docs`。
- PostgreSQL 本地端口为 `17950`。后端与后台 worker 共用数据库事务和 Redis 健康探测。
- 开发 HTML、CSS、ES modules 后运行 `docker compose up -d --build frontend`。Python 代码修改后运行 `docker compose up -d --build backend worker`。
- `SEED_DEMO` 控制自动填充。可改三项宿主端口、`DEMO_PASSWORD`、`JWT_SECRET`、`POSTGRES_PASSWORD`。持久卷保存业务数据和队列状态。停机并保留数据使用 `docker compose down`。
- 技术栈为 Python 3.11、FastAPI、PostgreSQL 16、Redis 7、Nginx 与原生浏览器 JS。后端业务模块、SQL 迁移都在 `backend/`。界面和交互在 `frontend/`。

| 账号 | 密码 | 典型权限 |
|---|---|---|
| operator@demo.local | Demo2026! | 登记发行和核销 |
| reviewer@demo.local | Demo2026! | 错录冲回、冻结月报 |
| viewer@demo.local | Demo2026! | 查阅记录和经计算的指标 |

共享角色和任务状态枚举分别位于 `backend/core.py` 的 `ROLES`、`JOB_STATES` 和 `frontend/base.js` 的 `roles`、`jobStates`。数据库检查约束与服务状态以相应 SQL 和模块为准。

许可证见 LICENSE。
