import random

import psycopg2
from joblib import load

from prediction.prediction_function import predict_product

loaded_model_1 = load('prediction/models/best_model_product1.joblib')
loaded_model_2 = load('prediction/models/best_model_product2.joblib')
loaded_model_3 = load('prediction/models/best_model_product3.joblib')
loaded_model_4 = load('prediction/models/best_model_product4.joblib')
loaded_model_5 = load('prediction/models/best_model_product5.joblib')
loaded_model_6 = load('prediction/models/best_model_product6.joblib')

# Словари с моделями и лейблами
models = {
    1: loaded_model_1,
    2: loaded_model_2,
    3: loaded_model_3,
    4: loaded_model_4,
    5: loaded_model_5,
    6: loaded_model_6
}

labels = {
    1: 'Product1',
    2: 'Product2',
    3: 'Product3',
    4: 'Product4',
    5: 'Product5',
    6: 'Product6'
}

products = {
    1: ['Курица', 'Говядина', 'Свинина', 'Рыба'],
    2: ['Банан', 'Апельсин', 'Яблоко'],
    3: ['Пармезан', 'Чеддер', 'Моцарелла', 'Козий сыр'],
    4: ['Огурец', 'Помидор', 'Болгарский перец', 'Морковь'],
    5: ['Базилик', 'Соль', 'Молотый перец', 'Тмин'],
    6: ['Макароны', 'Рис', 'Греча', 'Картошка']
}


def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="fitness_db",
        user='postgres',
        password='postgres'
    )
    return conn


def get_user(chat_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE chat_id = %s', (str(chat_id),))
    user = cur.fetchone()
    cur.close()
    conn.close()
    gender_code = 'Мужской' if user[2] == 'м' else 'Женский'
    user_data = {
        'gender': [gender_code],
        'age': [user[3]],
        'height': [user[4]],
        'weight': [user[5]]
    }
    return user_data


def get_liked_products(chat_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT p.name FROM liked_products lp JOIN users u ON lp.user_id = u.id JOIN products p ON lp.product_id = p.id WHERE u.chat_id = %s;', (str(chat_id),))
    liked_products = cur.fetchall()
    cur.close()
    conn.close()
    liked_products = [product[0] for product in liked_products]
    return liked_products


def predict_products(chat_id):
    random_numbers = random.sample(range(1, 7), 3)
    liked_products = get_liked_products(chat_id)
    user = get_user(chat_id)
    predicted_products = []
    for number in random_numbers:
        model = models[number]
        label = labels[number]
        cat_prod = products[number]
        product = ''
        for pl in liked_products:
            if pl in cat_prod:
                product = pl
                break
        data = {
            'Gender': user['gender'],
            'Age': user['age'],
            'Weight': user['weight'],
            'Height': user['height'],
            label: [product]
        }
        predicted_products.append(predict_product(model, data, label))
    return predicted_products


def predict_meal(chat_id):
    # Connect to the database
    conn = psycopg2.connect(
        host="localhost",
        database="fitness_db",
        user='postgres',
        password='postgres'
    )
    cur = conn.cursor()

    # Get the predicted products
    predicted_products = predict_products(chat_id)
    predicted_products = [item[0] for item in predicted_products]
    print(predicted_products)

    # Query to find dishes containing all three products
    cur.execute('''
        SELECT d.id, d.name, d.instruction
        FROM dishes d
        JOIN recipe r1 ON d.id = r1.dish_id
        JOIN products p1 ON r1.product_id = p1.id
        JOIN recipe r2 ON d.id = r2.dish_id
        JOIN products p2 ON r2.product_id = p2.id
        JOIN recipe r3 ON d.id = r3.dish_id
        JOIN products p3 ON r3.product_id = p3.id
        WHERE p1.name = %s AND p2.name = %s AND p3.name = %s;
    ''', (predicted_products[0], predicted_products[1], predicted_products[2]))

    dishes = cur.fetchall()

    # If no dishes contain all three products, find dishes containing at least two products
    if not dishes:
        cur.execute('''
            SELECT d.id, d.name, d.instruction
            FROM dishes d
            JOIN recipe r1 ON d.id = r1.dish_id
            JOIN products p1 ON r1.product_id = p1.id
            JOIN recipe r2 ON d.id = r2.dish_id
            JOIN products p2 ON r2.product_id = p2.id
            JOIN recipe r3 ON d.id = r3.dish_id
            JOIN products p3 ON r3.product_id = p3.id
            WHERE (p1.name = %s AND p2.name = %s)
               OR (p1.name = %s AND p3.name = %s)
               OR (p2.name = %s AND p3.name = %s);
        ''', (predicted_products[0], predicted_products[1],
              predicted_products[0], predicted_products[2],
              predicted_products[1], predicted_products[2]))
        dishes = cur.fetchall()

    # If no dishes contain at least two products, find dishes containing at least one product
    if not dishes:
        cur.execute('''
            SELECT d.id, d.name, d.instruction
            FROM dishes d
            JOIN recipe r1 ON d.id = r1.dish_id
            JOIN products p1 ON r1.product_id = p1.id
            JOIN recipe r2 ON d.id = r2.dish_id
            JOIN products p2 ON r2.product_id = p2.id
            JOIN recipe r3 ON d.id = r3.dish_id
            JOIN products p3 ON r3.product_id = p3.id
            WHERE p1.name = %s
               OR p2.name = %s
               OR p3.name = %s;
        ''', (predicted_products[0], predicted_products[1], predicted_products[2]))
        dishes = cur.fetchall()

    # If no dishes contain any of the products, select a random dish
    if not dishes:
        cur.execute('SELECT id, name, instruction FROM dishes ORDER BY RANDOM() LIMIT 1;')
        dishes = cur.fetchall()

    cur.close()
    conn.close()

    # Randomly select a dish from the filtered list
    if dishes:
        selected_dish = random.choice(dishes)
        return selected_dish[1], selected_dish[2]
    else:
        return None