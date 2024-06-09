import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, KFold, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score

from joblib import dump

if __name__ == '__main__':
    # Загрузка данных
    data = pd.read_excel('dataset.xlsx')

    # Переименование столбцов
    data = data.rename(columns={
        'Отметка времени': 'Timestamp',
        'Ваш пол': 'Gender',
        'Ваш возраст': 'Age',
        'Ваш вес': 'Weight',
        'Ваш рост': 'Height',
        'Выберите один': 'Product1',
        'Выберите один.1': 'Product2',
        'Выберите один.2': 'Product3',
        'Выберите один.3': 'Product4',
        'Выберите один.4': 'Product5',
        'Выберите один.5': 'Product6'
    })

    # Удаление ненужных столбцов
    data = data.drop(columns=['Timestamp'])

    # Кодирование категориальных признаков
    label_encoder = LabelEncoder()
    label_encoder.fit_transform(['Мужской', 'Женский',
                                 'Курица', 'Свинина', 'Говядина', 'Рыба',
                                 'Греча', 'Картошка', 'Макароны', 'Рис',
                                 'Банан', 'Апельсин', 'Яблоко',
                                 'Пармезан', 'Чеддер', 'Моцарелла',
                                 'Козий сыр', 'Огурец', 'Помидор', 'Болгарский перец', 'Морковь',
                                 'Молотый перец', 'Базилик', 'Соль', 'Тмин'])

    data['Gender'] = label_encoder.transform(data['Gender'])
    data['Product1'] = label_encoder.transform(data['Product1'])
    data['Product2'] = label_encoder.transform(data['Product2'])
    data['Product3'] = label_encoder.transform(data['Product3'])
    data['Product4'] = label_encoder.transform(data['Product4'])
    data['Product5'] = label_encoder.transform(data['Product5'])
    data['Product6'] = label_encoder.transform(data['Product6'])

    # Разделение на признаки и целевую переменную
    X = data[['Gender', 'Age', 'Weight', 'Height', 'Product3']]
    y = data['Product4']

    # Разделение на обучающую и тестовую выборки
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

    # Настройка параметров для GridSearchCV
    param_grid = {
        'randomforestclassifier__n_estimators': [50, 100, 200],
        'randomforestclassifier__max_depth': [None, 10, 20, 30],
        'randomforestclassifier__min_samples_split': [2, 5, 10]
    }

    # Создание пайплайна для масштабирования данных и обучения модели
    pipeline = make_pipeline(StandardScaler(), RandomForestClassifier(random_state=1))

    # Настройка GridSearchCV
    grid_search = GridSearchCV(pipeline, param_grid, cv=5, scoring='accuracy')
    grid_search.fit(X_train, y_train)

    # Лучшая модель
    best_model = grid_search.best_estimator_

    # Предсказания на тестовой выборке
    y_pred = best_model.predict(X_test)

    # Оценка точности на тестовой выборке
    accuracy = accuracy_score(y_test, y_pred)
    print(f'Точность на тестовой выборке (Продукт 6): {accuracy * 100:.2f}%')

    # Перекрестная проверка с лучшей моделью
    kfold = KFold(n_splits=5, shuffle=True, random_state=1)
    cross_val_scores = cross_val_score(best_model, X, y, cv=kfold, scoring='accuracy')

    # Средняя точность и стандартное отклонение
    mean_accuracy = cross_val_scores.mean()
    std_accuracy = cross_val_scores.std()

    print(f'Средняя точность с перекрестной проверкой (Продукт 6): {mean_accuracy * 100:.2f}%')
    print(f'Стандартное отклонение: {std_accuracy * 100:.2f}%')

    # Сохранение лучшей модели в файл
    dump(best_model, 'best_model_product4.joblib')
