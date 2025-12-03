from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
import logging

from keyboards import (
    get_main_menu,
    get_cancel_keyboard,
    get_confirm_keyboard,
    get_time_selection_keyboard,
    get_frequency_keyboard,
    get_habit_actions_keyboard,
    get_habits_keyboard,
    get_edit_habit_keyboard,
    get_emoji_selection_keyboard
)
from utils.states import HabitStates, EditHabitStates, DeleteHabitStates
from typing import Dict, Any

router = Router()
logger = logging.getLogger(__name__)


# ---------- Добавление привычки ----------
@router.message(F.text == "➕ Добавить привычку")
@router.message(Command("addhabit"))
async def add_habit_start(message: types.Message, state: FSMContext):
    """Начать процесс добавления привычки"""
    try:
        await message.answer(
            "📝 <b>Введите название привычки:</b>\n\n"
            "Например: <i>Утренняя зарядка, Пить воду, Читать книгу</i>",
            parse_mode="HTML",
            reply_markup=get_cancel_keyboard()
        )
        await state.set_state(HabitStates.waiting_for_habit_name)
    except Exception as e:
        logger.error(f"Error in add_habit_start: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.", reply_markup=get_main_menu())


@router.message(HabitStates.waiting_for_habit_name)
async def process_habit_name(message: types.Message, state: FSMContext):
    """Обработать название привычки"""
    try:
        if len(message.text) > 100:
            await message.answer("❌ Название слишком длинное. Максимум 100 символов.")
            return

        await state.update_data(name=message.text.strip())
        await message.answer(
            "📋 <b>Добавьте описание (необязательно):</b>\n\n"
            "Можете описать детали или мотивацию для этой привычки",
            parse_mode="HTML",
            reply_markup=get_cancel_keyboard()
        )
        await state.set_state(HabitStates.waiting_for_habit_description)
    except Exception as e:
        logger.error(f"Error in process_habit_name: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте снова.", reply_markup=get_cancel_keyboard())


@router.message(HabitStates.waiting_for_habit_description)
async def process_habit_description(message: types.Message, state: FSMContext):
    """Обработать описание привычки"""
    try:
        await state.update_data(description=message.text.strip())
        await message.answer(
            "⏰ <b>Выберите время напоминания:</b>\n\n"
            "В какое время вам удобнее всего получать напоминания?",
            parse_mode="HTML",
            reply_markup=get_time_selection_keyboard()
        )
        await state.set_state(HabitStates.waiting_for_habit_time)
    except Exception as e:
        logger.error(f"Error in process_habit_description: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте снова.", reply_markup=get_cancel_keyboard())


@router.message(HabitStates.waiting_for_habit_time)
async def process_habit_time(message: types.Message, state: FSMContext):
    """Обработать время напоминания"""
    try:
        valid_times = ["07:00", "08:00", "09:00", "12:00", "15:00", "18:00",
                       "21:00", "22:00", "⏰ Каждый час", "🚫 Без напоминания", "❌ Отмена"]

        if message.text not in valid_times:
            await message.answer("❌ Пожалуйста, выберите время из предложенных вариантов")
            return

        if message.text == "❌ Отмена":
            await state.clear()
            await message.answer("❌ Добавление привычки отменено", reply_markup=get_main_menu())
            return

        await state.update_data(reminder_time=message.text)
        await message.answer(
            "🔄 <b>Выберите частоту выполнения:</b>\n\n"
            "Как часто вы планируете выполнять эту привычку?",
            parse_mode="HTML",
            reply_markup=get_frequency_keyboard()
        )
        await state.set_state(HabitStates.waiting_for_habit_frequency)
    except Exception as e:
        logger.error(f"Error in process_habit_time: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте снова.", reply_markup=get_cancel_keyboard())


