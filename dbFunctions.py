import requests


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
