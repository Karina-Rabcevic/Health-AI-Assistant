from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from handlers import DataCollection
from constants import QUESTIONS

router = Router()

@router.callback_query(lambda c: c.data == "start_collection")
async def start_collection(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    sent_message = await callback.message.answer(
        text=QUESTIONS[list(QUESTIONS.keys())[0]],
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_collection")]])
    )
    await state.set_state(DataCollection.collecting_data)
    await state.update_data(
        current_question_idx=0,
        answers={},
        question_message_id=sent_message.message_id
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "cancel_collection")
async def cancel_collection(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        text="Сбор данных отменен. Выберите способ ввода данных:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard = [
            [InlineKeyboardButton(text="📝 Ответить на вопросы", callback_data="start_collection")]
        ])
    )
    await state.set_state(DataCollection.waiting_for_start)
    await callback.answer()