@router.message(HabitStates.waiting_for_habit_frequency)
async def process_habit_frequency(message: types.Message, state: FSMContext):
    """Обработать частоту выполнения"""
    try:
        # Определяем frequency_map ПЕРЕД использованием
        frequency_map = {
            "📅 Ежедневно": "daily",
            "🏢 По будням": "weekdays",
            "🏝️ По выходным": "weekends",
            "📆 Раз в неделю": "weekly",
            "🔢 Несколько раз в неделю": "custom"
        }

        valid_frequencies = list(frequency_map.keys()) + ["❌ Отмена"]

        if message.text not in valid_frequencies:
            await message.answer("❌ Пожалуйста, выберите вариант из предложенных")
            return

        if message.text == "❌ Отмена":
            await state.clear()
            await message.answer("❌ Добавление привычки отменено", reply_markup=get_main_menu())
            return

        await state.update_data(frequency=frequency_map.get(message.text, "daily"))
        await state.update_data(emoji="🎯")  # Эмодзи по умолчанию

        data = await state.get_data()

        confirmation_text = f"""
✅ <b>Проверьте данные привычки:</b>

<b>Название:</b> {data['name']}
<b>Описание:</b> {data.get('description', 'нет')}
<b>Время напоминания:</b> {data['reminder_time']}
<b>Частота:</b> {message.text}
<b>Эмодзи:</b> {data['emoji']}

<b>Все верно?</b>
        """

        await message.answer(
            confirmation_text,
            parse_mode="HTML",
            reply_markup=get_confirm_keyboard()
        )
        await state.set_state(HabitStates.waiting_for_habit_confirmation)
    except Exception as e:
        logger.error(f"Error in process_habit_frequency: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте снова.", reply_markup=get_cancel_keyboard())


@router.message(HabitStates.waiting_for_habit_confirmation)
async def process_habit_confirmation(message: types.Message, state: FSMContext):
    """Подтвердить создание привычки"""
    from database.database import add_habit

    try:
        if message.text == "❌ Отмена":
            await state.clear()
            await message.answer("❌ Создание привычки отменено", reply_markup=get_main_menu())
            return

        if message.text == "✅ Подтвердить":
            data = await state.get_data()

            habit_id = add_habit(
                user_id=message.from_user.id,
                name=data['name'],
                description=data.get('description'),
                reminder_time=data['reminder_time'],
                frequency=data['frequency'],
                emoji=data.get('emoji', '🎯')
            )

            if habit_id:
                await message.answer(
                    f"🎉 <b>Привычка \"{data['name']}\" успешно создана!</b>\n\n"
                    f"Теперь я буду напоминать вам о ней в {data['reminder_time']}",
                    parse_mode="HTML",
                    reply_markup=get_main_menu()
                )

                # Планируем напоминание через сервис
                try:
                    from services.reminder_service import schedule_habit_reminder
                    await schedule_habit_reminder(habit_id, data['reminder_time'])
                except ImportError:
                    logger.warning("Reminder service not available")
            else:
                await message.answer(
                    "❌ Не удалось создать привычку. Попробуйте позже.",
                    reply_markup=get_main_menu()
                )

        await state.clear()

    except Exception as e:
        logger.error(f"Error in process_habit_confirmation: {e}")
        await state.clear()
        await message.answer("❌ Произошла ошибка при создании привычки.", reply_markup=get_main_menu())


# ---------- Работа с существующими привычками ----------
@router.callback_query(F.data.startswith("habit_"))
async def show_habit_details(callback: types.CallbackQuery):
    """Показать детали привычки"""
    from database.database import get_habit_by_id

    try:
        habit_id = int(callback.data.split("_")[1])
        habit = get_habit_by_id(habit_id, callback.from_user.id)

        if not habit:
            await callback.answer("❌ Привычка не найдена")
            return

        # Получаем дополнительные данные
        completed_today = habit.get('completed_today', False)
        streak = habit.get('streak', 0)
        reminder_time = habit.get('reminder_time', 'нет')
        created_at = habit.get('created_at', '')

        status = "✅ Выполнено сегодня" if completed_today else "⏳ Ожидает выполнения"

        habit_text = f"""
{habit.get('emoji', '🎯')} <b>{habit['name']}</b>

{habit.get('description', '')}

<b>Статус:</b> {status}
<b>Цепочка:</b> 🔥 {streak} дней
<b>Время напоминания:</b> {reminder_time}
<b>Создана:</b> {str(created_at)[:10] if created_at else 'Неизвестно'}
        """

        await callback.message.edit_text(
            habit_text,
            parse_mode="HTML",
            reply_markup=get_habit_actions_keyboard(habit_id)
        )
        await callback.answer()
    except TelegramBadRequest:
        await callback.answer("❌ Сообщение устарело. Обновите список привычек.")
    except Exception as e:
        logger.error(f"Error in show_habit_details: {e}")
        await callback.answer("❌ Произошла ошибка при загрузке привычки")


