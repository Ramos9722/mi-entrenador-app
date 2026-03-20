import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Family Fitness Hub 🇵🇪", page_icon="👨‍👩‍👧‍👦", layout="wide")

# --- 1. CONFIGURACIÓN DE LA FAMILIA ---
# Agrega aquí los nombres de todos tus familiares
familia = ["Seleccionar...", "Anderson", "Emerson", "Jhon", "Nelida", "Sharon"]

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

# --- 2. LÓGICA DE SESIÓN ---
if 'carrito_comida' not in st.session_state:
    st.session_state.carrito_comida = []

conn = st.connection("gsheets", type=GSheetsConnection)
df_total = conn.read()

# --- 3. INTERFAZ DE BIENVENIDA (PERFILES) ---
st.title("👨‍👩‍👧‍👦 Family Fitness Hub")
usuario_activo = st.selectbox("👤 ¿Quién va a registrar su progreso?", familia)

if usuario_activo != "Seleccionar...":
    st.divider()
    st.header(f"Bienvenido, {usuario_activo} 👋")

    # FILTRAR DATOS SOLO PARA ESTE USUARIO
    if not df_total.empty and 'Usuario' in df_total.columns:
        df_usuario = df_total[df_total['Usuario'] == usuario_activo]
    else:
        df_usuario = pd.DataFrame()

    # --- 4. REGISTRO (BARRA LATERAL) ---
    with st.sidebar:
        st.header(f"🍎 Menú de {usuario_activo}")
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
            st.toast("¡Añadido!")

    # --- 5. RESUMEN Y GUARDADO ---
    col_izq, col_der = st.columns([1, 1])

    with col_izq:
        st.subheader("🍽️ Plato del día")
        if st.session_state.carrito_comida:
            resumen_df = pd.DataFrame(st.session_state.carrito_comida)
            st.table(resumen_df)
            
            total_cal = resumen_df['cal'].sum()
            total_prot = resumen_df['prot'].sum()
            detalle_texto = ", ".join([f"{i['momento']}: {i['nombre']}" for i in st.session_state.carrito_comida])
            
            st.metric("Total Calorías", f"{total_cal} kcal")
            st.metric("Total Proteína", f"{total_prot} g")

            peso_hoy = st.number_input("Peso (kg)", value=70.0, step=0.1)
            fecha_hoy = st.date_input("Fecha")

            if st.button("💾 GUARDAR REGISTRO"):
                nueva_fila = pd.DataFrame({
                    "Usuario": [usuario_activo], # AQUÍ SE ASIGNA EL NOMBRE
                    "Fecha": [str(fecha_hoy)],
                    "Peso": [peso_hoy],
                    "Calorias": [total_cal],
                    "Proteinas": [total_prot],
                    "Detalle": [detalle_texto]
                })
                df_final = pd.concat([df_total, nueva_fila], ignore_index=True)
                conn.update(data=df_final)
                st.session_state.carrito_comida = []
                st.success(f"✅ ¡Progreso de {usuario_activo} guardado!")
                st.rerun()
        else:
            st.info("Añade alimentos en la izquierda.")

    # --- 6. GRÁFICAS PERSONALES ---
    with col_der:
        st.subheader(f"📈 Progreso de {usuario_activo}")
        if not df_usuario.empty:
            df_graf = df_usuario.copy()
            df_graf['Fecha'] = pd.to_datetime(df_graf['Fecha'])
            st.line_chart(data=df_graf.sort_values('Fecha'), x="Fecha", y="Peso")
            st.bar_chart(data=df_graf, x="Fecha", y="Proteinas")
        else:
            st.write("Aún no tienes registros personales.")

else:
    st.info("Por favor, selecciona un perfil para comenzar.")
