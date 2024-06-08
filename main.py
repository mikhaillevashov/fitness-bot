import requests
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

# Токен бота
TELEGRAM_TOKEN = '6812814419:AAFw8WzAQi5FI_beRlbR6OOeJPXT5i-Vfn4'

# Определение состояний для ConversationHandler
(GENDER, AGE, WEIGHT, HEIGHT, FAVORITE_MEAT, FAVORITE_FRUIT, FAVORITE_CHEESE, FAVORITE_VEGETABLE,
 FAVORITE_SPICE, FAVORITE_GRAIN, CHANGE_MENU, CHANGE_GENDER, CHANGE_AGE, CHANGE_WEIGHT,
 CHANGE_HEIGHT) = range(15)

VALID_GENDERS = ['Мужской', 'Женский']
VALID_MEATS = ['Свинина', 'Курица', 'Говядина', 'Рыба']
VALID_FRUITS = ['Банан', 'Яблоко', 'Апельсин']
VALID_CHEESES = ['Чеддер', 'Козий сыр', 'Пармезан', 'Моцарелла']
VALID_VEGETABLES = ['Огурец', 'Помидор', 'Болгарский перец', 'Морковь']
VALID_SPICES = ['Соль', 'Молотый перец', 'Тмин', 'Базилик']
VALID_GRAINS = ['Рис', 'Греча', 'Макароны', 'Картошка']


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


def gender_keyboard():
    keyboard = [VALID_GENDERS]
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


async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text not in VALID_GENDERS:
        await update.message.reply_text('Пожалуйста, выберите корректный пол.', reply_markup=gender_keyboard())
        return GENDER
    context.user_data['gender'] = update.message.text
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


def save_favorite_product(chat_id, product_name):
    url = f"http://127.0.0.1:5000/user/{chat_id}/like_product"
    data = {'product_name': product_name}
    response = requests.post(url, json=data)
    if response.status_code != 201:
        print(f"Failed to add {product_name} for user {chat_id}: {response.status_code}")
        return False
    else:
        print(f"Successfully added {product_name} for user {chat_id}")
        return True


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
        f"Возраст: {user_data['age']}\n"
        f"Вес: {user_data['weight']} кг\n"
        f"Рост: {user_data['height']} см\n"
        'Вы можете изменить данные или узнать свои данные с помощью команд.',
        reply_markup=main_menu_keyboard()
    )
    return CHANGE_MENU


def main_menu_keyboard():
    keyboard = [
        ['Изменить данные', 'Узнать свои данные']
    ]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


def change_menu_keyboard():
    keyboard = [
        ['Пол', 'Возраст', 'Вес', 'Рост'],
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


async def get_or_update_user(chat_id, user_data):
    if not user_data or not all(user_data.get(k) for k in ('gender', 'height', 'age', 'weight')):
        try:
            response = requests.get(f'http://127.0.0.1:5000/user/{chat_id}')
            if response.status_code == 200:
                user_info = response.json()
                user_data['gender'] = user_info.get('gender', '')
                user_data['height'] = user_info.get('height', '')
                user_data['age'] = user_info.get('age', '')
                user_data['weight'] = user_info.get('weight', '')
            else:
                return False  # User not found, prompt registration
        except requests.RequestException as e:
            return False  # Error accessing user data
    return True  # User data fetched successfully


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
    elif text == "Пол":
        await handle_change_gender(update, context)
        return CHANGE_GENDER
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
            WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, weight)],
            HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, height)],
            FAVORITE_MEAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, favorite_meat)],
            FAVORITE_FRUIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, favorite_fruit)],
            FAVORITE_CHEESE: [MessageHandler(filters.TEXT & ~filters.COMMAND, favorite_cheese)],
            FAVORITE_VEGETABLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, favorite_vegetable)],
            FAVORITE_SPICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, favorite_spice)],
            FAVORITE_GRAIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, favorite_grain)],
            CHANGE_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
            CHANGE_GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_change_gender)],
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