@router.callback_query(F.data.startswith("complete_"))
async def complete_habit(callback: types.CallbackQuery):
    """Отметить привычку выполненной"""
    from database.database import mark_habit_completed, get_habit_by_id

    try:
        habit_id = int(callback.data.split("_")[1])

        success = mark_habit_completed(habit_id, callback.from_user.id)

        if success:
            habit = get_habit_by_id(habit_id, callback.from_user.id)
            streak = habit.get('streak', 0) if habit else 0
            await callback.answer(f"✅ Привычка выполнена! Цепочка: {streak} дней")

            # Обновляем сообщение
            if habit:
                status = "✅ Выполнено сегодня"
                habit_text = f"""
{habit.get('emoji', '🎯')} <b>{habit['name']}</b>

{habit.get('description', '')}

<b>Статус:</b> {status}
<b>Цепочка:</b> 🔥 {streak} дней
<b>Время напоминания:</b> {habit.get('reminder_time', 'нет')}

🎉 <b>Поздравляем! Вы поддерживаете цепочку {streak} дней!</b>
                """

                try:
                    await callback.message.edit_text(
                        habit_text,
                        parse_mode="HTML",
                        reply_markup=get_habit_actions_keyboard(habit_id)
                    )
                except TelegramBadRequest:
                    pass  # Сообщение уже обновлено
        else:
            await callback.answer("❌ Уже выполнено сегодня")
    except Exception as e:
        logger.error(f"Error in complete_habit: {e}")
        await callback.answer("❌ Произошла ошибка")


@router.callback_query(F.data.startswith("edit_"))
async def edit_habit_start(callback: types.CallbackQuery, state: FSMContext):
    """Начать редактирование привычки"""
    try:
        habit_id = int(callback.data.split("_")[1])

        await state.update_data(habit_id=habit_id)
        await callback.message.edit_text(
            "✏️ <b>Что вы хотите изменить?</b>",
            parse_mode="HTML",
            reply_markup=get_edit_habit_keyboard(habit_id)  # Передаем habit_id
        )
        await state.set_state(EditHabitStates.waiting_for_edit_field)
        await callback.answer()
    except TelegramBadRequest:
        await callback.answer("❌ Сообщение устарело")
    except Exception as e:
        logger.error(f"Error in edit_habit_start: {e}")
        await callback.answer("❌ Произошла ошибка")


@router.callback_query(F.data.startswith("edit_field_"))
async def edit_field_selected(callback: types.CallbackQuery, state: FSMContext):
    """Обработать выбор поля для редактирования"""
    try:
        field = callback.data.split("_")[2]

        # Получаем habit_id из состояния
        data = await state.get_data()
        habit_id = data.get('habit_id')

        if not habit_id:
            await callback.answer("❌ Ошибка: ID привычки не найден")
            return

        await state.update_data(edit_field=field)

        field_names = {
            "name": "название",
            "description": "описание",
            "reminder_time": "время напоминания",
            "frequency": "частоту",
            "emoji": "эмодзи"
        }

        if field == "emoji":
            await callback.message.edit_text(
                f"🎨 <b>Выберите новый эмодзи для привычки:</b>",
                parse_mode="HTML",
                reply_markup=get_emoji_selection_keyboard(habit_id)  # Передаем habit_id
            )
        else:
            await callback.message.edit_text(
                f"✏️ <b>Введите новое {field_names.get(field, field)}:</b>",
                parse_mode="HTML"
            )

        await state.set_state(EditHabitStates.waiting_for_new_value)
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in edit_field_selected: {e}")
        await callback.answer("❌ Произошла ошибка")


