import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
import random
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Family Coach Visual Pro", page_icon="🏋️‍♂️", layout="wide")

perfiles = {
    "Anderson": {"estatura": 1.57, "edad": 22, "nivel": "Elite"},
    "Emerson": {"estatura": 1.57, "edad": 22, "nivel": "Elite"},
    "Jhon": {"estatura": 1.70, "edad": 41, "nivel": "Adulto"},
    "Nelida": {"estatura": 1.54, "edad": 51, "nivel": "Adulto"},
    "Sharon": {"estatura": 1.50, "edad": 11, "nivel": "Junior"}
}

# --- 2. BANCO DE DATOS DE EJERCICIOS CON GUÍA VISUAL ---
banco_ejercicios = {
    "Elite": [
        {"n": "Burpees Explosivos", "t": "reps", "v": 20, "d": 15, "icon": "🤸‍♂️➡️🧎‍♂️➡️🤸‍♂️", "guia": "1. De pie. 2. Baja a plancha tocando pecho al suelo. 3. Sube explosivo y salta."},
        {"n": "Flexiones Diamante", "t": "reps", "v": 15, "d": 15, "icon": "⬇️💎⬆️", "guia": "1. Manos juntas formando un diamante. 2. Baja el pecho hacia las manos. 3. Sube controlando."},
        {"n": "Sentadilla Búlgara", "t": "reps", "v": 12, "d": 20, "icon": "🧎‍♂️🔄🧍‍♂️", "guia": "1. Un pie apoyado atrás en silla. 2. Baja la cadera recta con la otra pierna. 3. Sube sin inclinarte."},
        {"n": "Plancha con saltos (Plank Jacks)", "t": "tiempo", "v": 60, "d": 10, "icon": "⏸️👐⏸️👣", "guia": "1. Posición de plancha. 2. Abre y cierra piernas saltando, sin subir la cadera."},
        {"n": "Zancadas con salto (Switch)", "t": "reps", "v": 20, "d": 15, "icon": "💥🧍‍♂️💥", "guia": "1. Posición de zancada. 2. Salta y cambia de pierna en el aire. Cae suave."}
    ],
    "Adulto": [
        {"n": "Sentadillas en pared (Wall Sit)", "t": "tiempo", "v": 45, "d": 30, "icon": "🪑⏸️🪑", "guia": "1. Espalda apoyada en pared. 2. Baja hasta 90 grados como si te sentaras. Mantén."},
        {"n": "Flexiones inclinadas", "t": "reps", "v": 12, "d": 40, "icon": "🆙⬆️", "guia": "1. Manos apoyadas en mesa o pared. 2. Baja el pecho controlado. 3. Sube con fuerza."},
        {"n": "Puente de glúteo", "t": "reps", "v": 20, "d": 30, "icon": "🆙🍑⬆️", "guia": "1. Boca arriba, pies apoyados. 2. Sube la cadera apretando glúteos. 3. Baja suave."},
        {"n": "Caminata con rodillas altas", "t": "tiempo", "v": 60, "d": 30, "icon": "🏃‍♂️🆙🏃‍♂️", "guia": "1. En el sitio, sube rodillas al pecho alternadamente. Braceo activo."}
    ],
    "Junior": [
        {"n": "Salto de cuerda (imaginaria)", "t": "tiempo", "v": 60, "d": 20, "icon": "🌀🤸‍♂️🌀", "guia": "1. Salta suave sobre puntas de pies. Mueve muñecas como si tuvieras cuerda."},
        {"n": "Skipping rápido", "t": "tiempo", "v": 40, "d": 20, "icon": "🏃‍♂️🔥🏃‍♂️", "guia": "1. Corre en el sitio muy rápido subiendo rodillas poco. Braceo veloz."},
        {"n": "Polichinelas (Jumping Jacks)", "t": "reps", "v": 30, "d": 20, "icon": "👐🤸‍♂️👐👣", "guia": "1. Abre brazos y piernas a la vez. 2. Cierra a la vez. Mantén ritmo."}
    ]
}

alimentos_peru = {
    "huevo": {"cal": 78, "prot": 6.3, "medida": "unidad"},
    "pollo": {"cal": 165, "prot": 31, "medida": "presa mediana"},
    "arroz": {"cal": 240, "prot": 4.4, "medida": "taza cocida"},
    "menestra": {"cal": 230, "prot": 15, "medida": "porcion"},
    "pan frances": {"cal": 85, "prot": 2.5, "medida": "unidad"},
    "camote": {"cal": 115, "prot": 1.3, "medida": "unidad med."},
    "papa": {"cal": 90, "prot": 2, "medida": "unidad med."},
    "leche": {"cal": 150, "prot": 8, "medida": "taza"},
    "avena": {"cal": 150, "prot": 5, "medida": "taza"}
}

# --- 3. LÓGICA DE SESIÓN ---
if 'ejercicio_actual' not in st.session_state: st.session_state.ejercicio_actual = 0
if 'entrenando' not in st.session_state: st.session_state.entrenando = False
if 'rutina_dia' not in st.session_state: st.session_state.rutina_dia = []
if 'carrito_comida' not in st.session_state: st.session_state.carrito_comida = []

conn = st.connection("gsheets", type=GSheetsConnection)
df_total = conn.read()

