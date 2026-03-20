import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Mi Progreso AI", page_icon="📈")

st.title("📈 Mi Diario de Peso")

# 1. Conexión con los Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Leer datos (automáticamente usa la URL de los Secrets)
df = conn.read()

# 3. Formulario para añadir datos
with st.sidebar:
    st.header("Registrar hoy")
    with st.form(key="nuevo_registro"):
        nuevo_peso = st.number_input("Peso (kg):", min_value=30.0, max_value=200.0, step=0.1)
        fecha_registro = st.date_input("Fecha:")
        boton_enviar = st.form_submit_button("Guardar progreso")

if boton_enviar:
    # Crear fila nueva
    nueva_fila = pd.DataFrame([{"Fecha": str(fecha_registro), "Peso": nuevo_peso}])
    # Combinar
    df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
    # Guardar en Google
    conn.update(data=df_actualizado)
    st.success("✅ ¡Datos guardados en la nube!")
    st.rerun()

# 4. Mostrar Gráfica y Tabla
if not df.empty:
    st.subheader("Tu evolución visual")
    # Convertimos la fecha a formato que la gráfica entienda
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    st.line_chart(data=df, x="Fecha", y="Peso")
    
    st.write("Historial de datos:")
    st.dataframe(df)
else:
    st.info("Aún no hay datos. Registra tu peso en la barra lateral.")
