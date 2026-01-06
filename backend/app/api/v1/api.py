"""
API v1 router aggregation
"""
from fastapi import APIRouter
from .auth import router as auth_router
from .ip_ranges import router as ip_ranges_router
from .devices import router as devices_router
from .dhcp import router as dhcp_router
from .statistics import router as statistics_router
from .users import router as users_router
from .syslog import router as syslog_router
from .settings import router as settings_router
from .logs import router as logs_router

# Main API router
router = APIRouter()

# Include all sub-routers
router.include_router(auth_router)
router.include_router(ip_ranges_router)
router.include_router(devices_router)
router.include_router(dhcp_router)
router.include_router(statistics_router, prefix="/stats", tags=["statistics"])
router.include_router(users_router)
router.include_router(syslog_router)
router.include_router(settings_router)
router.include_router(logs_router)
