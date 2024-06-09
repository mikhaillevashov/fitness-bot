import pandas as pd
import psycopg2

# Загрузка данных из Excel файла
input_path = '/Users/mikhaillevashov/Desktop/Диплом/fitnessBot/server/db/xlsx/meals_ru.xlsx'
data = pd.read_excel(input_path)

# Подключение к базе данных
conn = psycopg2.connect(
    host="localhost",
    database="fitness_db",
    user='postgres',  # Замените на ваши значения
    password='postgres'  # Замените на ваши значения
)
cur = conn.cursor()


# Функция для проверки наличия записи в таблице и возвращения её id
def get_or_insert_dish(table, column, value, instruction_column, value_instruction):
    cur.execute(f"SELECT id FROM {table} WHERE {column} = %s", (value,))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        cur.execute(f"INSERT INTO {table} ({column}, {instruction_column}) VALUES (%s, %s) RETURNING id", (value, value_instruction))
        conn.commit()
        return cur.fetchone()[0]


# Функция для проверки наличия записи в таблице и возвращения её id
def get_or_insert_product(table, column, value):
    cur.execute(f"SELECT id FROM {table} WHERE {column} = %s", (value,))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        cur.execute(f"INSERT INTO {table} ({column}) VALUES (%s) RETURNING id", (value,))
        conn.commit()
        return cur.fetchone()[0]


# Обработка данных из Excel файла
for index, row in data.iterrows():
    meal_name = row['Meal Name']
    ingredient = row['Ingredient']
    instruction = row['Instruction']

    # Получение id блюда, добавление если не существует
    meal_id = get_or_insert_dish('dishes', 'name', meal_name, 'instruction', instruction)

    # Получение id продукта, добавление если не существует
    product_id = get_or_insert_product('products', 'name', ingredient)

    # Проверка на наличие записи в таблице recipe
    cur.execute("SELECT 1 FROM recipe WHERE dish_id = %s AND product_id = %s", (meal_id, product_id))
    if not cur.fetchone():
        cur.execute("INSERT INTO recipe (dish_id, product_id) VALUES (%s, %s)", (meal_id, product_id))

# Завершение работы с базой данных
conn.commit()
cur.close()
conn.close()

print("Data has been inserted into the database.")
