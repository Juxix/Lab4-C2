import streamlit as st
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt

st.title('Estimación de Ventas Diarias')

# Leo la informacion
info = pd.read_csv('ventas.csv')
st.write("Datos de Ventas Diarias")
st.dataframe(info)

# Preparo la info
X = torch.tensor(info['dia'].values, dtype=torch.float32).view(-1, 1)
y = torch.tensor(info['ventas'].values, dtype=torch.float32).view(-1, 1)

# Normalizo la informacion los datos
X_min, X_max = X.min(), X.max()
y_min, y_max = y.min(), y.max()
X_norm = (X - X_min) / (X_max - X_min)
y_norm = (y - y_min) / (y_max - y_min)

# Sidebar
st.sidebar.header('Parámetros de la Red Neuronal')
learning_rate = st.sidebar.slider('Tasa de Aprendizaje', 0.0, 1.0, 0.1)
epochs = st.sidebar.slider('Cantidad de Épocas', 10, 10000, 100)
hidden_neurons = st.sidebar.slider('Neurona en la capa oculta', 1, 100, 5)

# Entrenar la red neuronal
if st.sidebar.button('Entrenar'):
    class RedNeuronal(nn.Module):
        def __init__(self, input_size, hidden_size, output_size):
            super(RedNeuronal, self).__init__()
            self.hidden = nn.Linear(input_size, hidden_size)
            self.output = nn.Linear(hidden_size, output_size)
            self.relu = nn.ReLU()

        def forward(self, x):
            x = self.relu(self.hidden(x))
            x = self.output(x)
            return x

    # Instanciar la red neuronal
    modelo = RedNeuronal(input_size=1, hidden_size=hidden_neurons, output_size=1)

    # Definir la función de pérdida y el optimizador
    criterio = nn.MSELoss()
    optimizador = torch.optim.SGD(modelo.parameters(), lr=learning_rate)

    # Historial de pérdida
    historial_pérdida = []

    # Barra de progreso
    progreso = st.sidebar.progress(0)

    # Entrenamiento
    for epoch in range(epochs):
        predicciones = modelo(X_norm)
        perdida = criterio(predicciones, y_norm)

        optimizador.zero_grad()
        perdida.backward()
        optimizador.step()

        # Almacenar la pérdida de cada época
        historial_pérdida.append(perdida.item())

        # Actualizar barra de progreso
        progreso.progress((epoch + 1) / epochs)

    st.sidebar.success('Entrenamiento completado exitosamente.')

    # Mostrar gráfico de la función de costo
    plt.figure(figsize=(10, 6))
    plt.plot(historial_pérdida, label='Pérdida')
    plt.title('Evolución de la Función de Costo')
    plt.xlabel('Épocas')
    plt.ylabel('Pérdida')
    plt.legend()
    st.pyplot(plt)

    # Graficar las predicciones
    with torch.no_grad():
        predicciones_norm = modelo(X_norm)
        predicciones_invertidas = y_min + predicciones_norm * (y_max - y_min)

    # Gráfico de predicción de ventas
    plt.figure(figsize=(10, 6))
    plt.scatter(info['dia'], info['ventas'], color='green', label='Datos')
    plt.plot(info['dia'], predicciones_invertidas.numpy(), color='violet', label='Predicciones')
    plt.title('Predicción de Ventas Diarias')
    plt.xlabel('Día')
    plt.ylabel('Ventas')
    plt.legend()
    st.pyplot(plt)