# --- 4. INTERFAZ ---
st.title("👨‍👩‍👧‍👦 Coach Visual Familiar Inteligente")
usuario = st.selectbox("👤 ¿Quién eres?", ["Seleccionar..."] + list(perfiles.keys()))

if usuario != "Seleccionar...":
    datos_p = perfiles[usuario]
    dia_nombre = datetime.now().strftime('%A')
    es_domingo = dia_nombre == "Sunday"

    # Filtrar datos históricos
    if not df_total.empty and 'Usuario' in df_total.columns:
        df_usuario = df_total[df_total['Usuario'] == usuario]
        ultimo_peso = df_usuario['Peso'].iloc[-1] if not df_usuario.empty else 60.0
    else:
        df_usuario = pd.DataFrame()
        ultimo_peso = 60.0

    # --- 5. LÓGICA DE DOMINGO: MEDICIÓN OBLIGATORIA ---
    if es_domingo:
        st.warning("🏆 ¡ATENCIÓN! Hoy Domingo es DÍA DE MEDICIÓN OBLIGATORIA.")
        st.subheader(f"Hola {usuario}, para ver tu progreso y el reto, necesitamos tu peso de hoy:")
        
        with st.form(key="medicion_domingo"):
            peso_domingo = st.number_input("Tu peso actual (kg):", value=float(ultimo_peso), step=0.1)
            vasos_domingo = st.number_input("Vasos de agua tomados ayer:", min_value=0, value=0)
            submit_domingo = st.form_submit_button("💾 GUARDAR MEDICIÓN SEMANAL")

        if submit_domingo:
            nueva_fila_d = pd.DataFrame({
                "Usuario": [usuario], "Fecha": [str(datetime.now().date())],
                "Peso": [peso_domingo], "Calorias": [0], "Proteinas": [0],
                "Detalle": ["Medición Domingo Obligatoria"], "Vasos_Agua": [vasos_domingo]
            })
            df_final_d = pd.concat([df_total, nueva_fila_d], ignore_index=True)
            conn.update(data=df_final_d)
            st.success("✅ Peso guardado. ¡Ahora puedes ver tu progreso semanal abajo!")
            st.rerun()

    # --- 6. MENÚ PRINCIPAL ---
    st.divider()
    opcion = st.sidebar.radio("Ir a:", ["📊 Mi Progreso (Domingo)", "🍎 Nutrición Diario", "💪 Entrenamiento IA Pro"])

    # --- 7. SECCIÓN ENTRENAMIENTO PRO CON GUÍA VISUAL ---
    if opcion == "💪 Entrenamiento IA Pro":
        if es_domingo:
            st.warning("🏆 Hoy es Domingo: Reto Familiar de Medición. El entrenamiento normal está bloqueado.")
            st.info("El reto de hoy es un reto de volumen: ¡Haz 200 Sentadillas durante el día!")
        else:
            if not st.session_state.entrenando:
                random.seed(usuario + dia_nombre)
                st.session_state.rutina_dia = random.sample(banco_ejercicios[datos_p["nivel"]], 5)
                st.header(f"Plan de {usuario} para hoy {dia_nombre}")
                
                if st.button("🚀 INICIAR ENTRENAMIENTO IA CON GUÍA VISUAL"):
                    st.session_state.entrenando = True
                    st.session_state.ejercicio_actual = 0
                    st.rerun()
            else:
                prog = st.session_state.ejercicio_actual / len(st.session_state.rutina_dia)
                st.progress(prog)
                ej = st.session_state.rutina_dia[st.session_state.ejercicio_actual]
                
                st.markdown(f"## {ej['icon']} **EJERCICIO {st.session_state.ejercicio_actual + 1}: {ej['n']}**")
                
                # LA GUÍA VISUAL Y TÉCNICA
                with st.expander("📖 Ver guía técnica (Cómo hacerlo bien)", expanded=True):
                    st.markdown(f"### {ej['icon']}")
                    st.info(f"**Técnica Correcta:**\n{ej['guia']}")
                    st.warning("💡 Mantén la forma antes que la velocidad. Si duele, para.")

                if ej['t'] == 'reps':
                    st.markdown(f"🔢 Objetivo: Haz **{ej['v']} repeticiones** explosivas.")
                    if st.button("✅ CUMPLIDO"):
                        with st.empty():
                            for s in range(ej['d'], 0, -1):
                                st.warning(f"⏳ Descansando... {s}")
                                time.sleep(1)
                        st.session_state.ejercicio_actual += 1
                        st.rerun()
                else:
                    st.markdown(f"⏱️ Objetivo: Aguanta por **{ej['v']} segundos** con intensidad.")
                    if st.button("▶️ INICIAR TIEMPO"):
                        with st.empty():
                            for s in range(ej['v'], 0, -1):
                                st.error(f"🔥 ¡DALE! Quedan {s}s")
                                time.sleep(1)
                        with st.empty():
                            for s in range(ej['d'], 0, -1):
                                st.warning(f"⏳ Descansando... {s}")
                                time.sleep(1)
                        st.session_state.ejercicio_actual += 1
                        st.rerun()

                if st.session_state.ejercicio_actual >= len(st.session_state.rutina_dia):
                    st.balloons()
                    st.success("🏆 ¡RUTINA COMPLETADA! Has dado el 100%.")
                    if st.button("Terminar sesión"):
                        st.session_state.entrenando = False
                        st.rerun()

    # (Nutrición y Gráficas se mantienen igual abajo)
