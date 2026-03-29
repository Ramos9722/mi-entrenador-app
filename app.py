import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
import random
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Family Coach GOLD EDITION", page_icon="🏆", layout="wide")

# 2. PERFILES Y METAS INTELIGENTES
perfiles = {
    "Anderson": {"estatura": 1.57, "edad": 22, "nivel": "Elite", "cal_meta": 2200, "agua_meta": 10, "prot_meta": 90},
    "Emerson": {"estatura": 1.57, "edad": 22, "nivel": "Elite", "cal_meta": 2200, "agua_meta": 10, "prot_meta": 90},
    "Jhon": {"estatura": 1.70, "edad": 41, "nivel": "Adulto", "cal_meta": 2000, "agua_meta": 8, "prot_meta": 80},
    "Nelida": {"estatura": 1.50, "edad": 51, "nivel": "Adulto", "cal_meta": 1600, "agua_meta": 8, "prot_meta": 70},
    "Sharon": {"estatura": 1.47, "edad": 11, "nivel": "Junior", "cal_meta": 1800, "agua_meta": 7, "prot_meta": 60}
}

alimentos_peru = {
    "huevo": {"cal": 78, "prot": 6.3, "medida": "unidad"},
    "pollo": {"cal": 165, "prot": 31, "medida": "presa med."},
    "arroz": {"cal": 240, "prot": 4.4, "medida": "taza cocida"},
    "menestra": {"cal": 230, "prot": 15, "medida": "porcion"},
    "pan frances": {"cal": 85, "prot": 2.5, "medida": "unidad"},
    "camote": {"cal": 115, "prot": 1.3, "medida": "unidad"},
    "papa": {"cal": 90, "prot": 2, "medida": "unidad"}
}

banco_ejercicios = {
    "Elite": [
        {"n": "Burpees Explosivos", "t": "reps", "v": 20, "d": 15, "icon": "🤸‍♂️", "guia": "Pecho al suelo y salto máximo."},
        {"n": "Flexiones Diamante", "t": "reps", "v": 15, "d": 15, "icon": "💎", "guia": "Manos juntas en diamante."},
        {"n": "Sentadilla Búlgara", "t": "reps", "v": 12, "d": 20, "icon": "🍗", "guia": "Un pie en silla, baja recto."},
        {"n": "Plancha Militar", "t": "tiempo", "v": 60, "d": 10, "icon": "🧗", "guia": "Sube y baja antebrazos/manos."},
        {"n": "Zancadas con salto", "t": "reps", "v": 20, "d": 15, "icon": "💥", "guia": "Cambio explosivo en el aire."}
    ],
    "Adulto": [
        {"n": "Sentadilla Pared", "t": "tiempo", "v": 45, "d": 30, "icon": "🧱", "guia": "90 grados, espalda plana."},
        {"n": "Flexiones Inclinadas", "t": "reps", "v": 12, "d": 40, "icon": "🆙", "guia": "Manos en mesa o pared."},
        {"n": "Puente Glúteo", "t": "reps", "v": 20, "d": 30, "icon": "🍑", "guia": "Aprieta arriba 2 segundos."},
        {"n": "Caminata Rodillas Altas", "t": "tiempo", "v": 60, "d": 30, "icon": "🏃", "guia": "Braceo activo, espalda derecha."}
    ],
    "Junior": [
        {"n": "Salto Cuerda", "t": "tiempo", "v": 60, "d": 20, "icon": "➰", "guia": "Puntas de pies."},
        {"n": "Skipping Veloz", "t": "tiempo", "v": 40, "d": 20, "icon": "⚡", "guia": "Rodillas arriba rápido."},
        {"n": "Jumping Jacks", "t": "reps", "v": 30, "d": 20, "icon": "👐", "guia": "Abre y cierra todo a la vez."}
    ]
}

# --- 3. SESIÓN ---
for key in ['ejercicio_actual', 'entrenando', 'fase', 'carrito_comida', 'rutina_dia']:
    if key not in st.session_state:
        if key == 'fase': st.session_state[key] = "Calentamiento"
        elif key == 'ejercicio_actual': st.session_state[key] = 0
        elif key == 'entrenando': st.session_state[key] = False
        else: st.session_state[key] = []

conn = st.connection("gsheets", type=GSheetsConnection)
df_total = conn.read()

# --- 4. BARRA DE PODER FAMILIAR (GLOBAL) ---
st.markdown("### ⚡ Barra de Poder Familiar")
hoy_str = datetime.now().strftime('%Y-%m-%d')
usuarios_activos = df_total[df_total['Fecha'] == hoy_str]['Usuario'].nunique() if not df_total.empty else 0
poder_total = (usuarios_activos / len(perfiles))
st.progress(poder_total)
st.caption(f"Integrantes activos hoy: {usuarios_activos} de {len(perfiles)}. ¡Sincronicen sus datos para subir el poder!")

usuario = st.selectbox("👤 Selecciona tu perfil:", ["Seleccionar..."] + list(perfiles.keys()))

