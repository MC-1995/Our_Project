from .start_handler import router as start_router
from .menu_handlers import router as menu_router
from .habit_handlers import router as habit_router

# Экспортируем все роутеры для удобного импорта
routers = [start_router, menu_router, habit_router]

__all__ = [
    'start_router',
    'menu_router',
    'habit_router',
    'routers'
]