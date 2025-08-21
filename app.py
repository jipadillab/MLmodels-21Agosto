import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import random

# La línea st.set_option('deprecation.showPyplotGlobalUse', False) ha sido eliminada
# ya que la opción 'deprecation.showPyplotGlobalUse' ya no es reconocida por Streamlit,
# lo que causaba el KeyError. Esta advertencia no es necesaria en versiones recientes.

def generate_sport_data(num_samples, num_cols):
    """
    Genera un conjunto de datos deportivos sintético basado en el número de muestras y columnas.
    Incluye una mezcla de variables cuantitativas y cualitativas.
    """
    data = {}
    
    # Define las columnas potenciales y cómo generar sus datos
    possible_cols_generators = {
        'Puntos': lambda n: np.random.randint(5, 30, n), # Cuantitativa: Puntos anotados por jugador
        'Asistencias': lambda n: np.random.randint(0, 15, n), # Cuantitativa: Asistencias
        'Rebotes': lambda n: np.random.randint(0, 20, n), # Cuantitativa: Rebotes
        'MinutosJugados': lambda n: np.random.randint(20, 48, n), # Cuantitativa: Minutos jugados
        'Velocidad_KmH': lambda n: np.random.uniform(15.0, 35.0, n).round(1), # Cuantitativa: Velocidad media
        'Altura_cm': lambda n: np.random.randint(170, 205, n), # Cuantitativa: Altura
        'Equipo': lambda n: np.random.choice(['Leones', 'Águilas', 'Lobos', 'Tigres', 'Panteras', 'Condores'], n), # Cualitativa: Nombre del equipo
        'Posicion': lambda n: np.random.choice(['Delantero', 'Defensa', 'Mediocampista', 'Portero', 'Pivot', 'Escolta'], n), # Cualitativa: Posición en el juego
        'Genero': lambda n: np.random.choice(['Masculino', 'Femenino'], n), # Cualitativa: Género
        'EsCapitan': lambda n: np.random.choice([True, False], n), # Cualitativa (Binaria): Si es capitán
        'Rendimiento_Score': lambda n: (np.random.randint(5, 30, n) * 0.4 + np.random.randint(0, 15, n) * 0.3 + np.random.randint(0, 20, n) * 0.3 + np.random.uniform(0, 10, n)).round(0) # Cuantitativa mixta/derivada
    }
    
    # Selecciona las columnas a incluir, intentando mantener una mezcla
    all_possible_col_names = list(possible_cols_generators.keys())
    
    # Garantiza que el número de columnas no exceda las disponibles
    num_cols_to_use = min(num_cols, len(all_possible_col_names))
    
    # Selecciona columnas de forma aleatoria para obtener la cantidad deseada
    selected_col_names = random.sample(all_possible_col_names, num_cols_to_use)

    # Genera los datos para las columnas seleccionadas
    for col_name in selected_col_names:
        data[col_name] = possible_cols_generators[col_name](num_samples)
            
    df = pd.DataFrame(data)
    return df

# --- Configuración de la Interfaz de Usuario de Streamlit ---

st.title("📊 EDA Interactivo de Datos Deportivos")
st.markdown("Una herramienta para explorar conjuntos de datos simulados de deportes con visualizaciones dinámicas.")
st.markdown("---")

# Barra lateral para los controles de generación de datos
st.sidebar.header("Generar Datos Simulados")
num_samples = st.sidebar.slider(
    "Número de Muestras (Jugadores)", 
    min_value=50, 
    max_value=500, 
    value=200, 
    step=50
)
num_cols = st.sidebar.slider(
    "Número de Columnas", 
    min_value=2, 
    max_value=6, 
    value=4, 
    step=1
)

# Botón para generar un nuevo conjunto de datos
if st.sidebar.button("Generar Nuevo Conjunto de Datos"):
    st.session_state.df = generate_sport_data(num_samples, num_cols)
    st.success("¡Conjunto de datos generado!")

# Inicializa el DataFrame si no existe en el estado de la sesión
if 'df' not in st.session_state:
    st.session_state.df = generate_sport_data(num_samples, num_cols)

# --- Sección de Visualización de Datos ---

st.header("Visualización de Datos")

st.subheader("Tabla de Datos Generados")
# Muestra el DataFrame en la aplicación
st.dataframe(st.session_state.df)

st.markdown("---")
st.subheader("Análisis Exploratorio y Gráficos")

# Permite al usuario seleccionar columnas para graficar
available_columns = st.session_state.df.columns.tolist()
if not available_columns:
    st.warning("No hay columnas disponibles para graficar. Por favor, genera un conjunto de datos.")
