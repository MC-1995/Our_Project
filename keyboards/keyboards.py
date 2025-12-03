from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from typing import List, Dict, Any


def get_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню бота"""
    builder = ReplyKeyboardBuilder()

    builder.button(text="📝 Мои привычки")
    builder.button(text="➕ Добавить привычку")
    builder.button(text="📊 Статистика")
    builder.button(text="⚙️ Настройки")

    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Отмена")
    return builder.as_markup(resize_keyboard=True)


def get_confirm_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура подтверждения"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="✅ Подтвердить")
    builder.button(text="❌ Отмена")
    return builder.as_markup(resize_keyboard=True)


def get_back_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой назад"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="🔙 Назад")
    return builder.as_markup(resize_keyboard=True)


def get_habits_keyboard(habits: List[Dict[str, Any]], page: int = 0, per_page: int = 5) -> InlineKeyboardMarkup:
    """Инлайн-клавиатура со списком привычек"""
    builder = InlineKeyboardBuilder()

    # Если привычек нет
    if not habits:
        builder.button(text="➕ Добавить первую привычку", callback_data="add_habit")
        builder.adjust(1)
        return builder.as_markup()

    # Отображаем привычки для текущей страницы
    start_idx = page * per_page
    end_idx = min(start_idx + per_page, len(habits))

    for habit in habits[start_idx:end_idx]:
        habit_id = habit.get('id', 0)
        emoji = habit.get('emoji', '🎯')
        name = habit.get('name', 'Без названия')
        streak = habit.get('streak', 0)

        builder.button(
            text=f"{emoji} {name} 🔥{streak}",
            callback_data=f"habit_{habit_id}"
        )

    # Пагинация
    if len(habits) > per_page:
        row_buttons = []
        if page > 0:
            row_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_{page - 1}"))

        # Информация о странице
        total_pages = (len(habits) + per_page - 1) // per_page

        if (page + 1) * per_page < len(habits):
            row_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"page_{page + 1}"))

        if row_buttons:
            builder.row(*row_buttons)

    # Кнопки действий
    builder.button(text="➕ Добавить привычку", callback_data="add_habit")
    builder.button(text="🔙 В главное меню", callback_data="back_to_menu")

    builder.adjust(1)
    return builder.as_markup()


def get_habit_actions_keyboard(habit_id: int) -> InlineKeyboardMarkup:
    """Действия с конкретной привычкой"""
    builder = InlineKeyboardBuilder()

    builder.button(text="✅ Отметить выполнение", callback_data=f"complete_{habit_id}")
    builder.button(text="✏️ Редактировать", callback_data=f"edit_{habit_id}")
    builder.button(text="🗑️ Удалить", callback_data=f"delete_{habit_id}")
    builder.button(text="📊 Статистика привычки", callback_data=f"stats_habit_{habit_id}")
    builder.button(text="🔙 К списку привычек", callback_data="back_to_habits")

    builder.adjust(1)
    return builder.as_markup()


def get_time_selection_keyboard() -> ReplyKeyboardMarkup:
    """Выбор времени напоминания"""
    builder = ReplyKeyboardBuilder()

    times = ["07:00", "08:00", "09:00", "12:00", "15:00", "18:00", "21:00", "22:00"]
    for time in times:
        builder.button(text=time)

    builder.button(text="⏰ Каждый час")
    builder.button(text="🚫 Без напоминания")
    builder.button(text="❌ Отмена")

    builder.adjust(3, 3, 2, 1)
    return builder.as_markup(resize_keyboard=True)


def get_frequency_keyboard() -> ReplyKeyboardMarkup:
    """Выбор частоты выполнения"""
    builder = ReplyKeyboardBuilder()

    frequencies = [
        "📅 Ежедневно",
        "🏢 По будням",
        "🏝️ По выходным",
        "📆 Раз в неделю",
        "🔢 Несколько раз в неделю"
    ]

    for text in frequencies:
        builder.button(text=text)

    builder.button(text="❌ Отмена")

    builder.adjust(2, 2, 1, 1)
    return builder.as_markup(resize_keyboard=True)


def get_stats_period_keyboard() -> InlineKeyboardMarkup:
    """Выбор периода для статистики"""
    builder = InlineKeyboardBuilder()

    periods = [
        ("📅 Сегодня", "today"),
        ("📊 Неделя", "week"),
        ("📈 Месяц", "month"),
        ("📆 Все время", "all_time"),
        ("🗓️ За последние 30 дней", "last_30_days")
    ]

    for text, callback in periods:
        builder.button(text=text, callback_data=f"stats_period_{callback}")

    builder.button(text="🔙 Назад", callback_data="back_to_menu")
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def get_edit_habit_keyboard(habit_id: int) -> InlineKeyboardMarkup:
    """Выбор поля для редактирования привычки"""
    builder = InlineKeyboardBuilder()

    fields = [
        ("📝 Название", "name"),
        ("📋 Описание", "description"),
        ("⏰ Время напоминания", "reminder_time"),
        ("🔄 Частота", "frequency"),
        ("🎨 Эмодзи", "emoji")
    ]

    for text, field in fields:
        builder.button(text=text, callback_data=f"edit_field_{field}")

    # Кнопка возврата к привычке с передачей habit_id
    builder.button(text="🔙 Назад к привычке", callback_data=f"back_to_habit_{habit_id}")
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def get_emoji_selection_keyboard(habit_id: int) -> InlineKeyboardMarkup:
    """Выбор эмодзи для привычки"""
    builder = InlineKeyboardBuilder()

    emojis = ["🎯", "💪", "🏃", "📚", "💧", "🥗", "😴", "🧘", "🎨", "🎸", "✍️", "🧹", "💰", "🌱", "🌟"]

    for emoji in emojis:
        builder.button(text=emoji, callback_data=f"emoji_{emoji}")

    # Кнопка возврата к редактированию с передачей habit_id
    builder.button(text="🔙 Назад", callback_data=f"back_to_edit_{habit_id}")
    builder.adjust(5, 5, 5, 1)
    return builder.as_markup()