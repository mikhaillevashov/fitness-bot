import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="fitness_db",
    user='postgres',
    password='postgres')

cur = conn.cursor()

# Удаление существующих таблиц
cur.execute('DROP TABLE IF EXISTS users, products, dishes, recipe, liked_products;')

# Создание таблицы пользователей
cur.execute('''
    CREATE TABLE users (
        id serial PRIMARY KEY,
        chat_id varchar(50) UNIQUE,
        gender char(1) NOT NULL CHECK (gender IN ('м', 'ж')),
        age integer NOT NULL,
        height integer NOT NULL,
        weight integer NOT NULL
    );
''')

# Создание таблицы продуктов
cur.execute('''
    CREATE TABLE products (
        id serial PRIMARY KEY,
        name varchar(150) NOT NULL
    );
''')

# Создание таблицы блюд
cur.execute('''
    CREATE TABLE dishes (
        id serial PRIMARY KEY,
        name varchar(150) NOT NULL,
        instruction varchar(1000)
    );
''')

# Создание таблицы рецептов
cur.execute('''
    CREATE TABLE recipe (
        dish_id integer REFERENCES dishes(id),
        product_id integer REFERENCES products(id),
        PRIMARY KEY (dish_id, product_id)
    );
''')

# Создание таблицы понравившихся продуктов
cur.execute('''
    CREATE TABLE liked_products (
        user_id integer REFERENCES users(id),
        product_id integer REFERENCES products(id),
        PRIMARY KEY (user_id, product_id)
    );
''')

# Вставка данных в таблицы
cur.execute('INSERT INTO users (chat_id, gender, age, height, weight) VALUES (%s, %s, %s, %s, %s)',
            ('chat12345', 'м', 30, 175, 70))

conn.commit()

cur.close()
conn.close()
