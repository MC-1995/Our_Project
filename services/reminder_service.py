import asyncio
from database.database import db
from keyboards.keyboards import get_daily_check_keybord, get_negative_check_keyboard

bot = None

def set_bot(bot_instance):
    global bot
    bot = bot_instance

asyns def schedule_reminders(user_id: int, habit: str, habit_type: str):

    if habit_type == "negative":
        # Утреннее напоминание
        asyncio.create_task(send_morning_reminder(user_id, habit))
    else:
        # Для положительной привычки
        asyncio.create_task(send_habit_reminder(user_id, habit))