import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
import random
from datetime import datetime

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Family Coach - ELITE v9.1", page_icon="🏆", layout="wide")

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
if 'ejercicio_actual' not in st.session_state: st.session_state.ejercicio_actual = 0
if 'entrenando' not in st.session_state: st.session_state.entrenando = False
if 'fase' not in st.session_state: st.session_state.fase = "Calentamiento"

conn = st.connection("gsheets", type=GSheetsConnection)
df_total = conn.read(ttl=0)

# --- BARRA DE PODER ---
st.markdown("### ⚡ Barra de Poder Familiar")
hoy_str = datetime.now().strftime('%Y-%m-%d')
activos = df_total[df_total['Fecha'] == hoy_str]['Usuario'].nunique() if not df_total.empty else 0
st.progress(activos / len(perfiles))

usuario = st.selectbox("👤 ¿Quién eres?", ["Seleccionar..."] + list(perfiles.keys()))

if usuario != "Seleccionar...":
    datos_p = perfiles[usuario]
    
    # --- RECUPERACIÓN DE DATOS (Persistencia) ---
    if not df_total.empty:
        df_u_todo = df_total[df_total['Usuario'] == usuario].copy()
        df_hoy = df_u_todo[df_u_todo['Fecha'] == hoy_str]
        
        cal_hoy = df_hoy['Calorias'].sum()
        prot_hoy = df_hoy['Proteinas'].sum()
        agua_hoy = df_hoy['Vasos_Agua'].sum()
        ultimo_peso = df_u_todo['Peso'].iloc[-1] if not df_u_todo.empty else 60.0
    else:
        df_u_todo = pd.DataFrame()
        cal_hoy, prot_hoy, agua_hoy, ultimo_peso = 0, 0, 0, 60.0

    opcion = st.sidebar.radio("Menú:", ["🍎 Nutrición y Estadísticas", "💪 Entrenamiento IA Pro"])

    if opcion == "🍎 Nutrición y Estadísticas":
        st.header(f"Salud de {usuario}")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("🔥 Kcal Hoy", f"{int(cal_hoy)}", f"Meta: {datos_p['cal_meta']}")
        c2.metric("🥩 Prot Hoy", f"{int(prot_hoy)}g", f"Meta: {datos_p['prot_meta']}g")
        c3.metric("💧 Agua Hoy", f"{int(agua_hoy)} vasos", f"Meta: {datos_p['agua_meta']}")

        st.divider()
        col_in, col_res = st.columns([1, 1.2])
        
        with col_in:
            st.subheader("➕ Registro Rápido")
            if st.button("💧 Añadir 1 Vaso de Agua"):
                nueva = pd.DataFrame({"Usuario":[usuario],"Fecha":[hoy_str],"Peso":[ultimo_peso],"Calorias":[0],"Proteinas":[0],"Detalle":["Agua"],"Vasos_Agua":[1]})
                conn.update(data=pd.concat([df_total, nueva], ignore_index=True))
                st.rerun()
            
            st.write("---")
            n_m = st.text_input("¿Qué comiste? (ej: Almuerzo)")
            cc1, cc2 = st.columns(2)
            c_m = cc1.number_input("Kcal:", min_value=0)
            p_m = cc2.number_input("Prot(g):", min_value=0)
            if st.button("💾 Guardar Alimento"):
                if n_m:
                    nueva = pd.DataFrame({"Usuario":[usuario],"Fecha":[hoy_str],"Peso":[ultimo_peso],"Calorias":[c_m],"Proteinas":[p_m],"Detalle":[n_m],"Vasos_Agua":[0]})
                    conn.update(data=pd.concat([df_total, nueva], ignore_index=True))
                    st.rerun()

            st.divider()
            n_peso = st.number_input("⚖️ Actualizar Peso (kg):", value=float(ultimo_peso))
            if st.button("⚖️ Guardar Peso"):
                nueva = pd.DataFrame({"Usuario":[usuario],"Fecha":[hoy_str],"Peso":[n_peso],"Calorias":[0],"Proteinas":[0],"Detalle":["Peso"],"Vasos_Agua":[0]})
                conn.update(data=pd.concat([df_total, nueva], ignore_index=True))
                st.success("Peso guardado."); st.rerun()

        with col_res:
            st.subheader("📋 Resumen de Hoy")
            if not df_hoy.empty:
                st.dataframe(df_hoy[['Detalle', 'Calorias', 'Proteinas', 'Vasos_Agua']], use_container_width=True)
            else: st.info("Sin registros hoy.")

        # --- 📈 SECCIÓN DE ESTADÍSTICAS (Añadida) ---
        st.divider()
        st.subheader("📊 Análisis de Progreso")
        if not df_u_todo.empty:
            df_u_todo['Fecha'] = pd.to_datetime(df_u_todo['Fecha'])
            df_u_todo = df_u_todo.sort_values('Fecha')
            
            t1, t2 = st.tabs(["📉 Gráfica de Peso", "📅 Historial Completo"])
            with t1:
                st.line_chart(df_u_todo, x="Fecha", y="Peso")
            with t2:
                st.dataframe(df_u_todo[["Fecha", "Peso", "Calorias", "Proteinas", "Vasos_Agua", "Detalle"]], use_container_width=True)
        else:
            st.warning("Aún no hay datos históricos para graficar.")

    elif opcion == "💪 Entrenamiento IA Pro":
        st.header(f"Rutina IA para {usuario}")
        with st.expander("🧠 IA de Recuperación"):
            sueño = st.select_slider("¿Cómo dormiste?", options=range(1,11), value=8)
            dolor = st.select_slider("¿Dolor?", options=range(0,11), value=2)
            f_desc = 2 if (sueño < 6 or dolor > 7) else 1

        if not st.session_state.entrenando:
            if st.button("🚀 INICIAR ENTRENAMIENTO"):
                random.seed(usuario + hoy_str)
                st.session_state.rutina_dia = random.sample(banco_ejercicios[datos_p["nivel"]], 5)
                st.session_state.entrenando = True
                st.session_state.fase = "Calentamiento"
                st.session_state.ejercicio_actual = 0
                st.rerun()
        else:
            if st.session_state.fase == "Calentamiento":
                st.subheader("🔥 Fase 1: Calentamiento")
                if st.button("✅ ¡Listo! Empezar"): st.session_state.fase = "Circuito"; st.rerun()
            elif st.session_state.fase == "Circuito":
                ej = st.session_state.rutina_dia[st.session_state.ejercicio_actual]
                st.markdown(f"## {ej['icon']} {ej['n']}")
                if ej['t'] == 'reps':
                    st.write(f"🔢 Reps: **{ej['v']}**")
                    if st.button("✅ SIGUIENTE"):
                        with st.empty():
                            for s in range(ej['d']*f_desc, 0, -1): st.warning(f"⏳ Descanso: {s}s"); time.sleep(1)
                        st.session_state.ejercicio_actual += 1
                        if st.session_state.ejercicio_actual >= 5: st.session_state.fase = "Estiramiento"
                        st.rerun()
                else:
                    st.write(f"⏱️ Tiempo: **{ej['v']}s**")
                    if st.button("▶️ START"):
                        with st.empty():
                            for s in range(ej['v'], 0, -1): st.error(f"🔥 {s}s"); time.sleep(1)
                        st.session_state.ejercicio_actual += 1
                        if st.session_state.ejercicio_actual >= 5: st.session_state.fase = "Estiramiento"
                        st.rerun()
            elif st.session_state.fase == "Estiramiento":
                st.success("🧘 Finalizado."); st.balloons()
                if st.button("🏆 TERMINAR"): st.session_state.entrenando = False; st.rerun()
