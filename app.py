import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

st.set_page_config(page_title="Coach AI Pro", page_icon="⚖️")
st.title("⚖️ Mi Registro de Progreso")

# 1. Conexión con Google Sheets
url = "https://docs.google.com/spreadsheets/d/1lCJoaHAaE_lmXbQUGp5ZKNp0HDzd3IJxKWQk19BgWhc/edit?gid=0#gid=0" # <--- PEGA TU URL AQUÍ
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Entradas de datos
with st.sidebar:
    st.header("Registro Diario")
    fecha_hoy = date.today()
    peso_hoy = st.number_input("Peso de hoy (kg)", value=70.0)
    calorias_hoy = st.number_input("Calorías consumidas", value=2000)
    
    boton_guardar = st.button("Guardar mi progreso")

# 3. Lógica para guardar datos
if boton_guardar:
    # Leemos los datos actuales
    data_actual = conn.read(spreadsheet=url)
    
    # Creamos la nueva fila
    nueva_fila = pd.DataFrame([{
        "Fecha": str(fecha_hoy),
        "Peso": peso_hoy,
        "Calorias": calorias_hoy
    }])
    
    # Unimos y guardamos
    data_actualizada = pd.concat([data_actual, nueva_fila], ignore_index=True)
    conn.update(spreadsheet=url, data=data_actualizada)
    st.success("¡Datos guardados en Google Sheets!")

# 4. Mostrar el historial
st.subheader("Tu historial guardado")
datos_vistos = conn.read(spreadsheet=url)
st.dataframe(datos_vistos)