@router.callback_query(F.data.startswith("emoji_"))
async def process_emoji_selection(callback: types.CallbackQuery, state: FSMContext):
    """Обработать выбор эмодзи"""
    from database.database import update_habit

    try:
        emoji = callback.data.split("_")[1]
        data = await state.get_data()
        habit_id = data.get('habit_id')
        field = data.get('edit_field')

        if not habit_id or field != "emoji":
            await callback.answer("❌ Ошибка данных")
            return

        success = update_habit(habit_id, callback.from_user.id, field, emoji)

        if success:
            # Показываем успешное обновление
            await callback.message.edit_text(
                f"✅ Эмодзи обновлен на {emoji}\n\n"
                f"<i>Возвращаемся к просмотру привычки...</i>",
                parse_mode="HTML"
            )

            # Возвращаемся к просмотру привычки
            await show_habit_after_edit(callback, habit_id)
        else:
            await callback.message.edit_text(
                "❌ Не удалось обновить эмодзи",
                parse_mode="HTML"
            )

        await state.clear()
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in process_emoji_selection: {e}")
        await callback.answer("❌ Произошла ошибка")


async def show_habit_after_edit(callback: types.CallbackQuery, habit_id: int):
    """Показать привычку после редактирования"""
    from database.database import get_habit_by_id

    try:
        habit = get_habit_by_id(habit_id, callback.from_user.id)

        if not habit:
            await callback.answer("❌ Привычка не найдена")
            return

        # Получаем дополнительные данные
        completed_today = habit.get('completed_today', False)
        streak = habit.get('streak', 0)
        reminder_time = habit.get('reminder_time', 'нет')
        created_at = habit.get('created_at', '')

        status = "✅ Выполнено сегодня" if completed_today else "⏳ Ожидает выполнения"

        habit_text = f"""
{habit.get('emoji', '🎯')} <b>{habit['name']}</b>

{habit.get('description', '')}

<b>Статус:</b> {status}
<b>Цепочка:</b> 🔥 {streak} дней
<b>Время напоминания:</b> {reminder_time}
<b>Создана:</b> {str(created_at)[:10] if created_at else 'Неизвестно'}

✅ <i>Изменения сохранены!</i>
        """

        await callback.message.edit_text(
            habit_text,
            parse_mode="HTML",
            reply_markup=get_habit_actions_keyboard(habit_id)
        )
    except Exception as e:
        logger.error(f"Error in show_habit_after_edit: {e}")


@router.message(EditHabitStates.waiting_for_new_value)
async def process_new_value(message: types.Message, state: FSMContext):
    """Обработать новое значение для поля"""
    from database.database import update_habit

    try:
        data = await state.get_data()
        habit_id = data.get('habit_id')
        field = data.get('edit_field')

        if not habit_id or not field:
            await state.clear()
            await message.answer("❌ Сессия истекла. Начните редактирование заново.",
                                 reply_markup=get_main_menu())
            return

        # Валидация в зависимости от поля
        if field == "name" and len(message.text) > 100:
            await message.answer("❌ Название слишком длинное. Максимум 100 символов.")
            return

        success = update_habit(habit_id, message.from_user.id, field, message.text.strip())

        if success:
            # Обновляем напоминание если изменилось время
            if field == "reminder_time":
                try:
                    from services.reminder_service import update_habit_reminder
                    await update_habit_reminder(habit_id, message.text.strip())
                except ImportError:
                    logger.warning("Reminder service not available")

            await message.answer(
                "✅ Изменения сохранены!",
                reply_markup=get_main_menu()
            )
        else:
            await message.answer(
                "❌ Не удалось сохранить изменения",
                reply_markup=get_main_menu()
            )

        await state.clear()

    except Exception as e:
        logger.error(f"Error in process_new_value: {e}")
        await state.clear()
        await message.answer("❌ Произошла ошибка при сохранении изменений.",
                             reply_markup=get_main_menu())


