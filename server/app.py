from flask import Flask, request, jsonify
import psycopg2

from prediction.prediction_service import predict_meal

app = Flask(__name__)


def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="fitness_db",
        user='postgres',
        password='postgres'
    )
    return conn


@app.route('/user/<chat_id>', methods=['GET'])
def get_user_by_chat_id(chat_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE chat_id = %s', (chat_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user:
        user_data = {
            'id': user[0],
            'chat_id': user[1],
            'gender': user[2],
            'age': user[3],
            'height': user[4],
            'weight': user[5]
        }
        return jsonify(user_data)
    else:
        return jsonify({'error': 'User not found'}), 404


@app.route('/user', methods=['POST'])
def add_user():
    new_user = request.get_json()
    chat_id = new_user['chat_id']
    gender = new_user['gender']
    age = new_user['age']
    height = new_user['height']
    weight = new_user['weight']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO users (chat_id, gender, age, height, weight) VALUES (%s, %s, %s, %s, %s)',
                (chat_id, gender, age, height, weight))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'User added successfully'}), 201


@app.route('/user/<chat_id>', methods=['PUT'])
def update_user(chat_id):
    user_updates = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE chat_id = %s', (chat_id,))
    user = cur.fetchone()
    if not user:
        cur.close()
        conn.close()
        return jsonify({'error': 'User not found'}), 404

    gender = user_updates.get('gender', user[2])
    age = user_updates.get('age', user[3])
    height = user_updates.get('height', user[4])
    weight = user_updates.get('weight', user[5])

    cur.execute('''
        UPDATE users
        SET gender = %s, age = %s, height = %s, weight = %s
        WHERE chat_id = %s
    ''', (gender, age, height, weight, chat_id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'User updated successfully'})


@app.route('/user/<chat_id>/like_product', methods=['POST'])
def like_product(chat_id):
    data = request.get_json()
    product_name = data['product_name']

    conn = get_db_connection()
    cur = conn.cursor()

    # Получение user_id по chat_id
    cur.execute('SELECT id FROM users WHERE chat_id = %s', (chat_id,))
    user = cur.fetchone()
    if not user:
        cur.close()
        conn.close()
        return jsonify({'error': 'User not found'}), 404

    user_id = user[0]

    # Получение product_id по названию продукта
    cur.execute('SELECT id FROM products WHERE name = %s', (product_name,))
    product = cur.fetchone()
    if not product:
        cur.close()
        conn.close()
        return jsonify({'error': 'Product not found'}), 404

    product_id = product[0]

    # Добавление записи в таблицу liked_products
    try:
        cur.execute('INSERT INTO liked_products (user_id, product_id) VALUES (%s, %s)', (user_id, product_id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Product liked successfully'}), 201
    except psycopg2.IntegrityError:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'error': 'This product is already liked by the user'}), 409


@app.route('/predict_meal/<chat_id>', methods=['GET'])
def get_predicted_meal(chat_id):
    predicted_meal, instruction = predict_meal(chat_id)
    if predicted_meal:
        return jsonify(predicted_meal, instruction)
    else:
        return jsonify({'error': 'No dishes found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
