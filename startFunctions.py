from staticData import GENDER, TARGET, AGE, WEIGHT, HEIGHT, CHANGE_MENU
from staticData import FAVORITE_MEAT, FAVORITE_FRUIT, FAVORITE_CHEESE, FAVORITE_VEGETABLE
from staticData import VALID_GENDERS, VALID_MEATS, VALID_FRUITS, VALID_CHEESES, VALID_VEGETABLES
from staticData import FAVORITE_SPICE, FAVORITE_GRAIN, VALID_SPICES, VALID_GRAINS, VALID_TARGETS
from dbFunctions import get_or_update_user, save_favorite_product

import requests
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler


def main_menu_keyboard():
    keyboard = [
        ['Что мне поесть?', 'Узнать свои данные', 'Изменить данные']
    ]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


def gender_keyboard():
    keyboard = [VALID_GENDERS]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


def target_keyboard():
    keyboard = [VALID_TARGETS]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


def meat_keyboard():
    keyboard = [VALID_MEATS]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


def fruit_keyboard():
    keyboard = [VALID_FRUITS]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


def cheese_keyboard():
    keyboard = [VALID_CHEESES]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


def vegetable_keyboard():
    keyboard = [VALID_VEGETABLES]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


def spice_keyboard():
    keyboard = [VALID_SPICES]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


def grain_keyboard():
    keyboard = [VALID_GRAINS]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    chat_id = update.message.chat_id
    is_registered = await get_or_update_user(chat_id, user_data)
    if is_registered and all(key in user_data for key in
           ['gender', 'age', 'weight', 'height']):
        await update.message.reply_text(
            'Добро пожаловать обратно! Вы уже ввели свои данные. Выберите действие.',
            reply_markup=main_menu_keyboard()
        )
        return CHANGE_MENU
    else:
        await update.message.reply_text(
            'Здравствуйте! Пожалуйста, введите свои антропометрические данные.\n\nКаков ваш пол?',
            reply_markup=gender_keyboard()
        )
        return GENDER


async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text not in VALID_GENDERS:
        await update.message.reply_text('Пожалуйста, выберите корректный пол.', reply_markup=gender_keyboard())
        return GENDER
    context.user_data['gender'] = update.message.text
    await update.message.reply_text('Какая у вас цель?', reply_markup=target_keyboard())
    return TARGET


