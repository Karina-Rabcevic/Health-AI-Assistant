from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from llm_interpreter import get_llm_interpretation, ask_medical_agent
from constants import QUESTIONS, CATEGORICAL_MAPPINGS, OPTIMAL_THRESHOLDS
from utils import predict_heart_disease

router = Router()

class DataCollection(StatesGroup):
    waiting_for_start = State()
    collecting_data = State()

@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    await state.set_state(DataCollection.waiting_for_start)

    await message.answer(
        "❤️ Добро пожаловать в Health AI Assistant!\n\n"
        "Я помогу оценить риск сердечно-сосудистых заболеваний "
        "по вашим ответам на вопросы.\n\n"
        "Нажмите кнопку ниже, чтобы начать.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📝 Ответить на вопросы",
                        callback_data="start_collection"
                    )
                ]
            ]
        )
    )

@router.message(DataCollection.collecting_data)
async def process_answer(message: Message, state: FSMContext):
    user_data = await state.get_data()

    error_msg_id = user_data.get("error_msg_id")

    if error_msg_id:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=error_msg_id
            )
        except Exception:
            pass

        await state.update_data(error_msg_id=None)

    current_question_idx = user_data.get("current_question_idx", 0)
    answers = user_data.get("answers", {})
    message_id = user_data.get("question_message_id")
    
    error_msg_id = user_data.get("error_msg_id")

    if error_msg_id:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=error_msg_id
            )
        except Exception:
            pass

        await state.update_data(error_msg_id=None)
    


    # ПРОВЕРЯЕМ, НЕ ЗАДАЛ ЛИ ПОЛЬЗОВАТЕЛЬ ВОПРОС АГЕНТУ
    

    user_text = message.text.strip()

    if (
        "?" in user_text
        or user_text.lower().startswith((
            "что такое",
            "что значит",
            "что означает",
            "объясни",
            "расскажи",
            "почему",
            "зачем",
            "как понять"
        ))
    ):
        try:
            
            agent_response = await ask_medical_agent(user_text)

            
            agent_message = await message.answer(
                agent_response,
                parse_mode="HTML"
            )

            
            await state.update_data(
                temp_user_msg_id=message.message_id,
                temp_bot_msg_id=agent_message.message_id
            )

        except Exception as e:
            print(f"Ошибка AI-агента: {e}")

            agent_message = await message.answer(
                "⚠️ Не удалось получить ответ от AI-ассистента. "
                "Попробуйте задать вопрос ещё раз."
            )

            await state.update_data(
                temp_user_msg_id=message.message_id,
                temp_bot_msg_id=agent_message.message_id
            )

    
        return


        # УДАЛЯЕМ ПРЕДЫДУЩИЙ ВОПРОС ПОЛЬЗОВАТЕЛЯ И ОТВЕТ АГЕНТА
    

    temp_user_msg_id = user_data.get("temp_user_msg_id")
    temp_bot_msg_id = user_data.get("temp_bot_msg_id")

    if temp_user_msg_id:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=temp_user_msg_id
            )
        except Exception:
            pass

    if temp_bot_msg_id:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=temp_bot_msg_id
            )
        except Exception:
            pass

    await state.update_data(
        temp_user_msg_id=None,
        temp_bot_msg_id=None
    )

    
    # ОБЫЧНАЯ ОБРАБОТКА ОТВЕТА НА ВОПРОС
    

    feature = list(QUESTIONS.keys())[current_question_idx]
    user_input = message.text.strip()

    try:
        if feature in CATEGORICAL_MAPPINGS:

            if user_input.lower() not in CATEGORICAL_MAPPINGS[feature]:
                await message.delete()

                error_message = await message.answer(
                    "Пожалуйста, выберите корректный вариант. "
                    "Попробуйте снова."
                )
                await state.update_data(
                 error_msg_id=error_message.message_id
                )

                return

            answers[feature] = user_input.lower()

        else:
            value = float(user_input)

            if feature == "Age" and (value < 0 or value > 120):
                raise ValueError(
                    "Возраст должен быть от 0 до 120."
                )

            answers[feature] = value

    except ValueError:

        await message.delete()

        error_message = await message.answer(
            "Некорректный ввод. "
            "Пожалуйста, введите число или корректный вариант."
        )
        await state.update_data(
        error_msg_id=error_message.message_id
        )

        return

    
    await message.delete()

    
    # ПЕРЕХОД К СЛЕДУЮЩЕМУ ВОПРОСУ
    

    current_question_idx += 1

    if current_question_idx < len(QUESTIONS):

        await message.bot.edit_message_text(
            text=QUESTIONS[
                list(QUESTIONS.keys())[current_question_idx]
            ],
            chat_id=message.chat.id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="❌ Отменить",
                            callback_data="cancel_collection"
                        )
                    ]
                ]
            )
        )

        await state.update_data(
            current_question_idx=current_question_idx,
            answers=answers,
            question_message_id=message_id,
            temp_user_msg_id=None,
            temp_bot_msg_id=None
        )

    else:

        
        
        

        probability = predict_heart_disease(answers)

        try:

            llm_response = await get_llm_interpretation(
                answers,
                probability
            )

            final_text = (
                f"✅ Обработка завершена.\n\n"
                f"{llm_response}"
            )

        except Exception as e:

            print(f"Ошибка итогового LLM: {e}")

            if probability > OPTIMAL_THRESHOLDS:

                result = (
                    "🚨 Высокий риск сердечных заболеваний. "
                    "Настоятельно рекомендуется обратиться "
                    "к кардиологу для обследования."
                )

            else:

                result = (
                    f"💘 С вероятностью "
                    f"{100 - probability * 100:.1f}% "
                    f"риск сердечных заболеваний низкий."
                )

            final_text = (
                f"Обработка завершена.\n\n"
                f"{result}\n\n"
                f"(Не удалось получить подробные "
                f"рекомендации от ассистента)"
            )

        await message.bot.edit_message_text(
            text=final_text,
            chat_id=message.chat.id,
            message_id=message_id,
            parse_mode="HTML",
            reply_markup=None
        )

        await state.clear()


        
