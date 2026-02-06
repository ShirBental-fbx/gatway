"""Auto-generated legacy routers module.

DO NOT EDIT MANUALLY - Regenerate using: python legacy/scripts/generate_fastapi_routers.py
"""

from __future__ import annotations

from gateway.routers.legacy._string_original_platform_ import router as _string_original_platform__router
from gateway.routers.legacy._string_platform_ import router as _string_platform__router
from gateway.routers.legacy.api import router as api_router
from gateway.routers.legacy.fetch_credit_report import router as fetch_credit_report_router
from gateway.routers.legacy.fetch_ssn import router as fetch_ssn_router
from gateway.routers.legacy.fetch_ssn_masked import router as fetch_ssn_masked_router
from gateway.routers.legacy.fuse import router as fuse_router
from gateway.routers.legacy.galileo import router as galileo_router
from gateway.routers.legacy.heartbeat import router as heartbeat_router
from gateway.routers.legacy.hooks import router as hooks_router
from gateway.routers.legacy.mailhouse_round_delivered_notification import router as mailhouse_round_delivered_notification_router
from gateway.routers.legacy.oauth2 import router as oauth2_router
from gateway.routers.legacy.opt_out import router as opt_out_router
from gateway.routers.legacy.rtd_apply import router as rtd_apply_router
from gateway.routers.legacy.rtd_remove import router as rtd_remove_router
from gateway.routers.legacy.s3_data_upload import router as s3_data_upload_router
from gateway.routers.legacy.send_notification import router as send_notification_router
from gateway.routers.legacy.stripe import router as stripe_router
from gateway.routers.legacy.v1 import router as v1_router

# Export all routers for easy importing
__all__ = [
    "_string_original_platform__router",
    "_string_platform__router",
    "api_router",
    "fetch_credit_report_router",
    "fetch_ssn_router",
    "fetch_ssn_masked_router",
    "fuse_router",
    "galileo_router",
    "heartbeat_router",
    "hooks_router",
    "mailhouse_round_delivered_notification_router",
    "oauth2_router",
    "opt_out_router",
    "rtd_apply_router",
    "rtd_remove_router",
    "s3_data_upload_router",
    "send_notification_router",
    "stripe_router",
    "v1_router",
]

# List of all router instances for bulk inclusion
all_routers = [
    _string_original_platform__router,
    _string_platform__router,
    api_router,
    fetch_credit_report_router,
    fetch_ssn_router,
    fetch_ssn_masked_router,
    fuse_router,
    galileo_router,
    heartbeat_router,
    hooks_router,
    mailhouse_round_delivered_notification_router,
    oauth2_router,
    opt_out_router,
    rtd_apply_router,
    rtd_remove_router,
    s3_data_upload_router,
    send_notification_router,
    stripe_router,
    v1_router,
]
