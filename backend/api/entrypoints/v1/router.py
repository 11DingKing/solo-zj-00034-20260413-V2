from fastapi.routing import APIRouter

from api.entrypoints.v1 import root_response, random_number
from api.entrypoints.v1.auth import views as auth_views

router = APIRouter()
router.include_router(random_number.router, prefix="/random_number", tags=["Random Number"])
router.include_router(root_response.router, prefix="", tags=["Root Response"])
router.include_router(auth_views.router, prefix="/auth", tags=["Authentication"])