# @router.message(DataCollection.collecting_data)
# async def process_answer(message: Message, state: FSMContext):
#     user_data = await state.get_data()
#     current_question_idx = user_data.get("current_question_idx", 0)
#     answers = user_data.get("answers", {})
#     message_id = user_data.get("question_message_id")
    
#     feature = list(QUESTIONS.keys())[current_question_idx]
#     user_input = message.text.strip()
    
#     try:
#         if feature in CATEGORICAL_MAPPINGS:
#             if user_input.lower() not in CATEGORICAL_MAPPINGS[feature]:
#                 await message.delete()
#                 await message.answer("Пожалуйста, выберите корректный вариант. Попробуйте снова.")
#                 return
#             answers[feature] = user_input.lower()
#         else:
#             value = float(user_input)
#             if feature == "Age" and (value < 0 or value > 120):
#                 raise ValueError("Возраст должен быть от 0 до 120.")
#             answers[feature] = value
#     except ValueError:
#         await message.delete()
#         await message.answer("Некорректный ввод. Пожалуйста, введите число или корректный вариант.")
#         return
    
#     await message.delete()
    
#     current_question_idx += 1
#     if current_question_idx < len(QUESTIONS):
#         await message.bot.edit_message_text(
#             text=QUESTIONS[list(QUESTIONS.keys())[current_question_idx]],
#             chat_id=message.chat.id,
#             message_id=message_id,
#             reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_collection")]])
#         )
#         await state.update_data(
#             current_question_idx=current_question_idx,
#             answers=answers,
#             question_message_id=message_id
#         )
#     else:
#         probability = predict_heart_disease(answers)

#         try:
#             llm_response = await get_llm_interpretation(answers, probability)
#             final_text = f"✅ Обработка завершена.\n\n{llm_response}"
            
#         except Exception as e:
#             if probability > OPTIMAL_THRESHOLDS:
#                 result = "🚨 Высокий риск сердечных заболеваний. Настоятельно рекомендуется обратиться к кардиологу для обследования."
#             else:
#                 result = f"💘 С вероятностью {100 - probability*100:.1f}% риск сердечных заболеваний низкий."
#             final_text = f"Обработка завершена.\n\n{result}\n\n(Не удалось получить подробные рекомендации от ассистента)"
        
#         await message.bot.edit_message_text(
#             text=final_text,
#             chat_id=message.chat.id,
#             message_id=message_id,
#             parse_mode="HTML",
#             reply_markup=None
#         )
#         await state.clear()