if usuario != "Seleccionar...":
    datos_p = perfiles[usuario]
    dia_nombre = datetime.now().strftime('%A')
    
    # Datos históricos
    df_u = df_total[df_total['Usuario'] == usuario].copy() if not df_total.empty else pd.DataFrame()
    ultimo_peso = df_u['Peso'].iloc[-1] if not df_u.empty else 60.0

    opcion = st.sidebar.radio("Menú Principal:", ["🍎 Nutrición e IA de Peso", "💪 Entrenamiento & Recuperación"])

    # --- SECCIÓN NUTRICIÓN ---
    if opcion == "🍎 Nutrición e IA de Peso":
        st.header(f"Gestión de Salud - {usuario}")

        # 1. FORZAR LECTURA FRESCA DEL EXCEL (Para ver cambios al instante)
        # Esto asegura que no se "pise" la información vieja
        df_total = conn.read(ttl=0) 
        df_u = df_total[df_total['Usuario'] == usuario].copy() if not df_total.empty else pd.DataFrame()

        # --- MEMORIA TEMPORAL ---
        if f'agua_hoy_{usuario}' not in st.session_state:
            st.session_state[f'agua_hoy_{usuario}'] = 0
        
        cal_hoy = sum(i['c'] for i in st.session_state.carrito_comida)
        prot_hoy = sum(i['p'] for i in st.session_state.carrito_comida)
        agua_acumulada = st.session_state[f'agua_hoy_{usuario}']

        # --- PANEL DE MÉTRICAS ACTUALES ---
        c1, c2, c3 = st.columns(3)
        c1.metric("🔥 Kcal Acumuladas", f"{int(cal_hoy)}", f"Meta: {datos_p['cal_meta']}")
        c2.metric("🥩 Proteína Total", f"{int(prot_hoy)}g", f"Meta: {datos_p['prot_meta']}g")
        c3.metric("💧 Agua Tomada", f"{agua_acumulada} vasos", f"Meta: {datos_p['agua_meta']}")

        st.divider()

        col_in, col_res = st.columns([1, 1.2])
        
        with col_in:
            st.subheader("➕ Registro de Hoy")
            
            # Registro de Agua
            c_agua1, c_agua2 = st.columns(2)
            if c_agua1.button("➕ Tomé 1 Vaso"):
                st.session_state[f'agua_hoy_{usuario}'] += 1
                st.rerun()
            if c_agua2.button("🧹 Reiniciar Agua"):
                st.session_state[f'agua_hoy_{usuario}'] = 0
                st.rerun()

            # Registro de Comida
            n_m = st.text_input("¿Qué comiste ahora?")
            cc1, cc2 = st.columns(2)
            c_m = cc1.number_input("Kcal:", min_value=0, step=10)
            p_m = cc2.number_input("Prot(g):", min_value=0, step=1)
            
            if st.button("➕ Añadir al Plato del Día", use_container_width=True):
                if n_m:
                    st.session_state.carrito_comida.append({"n": n_m, "c": c_m, "p": p_m})
                    st.rerun()

            st.divider()
            n_peso = st.number_input("⚖️ Peso actual (kg):", value=float(ultimo_peso))
            f_reg = st.date_input("📅 Fecha de este registro:", datetime.now())

            # BOTÓN DE GUARDADO DEFINITIVO (Crea nueva fila)
            if st.button("🚀 FINALIZAR Y GUARDAR DÍA (Crea Nueva Fila)", type="primary", use_container_width=True):
                detalles = ", ".join([i['n'] for i in st.session_state.carrito_comida]) if st.session_state.carrito_comida else "Solo Peso/Agua"
                
                # Creamos el nuevo registro
                nueva_fila = pd.DataFrame({
                    "Usuario": [usuario], 
                    "Fecha": [f_reg.strftime('%Y-%m-%d')], # Formato estándar de fecha
                    "Peso": [n_peso], 
                    "Calorias": [cal_hoy], 
                    "Proteinas": [prot_hoy], 
                    "Detalle": [detalles], 
                    "Vasos_Agua": [agua_acumulada]
                })
                
                # Unimos lo nuevo con lo viejo y subimos
                actualizado = pd.concat([df_total, nueva_fila], ignore_index=True)
                conn.update(data=actualizado)
                
                # Limpiamos para el día siguiente
                st.session_state.carrito_comida = []
                st.session_state[f'agua_hoy_{usuario}'] = 0
                st.success("✅ ¡Datos guardados exitosamente como una nueva entrada!")
                time.sleep(1)
                st.rerun()

        with col_res:
            st.subheader("📋 Resumen de Ingesta")
            if st.session_state.carrito_comida:
                st.table(pd.DataFrame(st.session_state.carrito_comida))
            else:
                st.info("No hay alimentos anotados aún.")

        # --- 📈 PANEL DE ESTADÍSTICAS Y GRÁFICAS (SIEMPRE VISIBLE) ---
        st.divider()
        st.subheader(f"📊 Evolución Histórica: {usuario}")
        
        if not df_u.empty:
            # Aseguramos que la fecha sea reconocida como tal para la gráfica
            df_u['Fecha'] = pd.to_datetime(df_u['Fecha'])
            df_u = df_u.sort_values('Fecha') # Ordenar por fecha para que la línea tenga sentido

            tab1, tab2 = st.tabs(["📉 Gráfica de Peso", "📋 Historial Completo"])
            
            with tab1:
                st.line_chart(df_u, x="Fecha", y="Peso")
            
            with tab2:
                st.dataframe(df_u[["Fecha", "Peso", "Calorias", "Proteinas", "Vasos_Agua", "Detalle"]], use_container_width=True)
                
            # Analizador de Tendencia (Comparación entre las dos últimas filas)
            if len(df_u) >= 2:
                ultimo = df_u['Peso'].iloc[-1]
                anterior = df_u['Peso'].iloc[-2]
                cambio = ultimo - anterior
                if cambio < 0:
                    st.success(f"💪 ¡Genial! Has bajado {abs(cambio):.2f}kg desde tu último registro.")
                elif cambio > 0:
                    st.warning(f"⚠️ Has subido {cambio:.2f}kg. ¡A ajustar esa dieta!")
        else:
            st.warning("Aún no tienes registros guardados. ¡Guarda tu primer día para ver las gráficas!")

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