else:
    selected_columns = st.multiselect(
        "Selecciona Columna(s) para Graficar", 
        available_columns, 
        default=available_columns[0] if available_columns else []
    )

    # Permite al usuario seleccionar el tipo de gráfico
    chart_type = st.selectbox(
        "Selecciona el Tipo de Gráfico",
        ["Histograma", "Gráfico de Barras", "Gráfico de Dispersión", "Gráfico de Pastel", "Gráfico de Tendencia (Línea)"]
    )

    # --- Lógica para Generar Gráficos ---
    if selected_columns:
        # Histograma: Para una sola columna numérica
        if chart_type == "Histograma":
            if len(selected_columns) == 1:
                col = selected_columns[0]
                if pd.api.types.is_numeric_dtype(st.session_state.df[col]):
                    st.subheader(f"Histograma de **{col}**")
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.histplot(st.session_state.df[col], kde=True, ax=ax, palette='viridis')
                    ax.set_title(f'Distribución de {col}')
                    ax.set_xlabel(col)
                    ax.set_ylabel('Frecuencia')
                    st.pyplot(fig)
                else:
                    st.warning("Para un Histograma, selecciona una **columna numérica**.")
            else:
                st.warning("Selecciona **solo una columna** para el Histograma.")

        # Gráfico de Barras: Para conteo de una categórica o media de numérica por categórica
        elif chart_type == "Gráfico de Barras":
            st.subheader(f"Gráfico de Barras")
            fig, ax = plt.subplots(figsize=(12, 7))

            if len(selected_columns) == 1:
                col_x = selected_columns[0]
                if pd.api.types.is_categorical_dtype(st.session_state.df[col_x]) or pd.api.types.is_object_dtype(st.session_state.df[col_x]) or st.session_state.df[col_x].nunique() < 20:
                    sns.countplot(x=st.session_state.df[col_x], ax=ax, palette='viridis')
                    ax.set_title(f'Conteo de **{col_x}**')
                    ax.set_xlabel(col_x)
                    ax.set_ylabel('Conteo')
                    plt.xticks(rotation=45, ha='right')
                    st.pyplot(fig)
                else:
                    st.warning("Para un Gráfico de Barras de conteo, selecciona una **columna categórica** o una numérica con pocas categorías.")
            elif len(selected_columns) >= 2:
                col_numeric = None
                col_categorical = None

                # Busca una columna numérica y una categórica entre las seleccionadas
                for col in selected_columns:
                    if pd.api.types.is_numeric_dtype(st.session_state.df[col]) and col_numeric is None:
                        col_numeric = col
                    elif (pd.api.types.is_categorical_dtype(st.session_state.df[col]) or pd.api.types.is_object_dtype(st.session_state.df[col])) and col_categorical is None:
                        col_categorical = col
                
                if col_numeric and col_categorical:
                    sns.barplot(x=st.session_state.df[col_categorical], y=st.session_state.df[col_numeric], ax=ax, palette='viridis')
                    ax.set_title(f'Media de **{col_numeric}** por **{col_categorical}**')
                    ax.set_xlabel(col_categorical)
                    ax.set_ylabel(f'Media de {col_numeric}')
                    plt.xticks(rotation=45, ha='right')
                    st.pyplot(fig)
                else:
                    st.warning("Para un Gráfico de Barras por agrupación, selecciona al menos una **columna numérica** y una **categórica**.")
            else:
                st.warning("Selecciona al menos una columna categórica o una numérica y una categórica para el Gráfico de Barras.")

        # Gráfico de Dispersión: Para dos columnas numéricas
        elif chart_type == "Gráfico de Dispersión":
            if len(selected_columns) >= 2:
                col_x = selected_columns[0]
                col_y = selected_columns[1]
                if pd.api.types.is_numeric_dtype(st.session_state.df[col_x]) and pd.api.types.is_numeric_dtype(st.session_state.df[col_y]):
                    st.subheader(f"Gráfico de Dispersión entre **{col_x}** y **{col_y}**")
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.scatterplot(x=st.session_state.df[col_x], y=st.session_state.df[col_y], ax=ax, palette='viridis')
                    ax.set_title(f'Relación entre {col_x} y {col_y}')
                    ax.set_xlabel(col_x)
                    ax.set_ylabel(col_y)
                    st.pyplot(fig)
                else:
                    st.warning("Para un Gráfico de Dispersión, selecciona dos **columnas numéricas**.")
            else:
                st.warning("Selecciona al menos **dos columnas** para el Gráfico de Dispersión.")

        # Gráfico de Pastel: Para una sola columna cualitativa/categórica
        elif chart_type == "Gráfico de Pastel":
            if len(selected_columns) == 1:
                col = selected_columns[0]
                if not pd.api.types.is_numeric_dtype(st.session_state.df[col]) and st.session_state.df[col].nunique() < 20: # Apto para categóricas
                    st.subheader(f"Gráfico de Pastel de **{col}**")
                    fig, ax = plt.subplots(figsize=(8, 8))
                    counts = st.session_state.df[col].value_counts()
                    ax.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'black'})
                    ax.axis('equal') # Asegura que el pastel sea un círculo
                    ax.set_title(f'Distribución de {col}')
                    st.pyplot(fig)
                else:
                    st.warning("Para un Gráfico de Pastel, selecciona una **columna cualitativa/categórica** con no demasiadas categorías.")
            else:
                st.warning("Selecciona **solo una columna cualitativa** para el Gráfico de Pastel.")

        # Gráfico de Tendencia (Línea): Para una sola columna numérica
        elif chart_type == "Gráfico de Tendencia (Línea)":
            if len(selected_columns) == 1:
                col = selected_columns[0]
                if pd.api.types.is_numeric_dtype(st.session_state.df[col]):
                    st.subheader(f"Gráfico de Tendencia de **{col}**")
                    fig, ax = plt.subplots(figsize=(12, 6))
                    # Usando el índice como "tiempo" para una simple línea de tendencia
                    sns.lineplot(x=st.session_state.df.index, y=st.session_state.df[col], ax=ax, palette='viridis')
                    ax.set_title(f'Tendencia de {col} a lo largo de las Muestras')
                    ax.set_xlabel('Índice de Muestra')
                    ax.set_ylabel(col)
                    st.pyplot(fig)
                else:
                    st.warning("Para un Gráfico de Tendencia (Línea), selecciona una **columna numérica**.")
            else:
                st.warning("Selecciona **solo una columna** para el Gráfico de Tendencia (Línea).")
    else:
        st.info("Por favor, selecciona al menos una columna para generar gráficos.")

st.markdown("---")
st.sidebar.markdown("Desarrollado con ❤️ en Python y Streamlit")
