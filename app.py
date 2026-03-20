import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Family Coach 🇵🇪", page_icon="🏋️‍♂️", layout="wide")

# 2. BASE DE DATOS DE LA FAMILIA
perfiles = {
    "Anderson": {"estatura": 1.57, "edad": 22, "sexo": "M"},
    "Emerson": {"estatura": 1.57, "edad": 22, "sexo": "M"},
    "Jhon": {"estatura": 1.70, "edad": 41, "sexo": "M"},
    "Nelida": {"estatura": 1.54, "edad": 51, "sexo": "F"},
    "Sharon": {"estatura": 1.50, "edad": 11, "sexo": "F"}
}

# 3. DICCIONARIO NUTRICIONAL
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

# 4. FUNCIONES
def calcular_fitness(peso, estatura):
    imc = peso / (estatura ** 2)
    if imc < 18.5: estado = "Bajo peso 🦴"
    elif 18.5 <= imc < 25: estado = "Peso Normal ✅"
    elif 25 <= imc < 30: estado = "Sobrepeso ⚠️"
    else: estado = "Obesidad 🚨"
    vasos_meta = round((peso * 35) / 250)
    return round(imc, 1), estado, vasos_meta

# 5. CONEXIÓN
if 'carrito_comida' not in st.session_state:
    st.session_state.carrito_comida = []

conn = st.connection("gsheets", type=GSheetsConnection)
df_total = conn.read()

# 6. INTERFAZ PRINCIPAL
st.title("🏋️‍♂️ Family Fitness Hub 🇵🇪")
usuario_activo = st.selectbox("👤 ¿Quién eres?", ["Seleccionar..."] + list(perfiles.keys()))

if usuario_activo != "Seleccionar...":
    datos_p = perfiles[usuario_activo]
    
    # Datos históricos
    if not df_total.empty and 'Usuario' in df_total.columns:
        df_usuario = df_total[df_total['Usuario'] == usuario_activo]
        ultimo_peso = df_usuario['Peso'].iloc[-1] if not df_usuario.empty else 60.0
    else:
        df_usuario = pd.DataFrame()
        ultimo_peso = 60.0

    imc, estado_fisico, meta_agua = calcular_fitness(ultimo_peso, datos_p["estatura"])

    # --- MENÚ DE OPCIONES ---
    st.divider()
    opcion = st.sidebar.radio("Ir a:", ["🍎 Nutrición y Peso", "💪 Rutina de Ejercicios"])

    if opcion == "🍎 Nutrición y Peso":
        st.header(f"Gestión Nutricional - {usuario_activo}")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("IMC", imc)
        col2.metric("Estado", estado_fisico)
        col3.metric("Meta Agua", f"{meta_agua} vasos")

        c_input, c_resumen = st.columns([1, 1.2])
        with c_input:
            st.subheader("📝 Registrar Comida")
            momento = st.selectbox("Momento:", ["Desayuno", "Almuerzo", "Cena", "Snack"])
            comida_sel = st.selectbox("Alimento:", options=list(alimentos_peru.keys()))
            cant = st.number_input(f"Cantidad ({alimentos_peru[comida_sel]['medida']})", min_value=0.5, step=0.5)
            if st.button("➕ Añadir"):
                info = alimentos_peru[comida_sel]
                st.session_state.carrito_comida.append({"mom": momento, "nom": comida_sel, "c": info["cal"] * cant, "p": info["prot"] * cant})
                st.rerun()

            st.subheader("💧 Agua y Peso")
            v_reales = st.number_input("Vasos de agua hoy:", min_value=0)
            n_peso = st.number_input("Peso hoy (kg):", value=float(ultimo_peso))
            f_reg = st.date_input("Fecha:")

        with c_resumen:
            st.subheader("🍽️ Resumen de hoy")
            if st.session_state.carrito_comida:
                temp_df = pd.DataFrame(st.session_state.carrito_comida)
                st.table(temp_df)
                if st.button("💾 GUARDAR TODO"):
                    nueva_fila = pd.DataFrame({
                        "Usuario": [usuario_activo], "Fecha": [str(f_reg)], "Peso": [n_peso],
                        "Calorias": [temp_df['c'].sum()], "Proteinas": [temp_df['p'].sum()],
                        "Detalle": [", ".join(temp_df['nom'])], "Vasos_Agua": [v_reales]
                    })
                    df_final = pd.concat([df_total, nueva_fila], ignore_index=True)
                    conn.update(data=df_final)
                    st.session_state.carrito_comida = []
                    st.success("¡Datos guardados!")
                    st.rerun()
            else:
                st.info("Plato vacío.")

    elif opcion == "💪 Rutina de Ejercicios":
        st.header(f"Plan de Entrenamiento - {usuario_activo}")
        
        # Lógica de Rutina Basada en IMC
        if imc >= 25:
            st.warning("🎯 OBJETIVO: QUEMA DE GRASA Y TONIFICACIÓN")
            st.write("**Calentamiento:** 10 min de trote suave o saltar soga.")
            st.write("**Circuito (4 rondas):**")
            st.write("1. Sentadillas (15 reps)")
            st.write("2. Flexiones de pecho (12 reps)")
            st.write("3. Zancadas / Lunges (10 por pierna)")
            st.write("4. Plancha abdominal (45 segundos)")
            st.write("**Cardio Final:** 20 min de caminata rápida.")
        else:
            st.success("🎯 OBJETIVO: GANANCIA MUSCULAR / MANTENIMIENTO")
            st.write("**Calentamiento:** Movilidad articular 5 min.")
            st.write("**Entrenamiento (3 series de 10-12 reps):**")
            st.write("1. Sentadillas con peso (si tienes)")
            st.write("2. Dominadas o Remo con mochila")
            st.write("3. Press de hombros")
            st.write("4. Elevación de talones (pantorrillas)")
            st.write("**Nota:** Descansa 60 segundos entre series.")

        st.info("💡 Recuerda que la constancia es más importante que la intensidad inicial.")

    # Mostrar gráficas al final para ambos
    if not df_usuario.empty:
        st.divider()
        st.subheader("📉 Tu Historial")
        st.line_chart(df_usuario, x="Fecha", y="Peso")

else:
    st.info("👋 Selecciona un perfil para ver tu plan personalizado.")
