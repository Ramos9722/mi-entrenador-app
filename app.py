import streamlit as st
import pandas as pd

st.title("🏋️‍♂️ Mi Diario de Progreso")

# 1. TU URL (Asegúrate de que sea la de tu navegador)
url_original = "TU_URL_DE_GOOGLE_SHEETS_AQUI"

# 2. TRUCO DE PROGRAMADOR: Convertimos la URL para descarga directa
# Esto reemplaza el final de la URL para que Google nos entregue los datos directo
if "/edit" in url_original:
    url_csv = url_original.split("/edit")[0] + "/gviz/tq?tqx=out:csv"
else:
    url_csv = url_original

try:
    # 3. LEER LOS DATOS (Esto no pide permisos si está 'Cualquier persona con el enlace')
    df = pd.read_csv(url_csv)
    
    st.success("✅ ¡Conectado y datos leídos!")
    
    if not df.empty:
        st.write("Tu historial:")
        st.dataframe(df)
    else:
        st.info("La hoja está vacía.")

except Exception as e:
    st.error(f"No pudimos leer los datos: {e}")
    st.info("Revisa que el enlace sea correcto y público.")

# 4. Formulario de registro (Visual)
peso = st.number_input("Peso de hoy (kg)", value=70.0)
if st.button("Guardar"):
    st.warning("Para guardar datos automáticamente con este método simple, necesitamos un paso extra. ¡Primero confirmemos que puedes VER tus datos!")