@router.callback_query(F.data.startswith("delete_"))
async def delete_habit_start(callback: types.CallbackQuery, state: FSMContext):
    """Начать процесс удаления привычки"""
    from database.database import get_habit_by_id

    try:
        habit_id = int(callback.data.split("_")[1])

        await state.update_data(habit_id=habit_id)

        habit = get_habit_by_id(habit_id, callback.from_user.id)

        if not habit:
            await callback.answer("❌ Привычка не найдена")
            return

        await callback.message.edit_text(
            f"🗑️ <b>Вы уверены, что хотите удалить привычку?</b>\n\n"
            f"<b>{habit.get('emoji', '🎯')} {habit['name']}</b>\n"
            f"🔥 Цепочка: {habit.get('streak', 0)} дней\n\n"
            f"<i>Это действие нельзя отменить!</i>",
            parse_mode="HTML",
            reply_markup=get_confirm_keyboard()
        )
        await state.set_state(DeleteHabitStates.waiting_for_confirmation)
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in delete_habit_start: {e}")
        await callback.answer("❌ Произошла ошибка")


@router.message(DeleteHabitStates.waiting_for_confirmation)
async def delete_habit_confirm(message: types.Message, state: FSMContext):
    """Подтвердить удаление привычки"""
    from database.database import get_habit_by_id, delete_habit

    try:
        if message.text == "❌ Отмена":
            await state.clear()
            await message.answer("❌ Удаление отменено", reply_markup=get_main_menu())
            return

        if message.text == "✅ Подтвердить":
            data = await state.get_data()
            habit_id = data.get('habit_id')

            if not habit_id:
                await state.clear()
                await message.answer("❌ Сессия истекла", reply_markup=get_main_menu())
                return

            habit = get_habit_by_id(habit_id, message.from_user.id)

            if habit:
                # Удаляем напоминание если есть сервис
                try:
                    from services.reminder_service import cancel_habit_reminder
                    await cancel_habit_reminder(habit_id)
                except ImportError:
                    logger.warning("Reminder service not available")

                # Удаляем из БД
                delete_habit(habit_id, message.from_user.id)

                await message.answer(
                    f"🗑️ Привычка \"{habit['name']}\" удалена\n"
                    f"🔥 Ваша цепочка {habit.get('streak', 0)} дней сохранена в истории",
                    reply_markup=get_main_menu()
                )
            else:
                await message.answer("❌ Привычка не найдена", reply_markup=get_main_menu())

        await state.clear()

    except Exception as e:
        logger.error(f"Error in delete_habit_confirm: {e}")
        await state.clear()
        await message.answer("❌ Произошла ошибка при удалении привычки.",
                             reply_markup=get_main_menu())


@router.callback_query(F.data.startswith("stats_habit_"))
async def show_habit_stats(callback: types.CallbackQuery):
    """Показать статистику привычки"""
    from database.database import get_habit_stats, get_habit_by_id

    try:
        habit_id = int(callback.data.split("_")[2])
        stats = get_habit_stats(habit_id, callback.from_user.id)
        habit = get_habit_by_id(habit_id, callback.from_user.id)

        if not stats or not habit:
            await callback.answer("❌ Статистика не найдена")
            return

        stats_text = f"""
📊 <b>Статистика привычки "{habit['name']}"</b>

📈 <b>Выполнено дней:</b> {stats.get('total_completions', 0)}
📅 <b>Успешность:</b> {stats.get('success_rate', 0)}%
🔥 <b>Самая длинная цепь:</b> {stats.get('longest_streak', 0)} дней
📆 <b>Текущая цепь:</b> {stats.get('current_streak', 0)} дней
📊 <b>За последние 7 дней:</b> {stats.get('completions_last_7_days', 0)}/7
        """

        await callback.message.edit_text(
            stats_text,
            parse_mode="HTML",
            reply_markup=get_habit_actions_keyboard(habit_id)
        )
        await callback.answer()
    except TelegramBadRequest:
        await callback.answer("❌ Сообщение устарело")
    except Exception as e:
        logger.error(f"Error in show_habit_stats: {e}")
        await callback.answer("❌ Произошла ошибка при загрузке статистики")


