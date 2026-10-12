BOT_TOKEN = "YOUR_TOKEN_HERE"

OPENROUTER_API_KEY = "YOUR_OPENROUTER_API_KEY"
OPENROUTER_MODEL = "openai/gpt-4o-mini"

OPTIMAL_THRESHOLDS = 0.43

QUESTIONS = {
    "Age": "Сколько Вам лет? (от 0 до 120)",
    "Gender": "Какой у Вас пол? (м/ж)",
    "Blood Pressure": "Какое у Вас артериальное давление в покое? (мм рт.ст.)",
    "Cholesterol Level": "Какой Ваш уровень холестерина в крови? (мг/дл)",
    "Exercise Habits": "У Вас активные привычки к физическим упражнениям? (нет/нормально/да)",
    "Smoking": "Вы курите? (да/нет)",
    "Family Heart Disease": "Есть ли у Вашей семьи врождённые сердечные заболевания? (да/нет)",
    "Diabetes": "Есть ли у Вас сахарный диабет? (да/нет)",
    "BMI": "Какой у Вас индекс массы тела?",
    "High Blood Pressure": "У Вас высокое кровяное давление? (да/нет)",
    "Low HDL Cholesterol": "У Вас низкий уровень холестерина ЛПВП? (да/нет)",
    "High LDL Cholesterol": "У Вас высокий уровень холестерина ЛПВП? (да/нет)",
    "Alcohol Consumption": "Часто ли Вы употребляете алкоголь? (не пью/нормально/часто)",
    "Stress Level": "Часто ли Вы стрессуете? (нет/нормально/часто)",
    "Sleep Hours": "Сколько часов в сутки Вы спите?",
    "Sugar Consumption": "Много ли сахара Вы употребляете? (нет/нормально/да)",
    "Triglyceride Level": "Какой у Вас уровень триглицеридов?",
    "Fasting Blood Sugar": "Какой у Вас уровень сахара в крови натощак?",
    "CRP Level": "Какой у Вас уровень C-реактивных белков?",
    "Homocysteine Level": "Какой у Вас уровень гомоцистеина?",
}

CATEGORICAL_MAPPINGS = {
    "Gender": {"м": 1.0, "ж": 0.0},
    "Exercise Habits": {"нет": 0.0, "нормально": 0.5, "да": 1.0},
    "Smoking": {"да": 1.0, "нет": 0.0},
    "Family Heart Disease": {"да": 1.0, "нет": 0.0},
    "Diabetes": {"да": 1.0, "нет": 0.0},
    "High Blood Pressure": {"да": 1.0, "нет": 0.0},
    "Low HDL Cholesterol": {"да": 1.0, "нет": 0.0},
    "High LDL Cholesterol": {"да": 1.0, "нет": 0.0},
    "Alcohol Consumption": {"часто": 0.0, "не пью": 0.5, "нормально": 1.0},
    "Stress Level": {"часто": 0.0, "нет": 0.5, "нормально": 1.0},
    "Sugar Consumption": {"да": 0.0, "нет": 0.5, "нормально": 1.0},
}