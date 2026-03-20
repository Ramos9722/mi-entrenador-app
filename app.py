import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.title("🏋️‍♂️ Mi Diario de Progreso")

# Configuración básica
url = "TU_URL_DE_GOOGLE_SHEETS_AQUI"

# Intentar conectar de forma simple
try:
    # Esto leerá la hoja si es pública (Cualquier persona con el enlace -> Editor)
    gc = gspread.public_sheets() 
    sh = gc.open_by_url(url)
    worksheet = sh.get_worksheet(0)
    
    st.success("✅ Conectado a Google Sheets")
    
    # Mostrar datos
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    st.write("Tu historial:")
    st.dataframe(df)

except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.info("Asegúrate de que tu Google Sheet sea PÚBLICA (Cualquier persona con el enlace -> Editor)")

# Formulario simple
peso = st.number_input("Peso (kg)", value=70.0)
if st.button("Guardar"):
    worksheet.append_row([str(pd.Timestamp.now()), peso])
    st.rerun()
