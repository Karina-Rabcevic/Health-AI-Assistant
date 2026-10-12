import httpx

from constants import OPENROUTER_API_KEY, OPENROUTER_MODEL


async def get_llm_interpretation(extracted_data, probability):
    """
    Получает от AI интерпретацию результата после заполнения всей анкеты.
    """

    risk_percent = probability * 100

    system_prompt = """
Ты — медицинский информационный ассистент Telegram-бота.

Твоя задача — объяснить пользователю результат оценки риска
сердечно-сосудистых заболеваний на основе переданных данных.

Правила:
- Отвечай только на русском языке.
- Не ставь диагноз.
- Не утверждай, что у пользователя есть заболевание.
- Объясняй результат простыми и понятными словами.
- Укажи уровень риска.
- Дай 3–5 общих рекомендаций по здоровому образу жизни.
- Если риск высокий, рекомендуй обратиться к врачу.
- Не пугай пользователя и не делай категоричных медицинских выводов.
- В конце обязательно укажи, что оценка является ориентировочной
  и не заменяет консультацию врача.
- Не используй Markdown.
- Для форматирования используй только поддерживаемые Telegram HTML-теги:
  <b>, <strong>, <i>, <em>, <u>.
- Не используй <br>, ``` или другие HTML-теги.
"""

    user_prompt = f"""
Данные пользователя:

{extracted_data}

Расчётная вероятность риска:
{risk_percent:.1f}%

Проанализируй результат и дай понятное объяснение пользователю.
"""

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "temperature": 0.4,
        "max_tokens": 700
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://your-telegram-bot",
        "X-Title": "HeartDiseaseTelegramBot",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
                headers=headers
            )

        if response.status_code != 200:
            print(
                "OpenRouter error:",
                response.status_code,
                response.text
            )
            raise Exception(
                f"OpenRouter returned status {response.status_code}"
            )

        data = response.json()

        return data["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print("Ошибка при обращении к OpenRouter:", e)
        raise


async def ask_medical_agent(question: str) -> str:
    """
    Краткий медицинский справочник для вопросов во время анкеты.
    """

    system_prompt = """
Ты — краткий медицинский справочник в Telegram-боте.

Пользователь задаёт вопрос о показателе здоровья.
Отвечай ОЧЕНЬ КРАТКО — максимум 2–3 строки.

Формат ответа:

<b>Что это:</b> одно короткое объяснение.
<b>Норма:</b> диапазон или ориентировочное значение с единицами измерения.

Если для показателя нет единой числовой нормы, напиши кратко:
<b>Норма:</b> зависит от возраста, пола и других факторов.

ОБЯЗАТЕЛЬНО указывай числовой диапазон или ориентир,
если для показателя существует общепринятое справочное значение.

Основные справочные значения:

Артериальное давление:
около 120/80 мм рт. ст. — ориентир оптимального давления.
Обычно нормальным считают менее 120/80 мм рт. ст.

Общий холестерин:
желательно менее 200 мг/дл (менее 5,2 ммоль/л).

ЛПНП (LDL):
желательно менее 100 мг/дл (менее 2,6 ммоль/л).
Целевой уровень может зависеть от сердечно-сосудистого риска.

ЛПВП (HDL):
обычно желательно не менее 40 мг/дл у мужчин
и не менее 50 мг/дл у женщин.

Триглицериды:
менее 150 мг/дл (менее 1,7 ммоль/л).

Глюкоза натощак:
примерно 70–99 мг/дл (3,9–5,5 ммоль/л).

ИМТ (BMI):
18,5–24,9 кг/м² — нормальный диапазон.

Сон:
для большинства взрослых 7–9 часов в сутки.

Физическая активность:
не менее 150 минут умеренной активности в неделю.

Курение:
безопасного уровня употребления табака нет; оптимально — 0.

Алкоголь:
безопасного универсального уровня для всех людей нет.

CRP:
обычный C-реактивный белок обычно менее 10 мг/л,
но интерпретация зависит от ситуации.

Гомоцистеин:
ориентировочно 5–15 мкмоль/л.

Для возраста, пола, стресса и других показателей,
для которых нет одной универсальной нормы,
не придумывай диапазон.

ВАЖНЫЕ ПРАВИЛА:
- Только русский язык.
- Максимум 2–3 строки.
- Никаких длинных объяснений.
- Не повторяй вопрос пользователя.
- Не ставь диагноз.
- Не делай персональных медицинских выводов.
- Если есть числовая норма — обязательно укажи её.
- Всегда указывай единицы измерения.
- Используй только Telegram HTML:
  <b>, <strong>, <i>, <em>, <u>.
- Не используй Markdown.
- Не используй <br>.
- Не используй ```.

ВАЖНО:
- Никогда не используй символы < и > в ответе.
- Вместо них используй слова «ниже» и «выше».
- Например, пиши «ниже 200 мг/дл», а не «< 200 мг/дл». 

Пример:

Вопрос: Что такое холестерин?

Ответ:
<b>Холестерин</b> — вещество, необходимое организму для работы клеток и гормонов.
<b>Норма:</b> общий холестерин желательно < 200 мг/дл (< 5,2 ммоль/л).

Вопрос: Что такое давление?

Ответ:
<b>Давление</b> — сила, с которой кровь давит на стенки сосудов.
<b>Норма:</b> около 120/80 мм рт. ст.

Вопрос: Что такое ИМТ?

Ответ:
<b>ИМТ</b> — показатель соотношения веса и роста.
<b>Норма:</b> 18,5–24,9 кг/м².
"""

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "temperature": 0.2,
        "max_tokens": 180
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://your-telegram-bot",
        "X-Title": "HeartDiseaseTelegramBot",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
                headers=headers
            )

        if response.status_code != 200:
            print(
                "OpenRouter agent error:",
                response.status_code,
                response.text
            )
            raise Exception(
                f"OpenRouter returned status {response.status_code}"
            )

        data = response.json()

        return data["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print("Ошибка AI-агента:", e)
        raise


# import httpx
# from typing import Dict, Any

# from constants import OPTIMAL_THRESHOLDS, OPENROUTER_API_KEY, OPENROUTER_MODEL

# async def get_llm_interpretation(extracted_data: Dict[str, Any], probability: float) -> str:
#     """
#     Формирует интерпретацию + рекомендации через LLM.
#     Возвращает готовый текст для пользователя.
#     """
    
#     risk_level = "высокий" if probability > OPTIMAL_THRESHOLDS else "низкий"
#     risk_percent = f"{probability * 100:.1f}%"

#     user_info = "\n".join([f"- **{k}**: {v}" for k, v in extracted_data.items()])

#     system_prompt = """Ты — вежливый, эмпатичный и профессиональный медицинский ассистент, специализирующийся на сердечно-сосудистых заболеваниях.
# Ты НЕ ставишь диагноз и НЕ заменяешь врача.

# Правила ответа:
# - Отвечай **только на русском языке**.
# - Используй **только разрешённые Telegram HTML-теги**: <b>, <strong>, <i>, <em>, <u>, <ins>, <s>, <strike>, <del>.
# - **Запрещено** использовать: <div>, <p>, <ul>, <li>, <br>, <span>, <h1>, <h2> и любые другие теги.
# - Для выделения важного используй <b>текст</b> или <strong>текст</strong>.
# - Для списков используй простой текст с символами:
#   • Первый пункт
#   • Второй пункт
# - Не используй Markdown (** или *).
# - Начинай с эмпатии.
# - Чётко укажи уровень риска и вероятность в процентах.
# - Дай 3–5 конкретных, выполнимых рекомендаций.
# - Обязательно посоветуй обратиться к врачу при повышенном риске.
# - В конце добавь: "Это общая информация. Только врач может дать персонализированные рекомендации."

# Отвечай в чистом тексте с разрешёнными HTML-тегами. Не оборачивай ответ в ```html."""

#     user_prompt = f"""Данные пользователя:
# {user_info}

# Вероятность сердечных заболеваний по модели машинного обучения: {risk_percent} ({risk_level} риск).

# Сформируй полный, красивый и понятный ответ для пользователя."""

#     payload = {
#         "model": OPENROUTER_MODEL,
#         "messages": [
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt}
#         ],
#         "temperature": 0.7,
#         "max_tokens": 800
#     }

#     headers = {
#         "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#         "HTTP-Referer": "https://your-telegram-bot",   
#         "X-Title": "HeartDiseaseTelegramBot",
#         "Content-Type": "application/json"
#     }

#     async with httpx.AsyncClient(timeout=30.0) as client:
#         response = await client.post(
#             "https://openrouter.ai/api/v1/chat/completions",
#             json=payload,
#             headers=headers
#         )
        
#         if response.status_code != 200:
#             error_text = response.text
#             return f"⚠️ Не удалось получить интерпретацию от ИИ. Пожалуйста, попробуйте позже.\n\nТехническая ошибка: {error_text[:200]}"

#         data = response.json()
#         llm_text = data["choices"][0]["message"]["content"].strip()
        
#         return llm_text