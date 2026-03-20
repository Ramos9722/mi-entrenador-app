import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Mi Coach de Peso", page_icon="🏋️‍♂️")
st.title("🏋️‍♂️ Mi Diario de Progreso")

# 1. Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Leer datos (usamos un truco para que no falle si la hoja está rara)
df = conn.read()

# 3. Formulario en la barra lateral
with st.sidebar:
    st.header("Registrar peso")
    with st.form(key="registro"):
        peso = st.number_input("Peso (kg)", value=70.0, step=0.1)
        fecha = st.date_input("Fecha")
        submit = st.form_submit_button("Guardar progreso")

if submit:
    # Creamos la nueva fila con nombres de columna exactos
    nueva_fila = pd.DataFrame({"Fecha": [str(fecha)], "Peso": [peso]})
    
    # Combinamos con lo anterior, asegurando que no haya errores de formato
    df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
    
    # Actualizamos la hoja completa
    conn.update(data=df_actualizado)
    st.success("💪 ¡Dato guardado!")
    st.rerun()

# 4. Gráfica y Tabla
if not df.empty:
    st.subheader("Tu evolución")
    # Limpieza de datos para la gráfica
    df_grafica = df.copy()
    df_grafica['Fecha'] = pd.to_datetime(df_grafica['Fecha'])
    df_grafica = df_grafica.sort_values('Fecha')
    
    # Dibujar la gráfica
    st.line_chart(data=df_grafica, x="Fecha", y="Peso")
    
    st.write("Historial:")
    st.dataframe(df)
