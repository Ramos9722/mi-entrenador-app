import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
import random
from datetime import datetime

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Family Coach GOLD v8.1", page_icon="🏆", layout="wide")

perfiles = {
    "Anderson": {"estatura": 1.57, "edad": 22, "nivel": "Elite", "cal_meta": 2200, "agua_meta": 10, "prot_meta": 110},
    "Emerson": {"estatura": 1.57, "edad": 22, "nivel": "Elite", "cal_meta": 2200, "agua_meta": 10, "prot_meta": 110},
    "Jhon": {"estatura": 1.70, "edad": 41, "nivel": "Adulto", "cal_meta": 2000, "agua_meta": 8, "prot_meta": 100},
    "Nelida": {"estatura": 1.54, "edad": 51, "nivel": "Adulto", "cal_meta": 1600, "agua_meta": 7, "prot_meta": 80},
    "Sharon": {"estatura": 1.40, "edad": 11, "nivel": "Junior", "cal_meta": 1800, "agua_meta": 7, "prot_meta": 70}
}

banco_ejercicios = {
    "Elite": [
        {"n": "Burpees Explosivos", "t": "reps", "v": 20, "d": 15, "icon": "🤸‍♂️", "guia": "Pecho al suelo y salto máximo."},
        {"n": "Flexiones Diamante", "t": "reps", "v": 15, "d": 15, "icon": "💎", "guia": "Manos juntas en diamante."},
        {"n": "Sentadilla Búlgara", "t": "reps", "v": 12, "d": 20, "icon": "🍗", "guia": "Un pie en silla, baja recto."},
        {"n": "Plancha Militar", "t": "tiempo", "v": 60, "d": 10, "icon": "🧗", "guia": "Sube/baja antebrazos."},
        {"n": "Zancadas con salto", "t": "reps", "v": 20, "d": 15, "icon": "💥", "guia": "Cambio explosivo."}
    ],
    "Adulto": [
        {"n": "Sentadilla Pared", "t": "tiempo", "v": 45, "d": 30, "icon": "🧱", "guia": "90 grados."},
        {"n": "Flexiones Inclinadas", "t": "reps", "v": 12, "d": 40, "icon": "🆙", "guia": "Manos en mesa o pared."},
        {"n": "Puente Glúteo", "t": "reps", "v": 20, "d": 30, "icon": "🍑", "guia": "Aprieta arriba."},
        {"n": "Caminata Rodillas Altas", "t": "tiempo", "v": 60, "d": 30, "icon": "🏃", "guia": "Braceo activo."}
    ],
    "Junior": [
        {"n": "Salto Cuerda", "t": "tiempo", "v": 60, "d": 20, "icon": "➰", "guia": "Puntas de pies."},
        {"n": "Skipping Veloz", "t": "tiempo", "v": 40, "d": 20, "icon": "⚡", "guia": "Rodillas arriba."},
        {"n": "Jumping Jacks", "t": "reps", "v": 30, "d": 20, "icon": "👐", "guia": "Abre y cierra todo."}
    ]
}

# --- SESIÓN ---
for key in ['ejercicio_actual', 'entrenando', 'fase', 'carrito_comida', 'rutina_dia']:
    if key not in st.session_state:
        if key == 'fase': st.session_state[key] = "Calentamiento"
        elif key == 'ejercicio_actual': st.session_state[key] = 0
        elif key == 'entrenando': st.session_state[key] = False
        else: st.session_state[key] = []

# Conexión mejorada: ttl de 5 segundos para evitar bloqueos de Google API
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df_total = conn.read(ttl=5)
except Exception:
    st.error("⚠️ Error de conexión con Google Sheets. Reintentando...")
    time.sleep(2)
    st.rerun()

# --- BARRA DE PODER ---
st.markdown("### ⚡ Barra de Poder Familiar")
hoy_str = datetime.now().strftime('%Y-%m-%d')
usuarios_activos = df_total[df_total['Fecha'] == hoy_str]['Usuario'].nunique() if not df_total.empty else 0
st.progress(usuarios_activos / len(perfiles))

usuario = st.selectbox("👤 ¿Quién eres?", ["Seleccionar..."] + list(perfiles.keys()))

