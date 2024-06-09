import pandas as pd
import psycopg2


# Функция для подключения к базе данных
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="fitness_db",
        user='postgres',
        password='postgres'
    )
    return conn


# Чтение данных из Excel файла
file_path = '/Users/mikhaillevashov/Desktop/Диплом/fitnessBot/server/db/xlsx/dataset.xlsx'
data = pd.read_excel(file_path)

# Подключение к базе данных
conn = get_db_connection()
cur = conn.cursor()

# Обработка данных
for index, row in data.iterrows():
    gender = row.iloc[1]
    age = int(row.iloc[2])
    weight = float(row.iloc[3])
    height = float(row.iloc[4])
    favorite_products = row.iloc[5:]

    if gender.lower() in ['мужской', 'м']:
        gender = 'м'
    elif gender.lower() in ['женский', 'ж']:
        gender = 'ж'
    else:
        raise ValueError(f"Invalid gender value: {gender}")

    # Добавление пользователя
    cur.execute('INSERT INTO users (chat_id, gender, age, height, weight) VALUES (%s, %s, %s, %s, %s) RETURNING id',
                (None, gender, age, height, weight))
    user_id = cur.fetchone()[0]

    # Добавление любимых продуктов и заполнение таблицы liked_products
    for product_name in favorite_products:
        if pd.notna(product_name):  # Проверка, что продукт не является NaN
            product_name = product_name.strip()  # Удаление лишних пробелов
            # Проверка наличия продукта в таблице products
            cur.execute('SELECT id FROM products WHERE name = %s', (product_name,))
            product = cur.fetchone()
            if product is None:
                # Добавление нового продукта
                cur.execute('INSERT INTO products (name) VALUES (%s) RETURNING id', (product_name,))
                product_id = cur.fetchone()[0]
            else:
                product_id = product[0]

            # Добавление записи в таблицу liked_products
            cur.execute('INSERT INTO liked_products (user_id, product_id) VALUES (%s, %s)', (user_id, product_id))

# Подтверждение изменений и закрытие соединения
conn.commit()
cur.close()
conn.close()