async def target(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text not in VALID_TARGETS:
        await update.message.reply_text('Пожалуйста, выберите корректную цель.', reply_markup=target_keyboard())
        return TARGET
    context.user_data['target'] = update.message.text
    await update.message.reply_text('Сколько вам лет?', reply_markup=ReplyKeyboardRemove())
    return AGE


async def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        age = int(update.message.text)
        if age < 16 or age > 100:
            raise ValueError
        context.user_data['age'] = age
        await update.message.reply_text('Каков ваш вес (в кг)?')
        return WEIGHT
    except ValueError:
        await update.message.reply_text('Пожалуйста, введите корректный возраст (от 16 до 100 лет).')
        return AGE


async def weight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        weight = int(update.message.text)
        if weight < 40 or weight > 150:
            raise ValueError
        context.user_data['weight'] = weight
        await update.message.reply_text('Каков ваш рост (в см)?')
        return HEIGHT
    except ValueError:
        await update.message.reply_text('Пожалуйста, введите корректный вес (от 40 до 150 кг).')
        return WEIGHT


async def height(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        height = int(update.message.text)
        if height < 140 or height > 220:
            raise ValueError
        context.user_data['height'] = height
        user_data = context.user_data
        gender_code = 'м' if user_data['gender'] == 'Мужской' else 'ж'
        data = {
            'chat_id': update.message.chat_id,
            'gender': gender_code,
            'age': user_data['age'],
            'height': user_data['height'],
            'weight': user_data['weight']
        }
        response = requests.post('http://127.0.0.1:5000/user', json=data)
        if response.status_code == 201:
            await update.message.reply_text('Вы зарегистрировались.\n\n')
        else:
            # Обработка ошибки, если запрос не удался
            await update.message.reply_text('Ошибка при сохранении данных пользователя.')

        await update.message.reply_text('Для определения ваших вкусовых предпочтений, пройдите опрос.\n\n'
                                        'Выберите ваше любимое мясо:', reply_markup=meat_keyboard())
        return FAVORITE_MEAT
    except ValueError:
        await update.message.reply_text('Пожалуйста, введите корректный рост (от 140 до 220 см).')
        return HEIGHT


async def favorite_meat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text not in VALID_MEATS:
        await update.message.reply_text('Пожалуйста, выберите корректное мясо.', reply_markup=meat_keyboard())
        return FAVORITE_MEAT
    context.user_data['favorite_meat'] = update.message.text
    chat_id = update.message.chat_id
    user_data = context.user_data
    save_favorite_product(chat_id, user_data['favorite_meat'])
    await update.message.reply_text('Выберите ваш любимый фрукт:', reply_markup=fruit_keyboard())
    return FAVORITE_FRUIT


async def favorite_fruit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text not in VALID_FRUITS:
        await update.message.reply_text('Пожалуйста, выберите корректный фрукт.', reply_markup=fruit_keyboard())
        return FAVORITE_FRUIT
    context.user_data['favorite_fruit'] = update.message.text
    chat_id = update.message.chat_id
    user_data = context.user_data
    save_favorite_product(chat_id, user_data['favorite_fruit'])
    await update.message.reply_text('Выберите ваш любимый сыр:', reply_markup=cheese_keyboard())
    return FAVORITE_CHEESE


async def favorite_cheese(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text not in VALID_CHEESES:
        await update.message.reply_text('Пожалуйста, выберите корректный сыр.', reply_markup=cheese_keyboard())
        return FAVORITE_CHEESE
    context.user_data['favorite_cheese'] = update.message.text
    chat_id = update.message.chat_id
    user_data = context.user_data
    save_favorite_product(chat_id, user_data['favorite_cheese'])
    await update.message.reply_text('Выберите ваш любимый овощ:', reply_markup=vegetable_keyboard())
    return FAVORITE_VEGETABLE


async def favorite_vegetable(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text not in VALID_VEGETABLES:
        await update.message.reply_text('Пожалуйста, выберите корректный овощ.', reply_markup=vegetable_keyboard())
        return FAVORITE_VEGETABLE
    context.user_data['favorite_vegetable'] = update.message.text
    chat_id = update.message.chat_id
    user_data = context.user_data
    save_favorite_product(chat_id, user_data['favorite_vegetable'])
    await update.message.reply_text('Выберите вашу любимую специю:', reply_markup=spice_keyboard())
    return FAVORITE_SPICE


async def favorite_spice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text not in VALID_SPICES:
        await update.message.reply_text('Пожалуйста, выберите корректную специю.', reply_markup=spice_keyboard())
        return FAVORITE_SPICE
    context.user_data['favorite_spice'] = update.message.text
    chat_id = update.message.chat_id
    user_data = context.user_data
    save_favorite_product(chat_id, user_data['favorite_spice'])
    await update.message.reply_text('Выберите вашу любимую крупу:', reply_markup=grain_keyboard())
    return FAVORITE_GRAIN


async def favorite_grain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text not in VALID_GRAINS:
        await update.message.reply_text('Пожалуйста, выберите корректную крупу.', reply_markup=grain_keyboard())
        return FAVORITE_GRAIN
    context.user_data['favorite_grain'] = update.message.text
    chat_id = update.message.chat_id
    user_data = context.user_data
    save_favorite_product(chat_id, user_data['favorite_grain'])
    await update.message.reply_text(
        f"Ваши данные:\n"
        f"Пол: {user_data['gender']}\n"
        f"Цель: {user_data['target']}\n"
        f"Возраст: {user_data['age']}\n"
        f"Вес: {user_data['weight']} кг\n"
        f"Рост: {user_data['height']} см\n"
        'Вы можете изменить данные или узнать свои данные с помощью команд.',
        reply_markup=main_menu_keyboard()
    )
    return CHANGE_MENU
