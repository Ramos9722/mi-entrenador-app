import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
import random
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Family Coach IA Pro v7", page_icon="🤖", layout="wide")

perfiles = {
    "Anderson": {"estatura": 1.57, "edad": 22, "nivel": "Elite", "cal_meta": 2200, "agua_meta": 10, "prot_meta": 110},
    "Emerson": {"estatura": 1.57, "edad": 22, "nivel": "Elite", "cal_meta": 2200, "agua_meta": 10, "prot_meta": 110},
    "Jhon": {"estatura": 1.70, "edad": 41, "nivel": "Adulto", "cal_meta": 2000, "agua_meta": 8, "prot_meta": 100},
    "Nelida": {"estatura": 1.54, "edad": 51, "nivel": "Adulto", "cal_meta": 1600, "agua_meta": 7, "prot_meta": 80},
    "Sharon": {"estatura": 1.40, "edad": 11, "nivel": "Junior", "cal_meta": 1800, "agua_meta": 7, "prot_meta": 70}
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

# --- LÓGICA DE SESIÓN ---
if 'ejercicio_actual' not in st.session_state: st.session_state.ejercicio_actual = 0
if 'entrenando' not in st.session_state: st.session_state.entrenando = False
if 'carrito_comida' not in st.session_state: st.session_state.carrito_comida = []
if 'rutina_dia' not in st.session_state: st.session_state.rutina_dia = []

conn = st.connection("gsheets", type=GSheetsConnection)
df_total = conn.read()

# --- INTERFAZ ---
st.title("👨‍👩‍👧‍👦 Family Fitness Hub: Inteligencia Nutricional")
usuario = st.selectbox("👤 ¿Quién eres?", ["Seleccionar..."] + list(perfiles.keys()))

if usuario != "Seleccionar...":
    datos_p = perfiles[usuario]
    dia_nombre = datetime.now().strftime('%A')
    
    # Datos históricos
    if not df_total.empty and 'Usuario' in df_total.columns:
        df_usuario = df_total[df_total['Usuario'] == usuario].copy()
        df_usuario['Fecha'] = pd.to_datetime(df_usuario['Fecha'])
        ultimo_peso = df_usuario['Peso'].iloc[-1] if not df_usuario.empty else 60.0
    else:
        df_usuario = pd.DataFrame(); ultimo_peso = 60.0

    opcion = st.sidebar.radio("Ir a:", ["🍎 Nutrición Inteligente", "💪 Entrenamiento IA Pro"])

    if opcion == "🍎 Nutrición Inteligente":
        st.header(f"Panel de Salud - {usuario}")
        
        # 1. ANALIZADOR DE TENDENCIAS (IA DE PESO)
        if len(df_usuario) > 1:
            peso_inicial = df_usuario['Peso'].iloc[-7] if len(df_usuario) >= 7 else df_usuario['Peso'].iloc[0]
            diferencia = ultimo_peso - peso_inicial
            if diferencia < 0:
                st.info(f"📈 **Tendencia Semanal:** Has bajado {abs(diferencia):.2f} kg. ¡Excelente progreso!")
            elif diferencia > 0:
                st.warning(f"📈 **Tendencia Semanal:** Has subido {diferencia:.2f} kg. Revisa tu ingesta de calorías.")
            else:
                st.info("📈 **Tendencia Semanal:** Tu peso se mantiene estable.")

        # 2. MÉTRICAS DE PROTEÍNA Y CALORÍAS
        cal_consumidas = sum(item['c'] for item in st.session_state.carrito_comida)
        prot_consumida = sum(item['p'] for item in st.session_state.carrito_comida)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("🔥 Calorías", f"{int(cal_consumidas)} / {datos_p['cal_meta']} kcal")
        
        # Semáforo de Proteína
        color_prot = "normal" if prot_consumida >= datos_p['prot_meta'] else "inverse"
        m2.metric("🥩 Proteína", f"{int(prot_consumida)}g", f"Meta: {datos_p['prot_meta']}g", delta_color=color_prot)
        
        m3.metric("💧 Agua", f"Meta: {datos_p['agua_meta']} vasos")

        st.divider()

        col_in, col_res = st.columns([1, 1.2])
        with col_in:
            st.subheader("📝 Registro Diario")
            
            # Opción Alimento Personalizado
            tipo_ingreso = st.radio("Tipo de ingreso:", ["Lista Peruana", "Alimento Personalizado"], horizontal=True)
            
            if tipo_ingreso == "Lista Peruana":
                com = st.selectbox("Selecciona:", list(alimentos_peru.keys()))
                can = st.number_input(f"Cantidad ({alimentos_peru[com]['medida']})", min_value=0.5, step=0.5)
                if st.button("➕ Añadir"):
                    info = alimentos_peru[com]
                    st.session_state.carrito_comida.append({"n": com, "c": info["cal"] * can, "p": info["prot"] * can})
                    st.rerun()
            else:
                n_personal = st.text_input("Nombre del alimento:")
                c_personal = st.number_input("Calorías (kcal):", min_value=0)
                p_personal = st.number_input("Proteína (g):", min_value=0)
                if st.button("➕ Añadir Personalizado"):
                    if n_personal:
                        st.session_state.carrito_comida.append({"n": n_personal, "c": c_personal, "p": p_personal})
                        st.rerun()

            st.divider()
            v_agua = st.slider("Vasos de agua:", 0, 15, 0)
            n_peso = st.number_input("⚖️ PESO ACTUAL (kg):", value=float(ultimo_peso), step=0.1)
            f_reg = st.date_input("📅 FECHA:", datetime.now())

            # CORRECCIÓN: Botón de Guardado siempre visible y funcional
            if st.button("💾 GUARDAR TODO EL DÍA (Sincronizar)", use_container_width=True, type="primary"):
                nueva_fila = pd.DataFrame({
                    "Usuario": [usuario], "Fecha": [str(f_reg)], "Peso": [n_peso],
                    "Calorias": [cal_consumidas], "Proteinas": [prot_consumida],
                    "Detalle": [", ".join([i['n'] for i in st.session_state.carrito_comida]) if st.session_state.carrito_comida else "Solo Peso/Agua"],
                    "Vasos_Agua": [v_agua]
                })
                df_final = pd.concat([df_total, nueva_fila], ignore_index=True)
                conn.update(data=df_final)
                st.session_state.carrito_comida = [] # Limpiar plato
                st.success("✅ ¡Datos guardados en la nube con éxito!")
                time.sleep(1)
                st.rerun()

        with col_res:
            st.subheader("🍽️ Tu Plato de Hoy")
            if st.session_state.carrito_comida:
                temp_df = pd.DataFrame(st.session_state.carrito_comida)
                st.dataframe(temp_df.rename(columns={'n':'Alimento','c':'kcal','p':'Prot(g)'}), use_container_width=True)
                if st.button("🗑️ Vaciar Plato"):
                    st.session_state.carrito_comida = []
                    st.rerun()
            else:
                st.info("No hay alimentos en el plato. Puedes guardar solo tu peso si lo deseas.")

    # --- SECCIÓN ENTRENAMIENTO ---
    elif opcion == "💪 Entrenamiento IA Pro":
        if dia_nombre == "Sunday":
            st.warning("🏆 ¡DOMINGO DE MEDICIÓN! Registra tu peso en Nutrición.")
        elif not st.session_state.entrenando:
            st.header(f"Tu Rutina IA - {dia_nombre}")
            if st.button("🚀 INICIAR SESIÓN"):
                random.seed(usuario + dia_nombre)
                st.session_state.rutina_dia = random.sample(banco_ejercicios[datos_p["nivel"]], 5)
                st.session_state.entrenando = True
                st.session_state.fase = "Calentamiento"
                st.rerun()
        else:
            if st.session_state.fase == "Calentamiento":
                st.subheader("🔥 Fase 1: Calentamiento")
                st.write("Movilidad articular y estiramientos dinámicos (5 min).")
                if st.button("✅ Empezar Circuito"):
                    st.session_state.fase = "Circuito"; st.rerun()
            elif st.session_state.fase == "Circuito":
                prog = st.session_state.ejercicio_actual / len(st.session_state.rutina_dia)
                st.progress(prog)
                ej = st.session_state.rutina_dia[st.session_state.ejercicio_actual]
                st.markdown(f"## {ej['icon']} {ej['n']}")
                st.info(f"Técnica: {ej['guia']}")
                if ej['t'] == 'reps':
                    st.write(f"🔢 Repeticiones: **{ej['v']}**")
                    if st.button("✅ SIGUIENTE"):
                        time.sleep(1); st.session_state.ejercicio_actual += 1
                        if st.session_state.ejercicio_actual >= 5: st.session_state.fase = "Estiramiento"
                        st.rerun()
                else:
                    st.write(f"⏱️ Tiempo: **{ej['v']}s**")
                    if st.button("▶️ INICIAR"):
                        with st.empty():
                            for s in range(ej['v'], 0, -1):
                                st.error(f"¡DALE! {s}s"); time.sleep(1)
                        st.session_state.ejercicio_actual += 1
                        if st.session_state.ejercicio_actual >= 5: st.session_state.fase = "Estiramiento"
                        st.rerun()
            elif st.session_state.fase == "Estiramiento":
                st.success("🧘 Fase final: Estiramientos estáticos."); st.balloons()
                if st.button("🏆 FINALIZAR"):
                    st.session_state.entrenando = False; st.session_state.ejercicio_actual = 0; st.rerun()

    # --- GRÁFICAS AL FINAL ---
    if not df_usuario.empty:
        st.divider(); st.subheader("📈 Tu Evolución")
        st.line_chart(df_usuario, x="Fecha", y="Peso")
