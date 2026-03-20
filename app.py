import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Mi Coach Nutricional", page_icon="🍎")
st.title("🍎 Registro de Peso y Nutrición")

# --- BASE DE DATOS NUTRICIONAL (Puedes ampliarla luego) ---
# Valores por cada 100g o por pieza
alimentos_db = {
    "huevo": {"cal": 155, "prot": 13},
    "pechuga de pollo": {"cal": 165, "prot": 31},
    "avena": {"cal": 389, "prot": 17},
    "platano": {"cal": 89, "prot": 1.1},
    "arroz": {"cal": 130, "prot": 2.7},
    "leche": {"cal": 42, "prot": 3.4},
    "atun": {"cal": 130, "prot": 29}
}

# 1. Conexión
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read()

# 2. Formulario en la barra lateral
with st.sidebar:
    st.header("📝 Registro Diario")
    with st.form(key="registro"):
        peso = st.number_input("Tu peso hoy (kg)", value=70.0, step=0.1)
        fecha = st.date_input("Fecha")
        
        st.divider()
        st.subheader("¿Qué comiste hoy?")
        comida = st.text_input("Ej: huevo, pechuga de pollo, platano").lower()
        gramos = st.number_input("Gramos o cantidad (aprox)", value=100)
        
        submit = st.form_submit_button("Guardar todo")

if submit:
    # Lógica de cálculo nutricional
    cal_totales = 0
    prot_totales = 0
    
    if comida in alimentos_db:
        factor = gramos / 100
        cal_totales = alimentos_db[comida]["cal"] * factor
        prot_totales = alimentos_db[comida]["prot"] * factor
        st.info(f"Calculado: {cal_totales} kcal y {prot_totales}g de proteína.")
    else:
        st.warning("Alimento no encontrado en la base de datos, se guardará con 0. (Puedes añadirlo al código luego)")

    # Crear nueva fila
    nueva_fila = pd.DataFrame({
        "Fecha": [str(fecha)], 
        "Peso": [peso],
        "Calorias": [round(cal_totales, 1)],
        "Proteinas": [round(prot_totales, 1)]
    })
    
    df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
    conn.update(data=df_actualizado)
    st.success("💪 ¡Datos guardados correctamente!")
    st.rerun()

# 3. Mostrar Gráficas y Datos
if not df.empty:
    col1, col2 = st.columns(2)
    
    df_grafica = df.copy()
    df_grafica['Fecha'] = pd.to_datetime(df_grafica['Fecha'])
    df_grafica = df_grafica.sort_values('Fecha')

    with col1:
        st.subheader("Evolución Peso")
        st.line_chart(data=df_grafica, x="Fecha", y="Peso")
    
    with col2:
        st.subheader("Consumo Proteína")
        st.bar_chart(data=df_grafica, x="Fecha", y="Proteinas")

    st.write("Tu historial completo:")
    st.dataframe(df)