if usuario != "Seleccionar...":
    datos_p = perfiles[usuario]
    if f'agua_hoy_{usuario}' not in st.session_state: st.session_state[f'agua_hoy_{usuario}'] = 0
    
    df_u = df_total[df_total['Usuario'] == usuario].copy() if not df_total.empty else pd.DataFrame()
    ultimo_peso = df_u['Peso'].iloc[-1] if not df_u.empty else 60.0

    opcion = st.sidebar.radio("Menú:", ["🍎 Nutrición e Historial", "💪 Entrenamiento IA Pro"])

    if opcion == "🍎 Nutrición e Historial":
        st.header(f"Salud de {usuario}")
        
        cal_hoy = sum(i['c'] for i in st.session_state.carrito_comida)
        prot_hoy = sum(i['p'] for i in st.session_state.carrito_comida)
        agua_hoy = st.session_state[f'agua_hoy_{usuario}']
        
        c1, c2, c3 = st.columns(3)
        c1.metric("🔥 Kcal Hoy", f"{int(cal_hoy)}", f"Meta: {datos_p['cal_meta']}")
        c2.metric("🥩 Prot Hoy", f"{int(prot_hoy)}g", f"Meta: {datos_p['prot_meta']}g")
        c3.metric("💧 Agua Hoy", f"{agua_hoy} vasos", f"Meta: {datos_p['agua_meta']}")

        st.divider()
        col_in, col_res = st.columns([1, 1.2])
        
        with col_in:
            st.subheader("➕ Añadir Consumo")
            if st.button("➕ Tomé 1 Vaso de Agua"): 
                st.session_state[f'agua_hoy_{usuario}'] += 1
                st.rerun()
            
            st.write("---")
            n_m = st.text_input("¿Qué comiste? (ej: Almuerzo - Pollo)")
            cc1, cc2 = st.columns(2)
            c_m = cc1.number_input("Kcal:", min_value=0)
            p_m = cc2.number_input("Prot(g):", min_value=0)
            if st.button("➕ Agregar al Resumen Temporal"):
                if n_m: 
                    st.session_state.carrito_comida.append({"n": n_m, "c": c_m, "p": p_m})
                    st.rerun()

            st.divider()
            n_peso = st.number_input("⚖️ Peso (kg):", value=float(ultimo_peso))
            f_reg = st.date_input("📅 Fecha:", datetime.now())

            if st.button("🚀 FINALIZAR Y GUARDAR DÍA", type="primary", use_container_width=True):
                detalles = ", ".join([i['n'] for i in st.session_state.carrito_comida]) if st.session_state.carrito_comida else "Solo Registro"
                fila = pd.DataFrame({"Usuario": [usuario], "Fecha": [f_reg.strftime('%Y-%m-%d')], "Peso": [n_peso], "Calorias": [cal_hoy], "Proteinas": [prot_hoy], "Detalle": [detalles], "Vasos_Agua": [agua_hoy]})
                actualizado = pd.concat([df_total, fila], ignore_index=True)
                conn.update(data=actualizado)
                st.session_state.carrito_comida = []
                st.session_state[f'agua_hoy_{usuario}'] = 0
                st.success("✅ Guardado en la nube.")
                time.sleep(1); st.rerun()

        with col_res:
            st.subheader("📋 Resumen Temporal")
            if st.session_state.carrito_comida:
                st.table(pd.DataFrame(st.session_state.carrito_comida))
                if st.button("🗑️ Vaciar Plato"): 
                    st.session_state.carrito_comida = []; st.rerun()
            else: st.info("Plato vacío. Los datos se guardan al final del día.")

        st.divider()
        st.subheader("📊 Evolución")
        if not df_u.empty:
            df_u['Fecha'] = pd.to_datetime(df_u['Fecha'])
            df_u = df_u.sort_values('Fecha')
            st.line_chart(df_u, x="Fecha", y="Peso")
        else: st.info("Sin historial aún.")

    # --- SECCIÓN ENTRENAMIENTO ---
    elif opcion == "💪 Entrenamiento & Recuperación":
        st.header("🤖 Motor de Entrenamiento IA Pro")
        
        with st.expander("🧠 IA de Recuperación", expanded=True):
            sueño = st.select_slider("¿Cómo dormiste?", options=range(1,11), value=8)
            dolor = st.select_slider("¿Dolor muscular?", options=range(0,11), value=2)
            f_descanso = 2 if (sueño < 6 or dolor > 7) else 1
            if f_descanso == 2: st.warning("IA: Fatiga alta detectada. Descansos duplicados.")
            else: st.success("IA: Cuerpo en óptimas condiciones.")

        if dia_nombre == "Sunday":
            st.warning("🏆 ¡DOMINGO DE MEDICIÓN! El reto es pesar y 200 sentadillas.")
        elif not st.session_state.entrenando:
            if st.button("🚀 INICIAR RUTINA ADAPTATIVA"):
                random.seed(usuario + dia_nombre)
                st.session_state.rutina_dia = random.sample(banco_ejercicios[datos_p["nivel"]], 5)
                st.session_state.entrenando = True; st.session_state.fase = "Calentamiento"; st.rerun()
        else:
            if st.session_state.fase == "Calentamiento":
                st.subheader("🔥 Fase 1: Calentamiento")
                if st.button("✅ Empezar"): st.session_state.fase = "Circuito"; st.rerun()
            elif st.session_state.fase == "Circuito":
                ej = st.session_state.rutina_dia[st.session_state.ejercicio_actual]
                st.markdown(f"## {ej['icon']} {ej['n']}")
                st.caption(f"Guía: {ej['guia']}")
                if ej['t'] == 'reps':
                    st.write(f"🔢 Reps: **{ej['v']}**")
                    if st.button("✅ HECHO"):
                        with st.empty():
                            for s in range(ej['d']*f_descanso, 0, -1):
                                st.warning(f"⏳ Descanso IA: {s}s"); time.sleep(1)
                        st.session_state.ejercicio_actual += 1
                        if st.session_state.ejercicio_actual >= 5: st.session_state.fase = "Estiramiento"
                        st.rerun()
                else:
                    st.write(f"⏱️ Tiempo: **{ej['v']}s**")
                    if st.button("▶️ START"):
                        with st.empty():
                            for s in range(ej['v'], 0, -1):
                                st.error(f"🔥 ¡DALE! {s}s"); time.sleep(1)
                        st.session_state.ejercicio_actual += 1
                        if st.session_state.ejercicio_actual >= 5: st.session_state.fase = "Estiramiento"
                        st.rerun()
            elif st.session_state.fase == "Estiramiento":
                st.success("🧘 ¡Felicidades!"); st.balloons()
                if st.button("🏆 TERMINAR"): st.session_state.entrenando = False; st.session_state.ejercicio_actual = 0; st.rerun()
