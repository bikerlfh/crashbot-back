# Importar las librerías necesarias
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, LSTM

# Crear un arreglo de decimales de ejemplo
data = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])

# Definir la longitud de la secuencia de entrada
sequence_length = 3

# Crear un arreglo de entrenamiento y un arreglo de etiquetas para el modelo
x_train = []
y_train = []
for i in range(sequence_length, len(data)):
    x_train.append(data[i-sequence_length:i])
    y_train.append(data[i])

# Convertir los arreglos a matrices numpy
x_train = np.array(x_train)
y_train = np.array(y_train)

# Crear el modelo de inteligencia artificial
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(sequence_length, 1)))
model.add(LSTM(units=50))
model.add(Dense(units=1))
model.compile(optimizer='adam', loss='mean_squared_error')

# Entrenar el modelo
model.fit(x_train.reshape((x_train.shape[0], x_train.shape[1], 1)), y_train, epochs=100, batch_size=1)

# Predecir el siguiente valor en la secuencia
last_values = data[-sequence_length:]
next_value = model.predict(last_values.reshape((1, sequence_length, 1)))

# Imprimir la predicción
print("El siguiente valor en la secuencia es:", next_value[0][0])