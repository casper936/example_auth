import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from src.core.route_classes import ThreadLocalDataRouter
from src.schemas import (
    
)
from src.services.crud.profiles import ProfileService, get_profile_service
from src.utils.db import transactional
from src.utils.users import require_user

# Объект router, в котором регистрируем обработчики
router = APIRouter(route_class=ThreadLocalDataRouter)
logger = structlog.get_logger(__name__)
