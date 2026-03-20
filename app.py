import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Family Fitness Hub 🇵🇪", page_icon="👨‍👩‍👧‍👦", layout="wide")

# --- 1. BASE DE DATOS DE LA FAMILIA ---
perfiles = {
    "Anderson": {"estatura": 1.57, "edad": 22, "sexo": "M"},
    "Emerson": {"estatura": 1.57, "edad": 22, "sexo": "M"},
    "Jhon": {"estatura": 1.70, "edad": 41, "sexo": "M"},
    "Nelida": {"estatura": 1.54, "edad": 51, "sexo": "F"},
    "Sharon": {"estatura": 1.50, "edad": 11, "sexo": "F"}
}

# --- 2. DICCIONARIO DE ALIMENTOS PERUANOS (Por Unidades/Porciones) ---
alimentos_peru = {
    "huevo": {"cal": 78, "prot": 6.3, "medida": "unidad"},
    "pollo": {"cal": 165, "prot": 31, "medida": "presa mediana"},
    "arroz": {"cal": 240, "prot": 4.4, "medida": "taza cocida"},
    "menestra": {"cal": 230, "prot": 15, "medida": "porcion"},
    "pan frances": {"cal": 85, "prot": 2.5, "medida": "unidad"},
    "camote": {"cal": 115, "prot": 1.3, "medida": "unidad"},
    "jugo de papaya": {"cal": 120, "prot": 1, "medida": "vaso"},
    "papa": {"cal": 90, "prot": 2, "medida": "unidad"},
    "leche": {"cal": 150, "prot": 8, "medida": "taza"},
    "avena": {"cal": 150, "prot": 5, "medida": "taza"}
}

# --- 3. FUNCIONES DE CÁLCULO ---
def calcular_fitness(peso, estatura):
    imc = peso / (estatura ** 2)
    if imc < 18.5: estado = "Bajo peso 🦴"
    elif 18.5 <= imc < 25: estado = "Peso Normal ✅"
    elif 25 <= imc < 30: estado = "Sobrepeso ⚠️"
    else: estado = "Obesidad 🚨"
    
    vasos_meta = round((peso * 35) / 250) # 35ml por kg dividido en vasos de 250ml
    return round(imc, 1), estado, vasos_meta

# --- 4. CONEXIÓN Y SESIÓN ---
if 'carrito_comida' not in st.session_state:
    st.session_state.carrito_comida = []

conn = st.connection("gsheets", type=GSheetsConnection)
df_total = conn.read()

# --- 5. INTERFAZ PRINCIPAL ---
st.title("🏋️‍♂️ Coach Familiar Inteligente 🇵🇪")
usuario_activo = st.selectbox("👤 Selecciona tu perfil:", ["Seleccionar..."] + list(perfiles.keys()))

if usuario_activo != "Seleccionar...":
    datos_p = perfiles[usuario_activo]
    
    # Filtrar datos del usuario
    if not df_total.empty and 'Usuario' in df_total.columns:
        df_usuario = df_total[df_total['Usuario'] == usuario_activo]
        ultimo_peso = df_usuario['Peso'].iloc[-1] if not df_usuario.empty else 60.0
    else:
        df_usuario = pd.DataFrame()
        ultimo_peso = 60.0

    # Cálculos Automáticos
    imc, estado_fisico, meta_agua = calcular_fitness(ultimo_peso, datos_p["estatura"])

    # Métricas de Salud
    st.header(f"Panel de {usuario_activo}")
    m1, m2, m3 = st.columns(3)
    m1.metric("IMC Actual", f"{imc}", help=estado_fisico)
    m2.metric("Estado", estado_fisico)
    m3.metric("Meta de Agua", f"{meta_agua} vasos", help="Calculado según tu peso actual")

    st.divider()

    # --- REGISTRO DE COMIDA Y AGUA ---
    col_input, col_resumen = st.columns([1, 1.2])

    with col_input:
        st.subheader("📝 Registro de Hoy")
        
        # Selección de Comida
        with st.expander("➕ Añadir Alimentos"):
            momento = st.selectbox("Momento:", ["Desayuno", "Almuerzo", "Cena", "Snack"])
            comida_sel = st.selectbox("¿Qué comiste?", options=list(alimentos_peru.keys()))
            cant = st.number_input(f"Cantidad ({alimentos_peru[comida_sel]['medida']})", min_value=0.5, value=1.0, step=0.5)
            
            if st.button("Añadir al Plato"):
                info = alimentos_peru[comida_sel]
                st.session_state.carrito_comida.append({
                    "momento": momento,
                    "nombre": comida_sel,
                    "cal": info["cal"] * cant,
                    "prot": info["prot"] * cant
                })
                st.toast(f"{comida_sel} añadido!")

        # Registro de Agua y Peso
        vasos_reales = st.number_input("💧 Vasos de agua hoy:", min_value=0, value=0)
        nuevo_peso = st.number_input("⚖️ Peso actual (kg):", value=float(ultimo_peso), step=0.1)
        fecha_registro = st.date_input("📅 Fecha:")

    with col_resumen:
        st.subheader("🍽️ Resumen del Día")
        if st.session_state.carrito_comida:
            temp_df = pd.DataFrame(st.session_state.carrito_comida)
            st.table(temp_df[['momento', 'nombre', 'cal', 'prot']])
            
            total_cal = temp_df['cal'].sum()
            total_prot = temp_df['prot'].sum()
            detalle_txt = ", ".join([f"{i['momento']}: {i['nombre']}" for i in st.session_state.carrito_comida])
            
            st.write(f"**Total Calorías:** {round(total_cal,1)} kcal | **Total Proteína:** {round(total_prot,1)}g")
            
            if st.button("💾 GUARDAR TODO EN EXCEL"):
                nueva_fila = pd.DataFrame({
                    "Usuario": [usuario_activo],
                    "Fecha": [str(fecha_registro)],
                    "Peso": [nuevo_peso],
                    "Calorias": [total_cal],
                    "Proteinas": [total_prot],
                    "Detalle": [detalle_txt],
                    "Vasos_Agua": [vasos_reales]
                })
                df_final = pd.concat([df_total, nueva_fila], ignore_index=True)
                conn.update(data=df_final)
                st.session_state.carrito_comida = []
                st.success("¡Datos guardados con éxito!")
                st.rerun()
        else:
            st.info("Añade alimentos en el panel de la izquierda para comenzar.")

    # --- GRÁFICAS ---
    if not df_usuario.empty:
        st.divider()
        st.subheader(f"📈 Tu Evolución - {usuario_activo}")
        tab_peso, tab_nutri = st.tabs(["Control de Peso", "Nutrición y Agua"])
        
        with tab_peso:
            df_u_graf = df_usuario.copy()
            df_u_graf['Fecha'] = pd.to_datetime(df_u_graf['Fecha'])
            st.line_chart(data=df_u_graf.sort_values('Fecha'), x="Fecha", y="Peso")
            
        with tab_nutri:
            st.bar_chart(data=df_u_graf, x="Fecha", y=["Proteinas", "Vasos_Agua"])
else:
    st.info("👋 ¡Hola! Por favor selecciona un miembro de la familia para empezar su entrenamiento.")
    st.write("Aún no tienes registros personales.")

else:
    st.info("Por favor, selecciona un perfil para comenzar.")
