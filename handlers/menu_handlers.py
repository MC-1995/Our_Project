from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import logging

from keyboards import (
    get_main_menu,
    get_habits_keyboard,
    get_stats_period_keyboard,
    get_back_keyboard
)

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "📝 Мои привычки")
@router.message(Command("myhabits", "habits"))
async def show_habits(message: types.Message):
    """Показать список привычек пользователя"""
    from database.database import get_user_habits

    habits = get_user_habits(message.from_user.id)

    if not habits:
        await message.answer(
            "📭 <b>У вас пока нет привычек.</b>\n\n"
            "Добавьте свою первую привычку с помощью кнопки '➕ Добавить привычку'",
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
        return

    habits_text = "📋 <b>Ваши привычки:</b>\n\n"
    for i, habit in enumerate(habits[:5], 1):  # Показываем первые 5
        status = "✅" if habit.get('completed_today') else "⏳"
        emoji = habit.get('emoji', '🎯')
        name = habit.get('name', 'Без названия')
        streak = habit.get('streak', 0)
        reminder_time = habit.get('reminder_time', 'нет')

        habits_text += f"{status} {emoji} <b>{name}</b>\n"
        habits_text += f"   🔥 Цепочка: {streak} дней\n"
        habits_text += f"   ⏰ Напоминание: {reminder_time}\n\n"

    await message.answer(
        habits_text,
        parse_mode="HTML",
        reply_markup=get_habits_keyboard(habits)
    )


@router.message(F.text == "📊 Статистика")
@router.message(Command("stats", "statistics"))
async def show_stats_menu(message: types.Message):
    """Показать меню статистики"""
    from database.database import get_user_stats

    stats = get_user_stats(message.from_user.id)

    if not stats or stats.get('total_habits', 0) == 0:
        await message.answer(
            "📊 <b>Статистика появится после добавления первой привычки</b>",
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
        return

    total_habits = stats.get('total_habits', 0)
    active_habits = stats.get('active_habits', 0)
    longest_streak = stats.get('longest_streak', 0)
    success_rate = stats.get('success_rate', 0)
    completed_today = stats.get('completed_today', 0)

    stats_text = f"""
📊 <b>Ваша общая статистика:</b>

📈 <b>Всего привычек:</b> {total_habits}
✅ <b>Активных:</b> {active_habits}
🔥 <b>Самая длинная цепь:</b> {longest_streak} дней
📅 <b>Успешность:</b> {success_rate}%
🎯 <b>Выполнено сегодня:</b> {completed_today}/{active_habits}

<b>Выберите период для детальной статистики:</b>
    """

    await message.answer(
        stats_text,
        parse_mode="HTML",
        reply_markup=get_stats_period_keyboard()
    )


@router.callback_query(F.data.startswith("stats_period_"))
async def show_period_stats(callback: types.CallbackQuery):
    """Показать статистику за выбранный период"""
    period = callback.data.split("_")[2]

    period_names = {
        "today": "сегодня",
        "week": "неделю",
        "month": "месяц",
        "all_time": "все время",
        "last_30_days": "последние 30 дней"
    }

    period_name = period_names.get(period, period)

    # Здесь должна быть логика получения статистики за период
    # Пока заглушка
    stats_text = f"""
📊 <b>Статистика за {period_name}:</b>

🚧 <i>Функция в разработке</i>

Скоро здесь появится детальная статистика за выбранный период!
    """

    try:
        await callback.message.edit_text(
            stats_text,
            parse_mode="HTML",
            reply_markup=get_stats_period_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in show_period_stats: {e}")
        await callback.answer("❌ Не удалось обновить статистику")

    await callback.answer()


@router.message(F.text == "⚙️ Настройки")
@router.message(Command("settings"))
async def show_settings(message: types.Message):
    """Показать настройки"""
    settings_text = """
⚙️ <b>Настройки</b>

<i>Здесь вы можете настроить:</i>
• Часовой пояс
• Время напоминаний
• Язык интерфейса
• Уведомления

🚧 <b>Раздел в разработке</b>

<i>Скоро здесь появятся настройки!</i>
    """

    await message.answer(
        settings_text,
        parse_mode="HTML",
        reply_markup=get_back_keyboard()
    )


@router.message(F.text == "🔙 Назад")
async def back_to_menu(message: types.Message):
    """Вернуться в главное меню"""
    await message.answer(
        "🏠 <b>Главное меню:</b>",
        parse_mode="HTML",
        reply_markup=get_main_menu()
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_callback(callback: types.CallbackQuery):
    """Обработчик inline кнопки возврата в меню"""
    try:
        await callback.message.delete()
    except Exception as e:
        logger.warning(f"Could not delete message in back_to_menu_callback: {e}")

    await callback.message.answer(
        "🏠 <b>Главное меню:</b>",
        parse_mode="HTML",
        reply_markup=get_main_menu()
    )
    await callback.answer()