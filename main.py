from startFunctions import start, gender, target, height, weight, age, favorite_fruit
from startFunctions import favorite_meat, favorite_vegetable, favorite_spice, gender_keyboard
from startFunctions import favorite_cheese, favorite_grain, main_menu_keyboard, target_keyboard
from staticData import GENDER, TARGET, AGE, WEIGHT, HEIGHT, CHANGE_MENU, CHANGE_AGE, CHANGE_WEIGHT, CHANGE_HEIGHT
from staticData import FAVORITE_MEAT, FAVORITE_FRUIT, FAVORITE_CHEESE, FAVORITE_VEGETABLE, CHANGE_GENDER, VALID_TARGETS
from staticData import FAVORITE_SPICE, FAVORITE_GRAIN, VALID_GENDERS, VALID_ANSWERS, POLL_RESPONSE, SUGGEST_FOOD, CHANGE_TARGET
from dbFunctions import get_or_update_user

import requests
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

# Токен бота
TELEGRAM_TOKEN = '6812814419:AAFw8WzAQi5FI_beRlbR6OOeJPXT5i-Vfn4'


def feedback_keyboard():
    keyboard = [VALID_ANSWERS]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


async def suggest_food(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = context.user_data
    favorite_meat = user_data.get('favorite_meat', 'мясо')
    favorite_fruit = user_data.get('favorite_fruit', 'фрукт')
    favorite_cheese = user_data.get('favorite_cheese', 'сыр')
    favorite_vegetable = user_data.get('favorite_vegetable', 'овощ')
    favorite_spice = user_data.get('favorite_spice', 'специю')
    favorite_grain = user_data.get('favorite_grain', 'крупу')

    chat_id = update.message.chat_id
    url = f"http://127.0.0.1:5000/predict_meal/{chat_id}"
    response = requests.get(url)
    meal = response.json()
    suggestion = (f"Предлагаем вам попробовать блюдо <b>{meal}</b> с парашой. ")
    await update.message.reply_text(suggestion, reply_markup=feedback_keyboard(), parse_mode='HTML')
    return POLL_RESPONSE


async def poll_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    answer = update.message.text
    if answer == "Да":
        await update.message.reply_text("Рад, что вам понравилось!", reply_markup=main_menu_keyboard())
    elif answer == "Нет":
        await update.message.reply_text("Жаль, что вам не понравилось.", reply_markup=main_menu_keyboard())
    return CHANGE_MENU


def change_menu_keyboard():
    keyboard = [
        ['Пол', 'Цель'],
        ['Возраст', 'Вес', 'Рост'],
        ['Назад']
    ]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


async def change_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("IN")
    await update.message.reply_text('Выберите, что вы хотите изменить:', reply_markup=change_menu_keyboard())
    return CHANGE_MENU


async def get_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = context.user_data
    chat_id = update.message.chat_id
    await get_or_update_user(chat_id, user_data)
    data = (
        f"Ваши данные:\n"
        f"Пол: {user_data.get('gender', 'Не указан')}\n"
        f"Цель: {user_data.get('target', 'Не указана')}\n"
        f"Возраст: {user_data.get('age', 'Не указан')}\n"
        f"Вес: {user_data.get('weight', 'Не указан')} кг\n"
        f"Рост: {user_data.get('height', 'Не указан')} см\n"
    )
    await update.message.reply_text(data, reply_markup=main_menu_keyboard())


async def handle_change_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text not in VALID_GENDERS:
        await update.message.reply_text('Пожалуйста, выберите корректный пол.', reply_markup=gender_keyboard())
        return CHANGE_GENDER

    context.user_data['gender'] = update.message.text
    user_data = context.user_data
    gender_code = 'м' if user_data['gender'] == 'Мужской' else 'ж'
    data = {
        'gender': gender_code,
        'age': user_data['age'],
        'height': user_data['height'],
        'weight': user_data['weight']
    }
    response = requests.put(f'http://127.0.0.1:5000/user/{update.message.chat_id}', json=data)

    # Проверяем успешность запроса
    if response.status_code == 200:
        await update.message.reply_text('Пол успешно обновлен.', reply_markup=change_menu_keyboard())
        return CHANGE_MENU
    else:
        # Обработка ошибки, если запрос не удался
        await update.message.reply_text('Ошибка при обновлении данных пользователя.')


async def handle_change_target(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text not in VALID_TARGETS:
        await update.message.reply_text('Пожалуйста, выберите корректную цель.', reply_markup=target_keyboard())
        return CHANGE_TARGET
    else:
        context.user_data['target'] = update.message.text
        await update.message.reply_text('Цель успешно обновлена.', reply_markup=change_menu_keyboard())
        return CHANGE_MENU


async def handle_change_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        age = int(update.message.text)
        if age < 16 or age > 100:
            raise ValueError

        context.user_data['age'] = age
        user_data = context.user_data
        gender_code = 'м' if user_data['gender'] == 'Мужской' else 'ж'
        data = {
            'gender': gender_code,
            'age': user_data['age'],
            'height': user_data['height'],
            'weight': user_data['weight']
        }
        response = requests.put(f'http://127.0.0.1:5000/user/{update.message.chat_id}', json=data)

        if response.status_code == 200:
            await update.message.reply_text('Возраст успешно обновлен.', reply_markup=change_menu_keyboard())
            return CHANGE_MENU
        else:
            await update.message.reply_text('Ошибка при обновлении данных пользователя.')
            return CHANGE_AGE

    except ValueError:
        await update.message.reply_text('Пожалуйста, введите корректный возраст (от 16 до 100 лет).')
        return CHANGE_AGE


async def handle_change_weight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        weight = int(update.message.text)
        if weight < 40 or weight > 150:
            raise ValueError

        context.user_data['weight'] = weight
        user_data = context.user_data
        gender_code = 'м' if user_data['gender'] == 'Мужской' else 'ж'
        data = {
            'gender': gender_code,
            'age': user_data['age'],
            'height': user_data['height'],
            'weight': user_data['weight']
        }
        response = requests.put(f'http://127.0.0.1:5000/user/{update.message.chat_id}', json=data)

        if response.status_code == 200:
            await update.message.reply_text('Вес успешно обновлен.', reply_markup=change_menu_keyboard())
            return CHANGE_MENU
        else:
            await update.message.reply_text('Ошибка при обновлении данных пользователя.')
            return CHANGE_WEIGHT

    except ValueError:
        await update.message.reply_text('Пожалуйста, введите корректный вес (от 40 до 150 кг).')
        return CHANGE_WEIGHT


async def handle_change_height(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        height = int(update.message.text)
        if height < 140 or height > 220:
            raise ValueError

        context.user_data['height'] = height
        user_data = context.user_data
        gender_code = 'м' if user_data['gender'] == 'Мужской' else 'ж'
        data = {
            'gender': gender_code,
            'age': user_data['age'],
            'height': user_data['height'],
            'weight': user_data['weight']
        }
        response = requests.put(f'http://127.0.0.1:5000/user/{update.message.chat_id}', json=data)

        if response.status_code == 200:
            await update.message.reply_text('Рост успешно обновлен.', reply_markup=change_menu_keyboard())
            return CHANGE_MENU
        else:
            await update.message.reply_text('Ошибка при обновлении данных пользователя.')
            return CHANGE_HEIGHT

    except ValueError:
        await update.message.reply_text('Пожалуйста, введите корректный рост (от 140 до 220 см).')
        return CHANGE_HEIGHT


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    print(f'GOT: {text}')

    chat_id = update.message.chat_id
    user_data = context.user_data

    if not all(key in user_data for key in ['gender', 'age', 'weight', 'height']):
        await get_or_update_user(chat_id, user_data)

    if text == "Изменить данные":
        await change_data(update, context)
    elif text == "Узнать свои данные":
        await get_user_data(update, context)
    elif text == "Что мне поесть?":
        await suggest_food(update, context)
        return POLL_RESPONSE
    elif text == "Пол":
        await handle_change_gender(update, context)
        return CHANGE_GENDER
    elif text == "Цель":
        await handle_change_target(update, context)
        return CHANGE_TARGET
    elif text == "Возраст":
        await handle_change_age(update, context)
        return CHANGE_AGE
    elif text == "Вес":
        await handle_change_weight(update, context)
        return CHANGE_WEIGHT
    elif text == "Рост":
        await handle_change_height(update, context)
        return CHANGE_HEIGHT
    elif text == "Назад":
        await update.message.reply_text('Выберите действие:', reply_markup=main_menu_keyboard())
    else:
        await update.message.reply_text('Неизвестная команда. Пожалуйста, выберите действие из меню.',
                                        reply_markup=main_menu_keyboard())


def main() -> None:
    # Создание объекта Application и передача ему токена бота
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Создание ConversationHandler для ввода и изменения антропометрических данных
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            TARGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, target)],
            WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, weight)],
            HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, height)],
            FAVORITE_MEAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, favorite_meat)],
            FAVORITE_FRUIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, favorite_fruit)],
            FAVORITE_CHEESE: [MessageHandler(filters.TEXT & ~filters.COMMAND, favorite_cheese)],
            FAVORITE_VEGETABLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, favorite_vegetable)],
            FAVORITE_SPICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, favorite_spice)],
            FAVORITE_GRAIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, favorite_grain)],
            SUGGEST_FOOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, suggest_food)],
            POLL_RESPONSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, poll_response)],
            CHANGE_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
            CHANGE_GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_change_gender)],
            CHANGE_TARGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_change_target)],
            CHANGE_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_change_age)],
            CHANGE_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_change_weight)],
            CHANGE_HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_change_height)]
        },
        fallbacks=[CommandHandler('start', start)],
    )

    # Добавление обработчиков в приложение
    application.add_handler(conv_handler)

    # Запуск приложения
    application.run_polling()


if __name__ == '__main__':
    main()