# ---------- Навигация ----------
@router.callback_query(F.data == "back_to_habits")
async def back_to_habits_list(callback: types.CallbackQuery):
    """Вернуться к списку привычек"""
    from database.database import get_user_habits

    try:
        habits = get_user_habits(callback.from_user.id)

        if not habits:
            await callback.message.edit_text(
                "📭 У вас пока нет привычек",
                reply_markup=get_main_menu()
            )
            return

        await callback.message.edit_text(
            "📋 <b>Ваши привычки:</b>",
            parse_mode="HTML",
            reply_markup=get_habits_keyboard(habits)
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in back_to_habits_list: {e}")
        await callback.answer("❌ Произошла ошибка")


@router.callback_query(F.data.startswith("page_"))
async def change_page(callback: types.CallbackQuery):
    """Смена страницы в списке привычек"""
    from database.database import get_user_habits

    try:
        page = int(callback.data.split("_")[1])
        habits = get_user_habits(callback.from_user.id)

        await callback.message.edit_reply_markup(
            reply_markup=get_habits_keyboard(habits, page)
        )
        await callback.answer()
    except TelegramBadRequest:
        await callback.answer("❌ Сообщение устарело")
    except Exception as e:
        logger.error(f"Error in change_page: {e}")
        await callback.answer("❌ Произошла ошибка")


@router.callback_query(F.data == "add_habit")
async def add_habit_from_list(callback: types.CallbackQuery):
    """Добавить привычку из списка"""
    try:
        await callback.message.edit_text(
            "📝 <b>Введите название привычки:</b>",
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in add_habit_from_list: {e}")
        await callback.answer("❌ Произошла ошибка")


@router.callback_query(F.data.startswith("back_to_habit_"))
async def back_to_habit(callback: types.CallbackQuery):
    """Вернуться к просмотру привычки"""
    from database.database import get_habit_by_id

    try:
        habit_id = int(callback.data.split("_")[3])
        habit = get_habit_by_id(habit_id, callback.from_user.id)

        if not habit:
            await callback.answer("❌ Привычка не найдена")
            return

        # Получаем дополнительные данные
        completed_today = habit.get('completed_today', False)
        streak = habit.get('streak', 0)
        reminder_time = habit.get('reminder_time', 'нет')
        created_at = habit.get('created_at', '')

        status = "✅ Выполнено сегодня" if completed_today else "⏳ Ожидает выполнения"

        habit_text = f"""
{habit.get('emoji', '🎯')} <b>{habit['name']}</b>

{habit.get('description', '')}

<b>Статус:</b> {status}
<b>Цепочка:</b> 🔥 {streak} дней
<b>Время напоминания:</b> {reminder_time}
<b>Создана:</b> {str(created_at)[:10] if created_at else 'Неизвестно'}
        """

        await callback.message.edit_text(
            habit_text,
            parse_mode="HTML",
            reply_markup=get_habit_actions_keyboard(habit_id)
        )
        await callback.answer()
    except TelegramBadRequest:
        await callback.answer("❌ Сообщение устарело. Обновите список привычек.")
    except Exception as e:
        logger.error(f"Error in back_to_habit: {e}")
        await callback.answer("❌ Произошла ошибка при загрузке привычки")


@router.callback_query(F.data.startswith("back_to_edit_"))
async def back_to_edit(callback: types.CallbackQuery, state: FSMContext):
    """Вернуться к выбору поля редактирования"""
    try:
        # Получаем habit_id из callback_data
        habit_id = int(callback.data.split("_")[3])

        # Обновляем состояние
        await state.update_data(habit_id=habit_id)

        await callback.message.edit_text(
            "✏️ <b>Что вы хотите изменить?</b>",
            parse_mode="HTML",
            reply_markup=get_edit_habit_keyboard(habit_id)
        )
        await state.set_state(EditHabitStates.waiting_for_edit_field)
        await callback.answer()
    except TelegramBadRequest:
        await callback.answer("❌ Сообщение устарело")
    except Exception as e:
        logger.error(f"Error in back_to_edit: {e}")
        await callback.answer("❌ Произошла ошибка")