# Libraries
import numpy as np
from keras.layers import Dense
from keras.models import Sequential
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

# Internal
from apps.django_projects.core import selectors
from apps.prediction.utils import transform_multipliers_to_data

# from keras.losses import


def create_sequences(data, window_size, threshold):
    X = []
    y = []
    for i in range(len(data) - window_size):
        X.append(data[i : i + window_size])  # noqa
        y.append(1 if data[i + window_size] >= threshold else 0)
    return np.array(X), np.array(y)


def create_model(input_dim):
    model = Sequential()
    model.add(Dense(32, input_dim=input_dim, activation="relu"))
    model.add(Dense(16, activation="relu"))
    model.add(Dense(1, activation="sigmoid"))

    model.compile(
        loss="binary_crossentropy",
        optimizer=Adam(learning_rate=0.001),
        metrics=["accuracy"],
    )
    return model


def test_():
    """
    from apps.prediction.test_next_number import test_
    test_()
    """
    # Datos de ejemplo
    data = selectors.get_last_multipliers(home_bet_id=2)
    data = transform_multipliers_to_data(data)
    threshold = 2
    window_size = 5

    # Crear secuencias y etiquetas
    X, y = create_sequences(data, window_size, threshold)

    # Normalizar y dividir los datos
    scaler = MinMaxScaler()
    X = scaler.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Crear y entrenar el modelo
    input_dim = X_train.shape[1]
    model = create_model(input_dim)
    model.fit(X_train, y_train, epochs=1000, batch_size=15, verbose=2)

    # Evaluar el modelo
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f"Accuracy: {accuracy * 100:.2f}%")

    data_test = data[:200]
    X, y = create_sequences(data_test, window_size, threshold)
    X = scaler.fit_transform(X)
    while True:
        probability = 0.6
        correct = 0
        incorrect = 0
        count = 0
        # Predecir el siguiente número
        for i in range(len(X)):
            data_ = X[i]
            next_value = y[i]
            new_sequence = np.array(data_)  # Ejemplo de secuencia
            new_sequence = scaler.transform([new_sequence])
            prediction = model.predict(new_sequence)
            if prediction[0][0] > probability:
                count += 1
                if next_value == 1:
                    correct += 1
                else:
                    incorrect += 1
                print(
                    f"Probabilidad de que el siguiente número "
                    f"sea mayor a {threshold}: {prediction[0][0] * 100:.2f}% "
                    f" ({next_value})"
                )

        count = count if count > 0 else 1
        print(f"corrects predictions: {correct} ({round(correct/count, 2)})")
        print(
            f"incorrect predictions: {incorrect} "
            f"({round(incorrect / count, 2)})"
        )
