import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Coach Nutricional Peruano", page_icon="🇵🇪")
st.title("🇵🇪 Mi Diario Nutricional Completo")

# --- DICCIONARIO NUTRICIONAL PERUANO ---
alimentos_peru = {
    "huevo": {"cal": 78, "prot": 6.3, "medida": "unidad"},
    "pollo": {"cal": 165, "prot": 31, "medida": "presa mediana"},
    "arroz": {"cal": 240, "prot": 4.4, "medida": "taza cocida"},
    "menestra": {"cal": 230, "prot": 15, "medida": "porcion"},
    "pan frances": {"cal": 85, "prot": 2.5, "medida": "unidad"},
    "camote": {"cal": 115, "prot": 1.3, "medida": "unidad mediana"},
    "jugo de papaya": {"cal": 120, "prot": 1, "medida": "vaso grande"},
    "papa": {"cal": 90, "prot": 2, "medida": "unidad mediana"},
    "leche": {"cal": 150, "prot": 8, "medida": "taza/vaso"}
}

# 1. Inicializar la "Bolsa de Comida" del día si no existe
if 'carrito_comida' not in st.session_state:
    st.session_state.carrito_comida = []

# 2. Conexión
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read()

# 3. BARRA LATERAL: Armar el plato
with st.sidebar:
    st.header("🍎 Armar Menú de Hoy")
    tipo_comida = st.selectbox("Momento:", ["Desayuno", "Almuerzo", "Cena", "Otros"])
    alimento_sel = st.selectbox("Alimento:", options=list(alimentos_peru.keys()))
    cant = st.number_input(f"Cantidad ({alimentos_peru[alimento_sel]['medida']})", min_value=0.5, value=1.0, step=0.5)
    
    if st.button("➕ Añadir al plato"):
        info = alimentos_peru[alimento_sel]
        item = {
            "momento": tipo_comida,
            "nombre": alimento_sel,
            "cal": info["cal"] * cant,
            "prot": info["prot"] * cant
        }
        st.session_state.carrito_comida.append(item)
        st.toast(f"Añadido {alimento_sel} al {tipo_comida}")

# 4. CUERPO PRINCIPAL: Resumen y Guardado
st.subheader("🍽️ Tu plato de hoy")
if st.session_state.carrito_comida:
    resumen_df = pd.DataFrame(st.session_state.carrito_comida)
    st.table(resumen_df) # Muestra lo que vas acumulando
    
    total_cal = resumen_df['cal'].sum()
    total_prot = resumen_df['prot'].sum()
    detalle_texto = ", ".join([f"{i['momento']}: {i['nombre']}" for i in st.session_state.carrito_comida])
    
    st.metric("Total Calorías", f"{total_cal} kcal")
    st.metric("Total Proteína", f"{total_prot} g")

    col1, col2 = st.columns(2)
    with col1:
        peso_hoy = st.number_input("Tu peso hoy (kg)", value=70.0, step=0.1)
        fecha_hoy = st.date_input("Fecha de registro")
    
    if st.button("💾 GUARDAR TODO EN GOOGLE SHEETS"):
        nueva_fila = pd.DataFrame({
            "Fecha": [str(fecha_hoy)],
            "Peso": [peso_hoy],
            "Calorias": [total_cal],
            "Proteinas": [total_prot],
            "Detalle": [detalle_texto]
        })
        df_final = pd.concat([df, nueva_fila], ignore_index=True)
        conn.update(data=df_final)
        st.session_state.carrito_comida = [] # Limpiar para mañana
        st.success("✅ ¡Día guardado con éxito!")
        st.rerun()
    
    if st.button("🗑️ Vaciar plato"):
        st.session_state.carrito_comida = []
        st.rerun()
else:
    st.info("Tu plato está vacío. Usa la barra lateral para añadir lo que comiste.")

# 5. Gráficas (igual que antes)
if not df.empty:
    st.divider()
    st.subheader("📊 Tu Historial Real")
    df_graf = df.copy()
    df_graf['Fecha'] = pd.to_datetime(df_graf['Fecha'])
    st.line_chart(data=df_graf.sort_values('Fecha'), x="Fecha", y="Peso")
