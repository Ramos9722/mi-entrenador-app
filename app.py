import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
import random
from datetime import datetime

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Family Coach - SISTEMA INTEGRAL v10", page_icon="🏆", layout="wide")

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
if 'factor_descanso' not in st.session_state: st.session_state.factor_descanso = 1

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
    
    # Recuperación de datos históricos y del día
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

    # --- SECCIÓN NUTRICIÓN ---
    if opcion == "🍎 Nutrición y Estadísticas":
        st.header(f"Salud de {usuario}")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("🔥 Kcal Hoy", f"{int(cal_hoy)}", f"Meta: {datos_p['cal_meta']}")
        c2.metric("🥩 Prot Hoy", f"{int(prot_hoy)}g", f"Meta: {datos_p['prot_meta']}g")
        c3.metric("💧 Agua Hoy", f"{int(agua_hoy)} vasos", f"Meta: {datos_p['agua_meta']}")

        st.divider()
        col_in, col_res = st.columns([1, 1.2])
        
        with col_in:
            st.subheader("📝 Registrar Datos")
            f_reg = st.date_input("📅 Fecha del registro:", datetime.now())
            
            if st.button("💧 Añadir 1 Vaso de Agua"):
                nueva = pd.DataFrame({"Usuario":[usuario],"Fecha":[f_reg.strftime('%Y-%m-%d')],"Peso":[ultimo_peso],"Calorias":[0],"Proteinas":[0],"Detalle":["Agua"],"Vasos_Agua":[1]})
                conn.update(data=pd.concat([df_total, nueva], ignore_index=True))
                st.rerun()
            
            st.write("---")
            n_m = st.text_input("¿Qué comiste?")
            cc1, cc2 = st.columns(2)
            c_m = cc1.number_input("Kcal:", min_value=0)
            p_m = cc2.number_input("Prot(g):", min_value=0)
            if st.button("💾 Guardar Alimento"):
                if n_m:
                    nueva = pd.DataFrame({"Usuario":[usuario],"Fecha":[f_reg.strftime('%Y-%m-%d')],"Peso":[ultimo_peso],"Calorias":[c_m],"Proteinas":[p_m],"Detalle":[n_m],"Vasos_Agua":[0]})
                    conn.update(data=pd.concat([df_total, nueva], ignore_index=True))
                    st.rerun()

            st.divider()
            n_peso = st.number_input("⚖️ Actualizar Peso (kg):", value=float(ultimo_peso))
            if st.button("⚖️ Guardar Peso"):
                nueva = pd.DataFrame({"Usuario":[usuario],"Fecha":[f_reg.strftime('%Y-%m-%d')],"Peso":[n_peso],"Calorias":[0],"Proteinas":[0],"Detalle":["Peso"],"Vasos_Agua":[0]})
                conn.update(data=pd.concat([df_total, nueva], ignore_index=True))
                st.success("Peso guardado."); st.rerun()

        with col_res:
            st.subheader("📋 Resumen del Día")
            if not df_hoy.empty:
                st.dataframe(df_hoy[['Detalle', 'Calorias', 'Proteinas', 'Vasos_Agua']], use_container_width=True)
            else: st.info("Sin registros en la fecha seleccionada.")

        # ESTADÍSTICAS
        st.divider()
        st.subheader("📊 Progreso Histórico")
        if not df_u_todo.empty:
            df_u_todo['Fecha'] = pd.to_datetime(df_u_todo['Fecha'])
            df_u_todo = df_u_todo.sort_values('Fecha')
            t1, t2 = st.tabs(["📉 Gráfica", "📅 Lista"])
            t1.line_chart(df_u_todo, x="Fecha", y="Peso")
            t2.dataframe(df_u_todo)

    # --- SECCIÓN ENTRENAMIENTO ---
    elif opcion == "💪 Entrenamiento IA Pro":
        st.header(f"Rutina IA para {usuario}")
        
        # IA de Recuperación - Influye directamente en el inicio
        with st.container(border=True):
            st.subheader("🧠 IA de Recuperación")
            sueño = st.select_slider("¿Cómo dormiste?", options=range(1,11), value=8)
            dolor = st.select_slider("¿Dolor muscular?", options=range(0,11), value=2)
            temp_factor = 2 if (sueño < 6 or dolor > 7) else 1
            
            if temp_factor == 2: st.warning("⚠️ Fatiga detectada. Se aplicará descanso doble.")
            else: st.success("✅ Cuerpo listo para el esfuerzo.")

        if not st.session_state.entrenando:
            if st.button("🚀 INICIAR ENTRENAMIENTO", type="primary", use_container_width=True):
                st.session_state.factor_descanso = temp_factor
                random.seed(usuario + hoy_str)
                st.session_state.rutina_dia = random.sample(banco_ejercicios[datos_p["nivel"]], 5)
                st.session_state.entrenando = True
                st.session_state.fase = "Calentamiento"
                st.session_state.ejercicio_actual = 0
                st.rerun()
        else:
            # Flujo de Rutina
            if st.session_state.fase == "Calentamiento":
                st.subheader("🔥 Fase 1: Calentamiento")
                st.write("Realiza movilidad articular suave por 5 minutos.")
                if st.button("✅ ¡Listo! Empezar Circuito"):
                    st.session_state.fase = "Circuito"; st.rerun()
            
            elif st.session_state.fase == "Circuito":
                ej = st.session_state.rutina_dia[st.session_state.ejercicio_actual]
                st.markdown(f"## {ej['icon']} {ej['n']}")
                st.info(f"Técnica: {ej['guia']}")
                
                if ej['t'] == 'reps':
                    st.write(f"🔢 Objetivo: **{ej['v']} repeticiones**")
                    if st.button("✅ SIGUIENTE EJERCICIO"):
                        with st.empty():
                            descanso = ej['d'] * st.session_state.factor_descanso
                            for s in range(descanso, 0, -1):
                                st.warning(f"⏳ Descanso Inteligente: {s}s"); time.sleep(1)
                        st.session_state.ejercicio_actual += 1
                        if st.session_state.ejercicio_actual >= 5: st.session_state.fase = "Estiramiento"
                        st.rerun()
                else:
                    st.write(f"⏱️ Tiempo: **{ej['v']} segundos**")
                    if st.button("▶️ INICIAR CRONÓMETRO"):
                        with st.empty():
                            for s in range(ej['v'], 0, -1):
                                st.error(f"🔥 ¡DALE! {s}s"); time.sleep(1)
                        st.session_state.ejercicio_actual += 1
                        if st.session_state.ejercicio_actual >= 5: st.session_state.fase = "Estiramiento"
                        st.rerun()
            
            elif st.session_state.fase == "Estiramiento":
                st.success("🧘 ¡Felicidades! Rutina terminada."); st.balloons()
                if st.button("🏆 TERMINAR SESIÓN"):
                    st.session_state.entrenando = False; st.rerun()
