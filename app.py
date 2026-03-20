import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Coach Nutricional Peruano", page_icon="🇵🇪")
st.title("🇵🇪 Mi Diario Fitness Peruano")

# --- DICCIONARIO NUTRICIONAL PERUANO (Basado en Tablas de Composición) ---
# Valores aproximados por UNIDAD o PORCIÓN ESTÁNDAR
alimentos_peru = {
    "huevo": {"cal": 78, "prot": 6.3, "medida": "unidad"},
    "pollo": {"cal": 165, "prot": 31, "medida": "presa mediana"},
    "arroz": {"cal": 240, "prot": 4.4, "medida": "taza cocida"},
    "menestra": {"cal": 230, "prot": 15, "medida": "plato hondo/porción"},
    "pan frances": {"cal": 85, "prot": 2.5, "medida": "unidad"},
    "camote": {"cal": 115, "prot": 1.3, "medida": "unidad mediana"},
    "papa": {"cal": 90, "prot": 2, "medida": "unidad mediana"},
    "manzana": {"cal": 52, "prot": 0.3, "medida": "unidad"},
    "platano": {"cal": 90, "prot": 1, "medida": "unidad"},
    "leche": {"cal": 150, "prot": 8, "medida": "taza/vaso"},
    "atun": {"cal": 120, "prot": 25, "medida": "lata entera"}
}

# 1. Conexión
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read()

# 2. Formulario mejorado
with st.sidebar:
    st.header("🍴 Registro de Hoy")
    with st.form(key="registro"):
        peso = st.number_input("Peso hoy (kg)", value=70.0, step=0.1)
        fecha = st.date_input("Fecha")
        
        st.divider()
        # Selector para evitar errores de escritura
        comida = st.selectbox("¿Qué comiste?", options=list(alimentos_peru.keys()))
        cantidad = st.number_input(f"Cantidad ({alimentos_peru[comida]['medida']})", min_value=0.5, value=1.0, step=0.5)
        
        submit = st.form_submit_button("Guardar Registro")

if submit:
    # Cálculo basado en unidades/porciones
    info = alimentos_peru[comida]
    cal_totales = info["cal"] * cantidad
    prot_totales = info["prot"] * cantidad
    
    st.info(f"Has consumido: {cal_totales} kcal y {prot_totales}g de proteína en esa porción.")

    # Crear nueva fila para Google Sheets
    nueva_fila = pd.DataFrame({
        "Fecha": [str(fecha)], 
        "Peso": [peso],
        "Calorias": [round(cal_totales, 1)],
        "Proteinas": [round(prot_totales, 1)]
    })
    
    df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
    conn.update(data=df_actualizado)
    st.success("💪 ¡Datos guardados!")
    st.rerun()

# 3. Visualización
if not df.empty:
    tab1, tab2 = st.tabs(["📈 Gráficas", "📋 Historial"])
    
    with tab1:
        df_grafica = df.copy()
        df_grafica['Fecha'] = pd.to_datetime(df_grafica['Fecha'])
        df_grafica = df_grafica.sort_values('Fecha')
        
        st.subheader("Evolución de Peso")
        st.line_chart(data=df_grafica, x="Fecha", y="Peso")
        
        st.subheader("Proteína consumida por día")
        st.bar_chart(data=df_grafica, x="Fecha", y="Proteinas")

    with tab2:
        st.dataframe(df)
