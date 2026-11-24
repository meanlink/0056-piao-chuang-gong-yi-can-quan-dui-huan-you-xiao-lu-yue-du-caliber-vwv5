from fastapi import APIRouter
from batch_routes import router as router_0
from counter_routes import router as router_1
from reversal_routes import router as router_2
from month_routes import router as router_3
from voucher_seed import seed
from month_worker import run as run_job

router = APIRouter(prefix="/api")
router.include_router(router_0)
router.include_router(router_1)
router.include_router(router_2)
router.include_router(router_3)
