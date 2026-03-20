import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.title("🏋️‍♂️ Mi Diario de Progreso")

# Configuración básica
url = "TU_URL_DE_GOOGLE_SHEETS_AQUI"

# Intentar conectar de forma simple
try:
    # 1. Conexión simplificada
    gc = gspread.service_account_from_dict({}) # Ignora los errores de permiso aquí
    # Usamos el cliente directo de gspread
    sh = gspread.open_by_url(url)
    worksheet = sh.get_worksheet(0)
    
    st.success("✅ ¡Conectado con éxito!")
    
    # 2. Leer datos
    data = worksheet.get_all_records()
    if data:
        df = pd.DataFrame(data)
        st.write("Tu historial:")
        st.table(df) # st.table se ve más limpio para pocos datos
    else:
        st.info("La hoja está vacía. ¡Registra tu primer peso!")

except Exception as e:
    # Este es el truco: si falla lo anterior, intentamos abrirlo de forma anónima
    try:
        gc = gspread.authorize(None)
        sh = gc.open_by_url(url)
        worksheet = sh.get_worksheet(0)
        st.success("✅ Conectado (Modo Anónimo)")
    except:
        st.error("Error: Asegúrate de que en Google Sheets pusiste 'Cualquier persona con el enlace' -> 'EDITOR'")
