import requests
import pandas as pd
import string


# Функция для получения данных с API
def get_meal_data(letter):
    url = f"https://www.themealdb.com/api/json/v1/1/search.php?f={letter}"
    response = requests.get(url)
    return response.json()


# Инициализация пустого DataFrame для хранения данных
columns = ['Meal Name', 'Ingredient', 'Instruction']
data = pd.DataFrame(columns=columns)

# Обход всех букв латинского алфавита
for letter in string.ascii_lowercase:
    meal_data = get_meal_data(letter)

    if meal_data['meals']:
        for meal in meal_data['meals']:
            meal_name = meal['strMeal']
            meal_instr = meal['strInstructions']
            for i in range(1, 21):
                ingredient = meal[f'strIngredient{i}']
                if ingredient and ingredient.strip():
                    new_row = pd.DataFrame({'Meal Name': [meal_name],
                                            'Ingredient': [ingredient],
                                            'Instruction': [meal_instr]})
                    data = pd.concat([data, new_row], ignore_index=True)

# Запись данных в Excel файл
output_path = '/Users/mikhaillevashov/Desktop/Диплом/fitnessBot/server/db/xlsx/meals_ingredients.xlsx'
data.to_excel(output_path, index=False)
print(f"Data has been written to {output_path}")
