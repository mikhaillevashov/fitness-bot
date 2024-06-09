from joblib import load
import numpy as np


def predict_product(model, data, product_label):
    # Загрузка сохраненной модели
    label_encoder = load('prediction/models/label_encoder.joblib')

    # Перекодирование категориальных признаков новых данных
    # label_encoder = LabelEncoder()
    data['Gender'] = label_encoder.transform(data['Gender'])
    data[product_label] = label_encoder.transform(data[product_label])

    # Преобразование данных в формат массива numpy
    data_array = np.array([data['Gender'], data['Age'], data['Weight'], data['Height'], data[product_label]]).reshape(1, -1)

    # Предсказание на новых данных
    prediction = model.predict(data_array)

    # Раскодирование предсказанного значения
    predicted_product = label_encoder.inverse_transform(prediction)
    print(f'Предсказанный продукт {product_label}: {predicted_product[0]}')

    return predicted_product

