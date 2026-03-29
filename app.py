import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
import random
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Family Coach IA Total", page_icon="🤖", layout="wide")

# 2. PERFILES (Corregido Sharon 1.40m y Metas)
perfiles = {
    "Anderson": {"estatura": 1.57, "edad": 22, "nivel": "Elite", "cal_meta": 2200, "agua_meta": 10},
    "Emerson": {"estatura": 1.57, "edad": 22, "nivel": "Elite", "cal_meta": 2200, "agua_meta": 10},
    "Jhon": {"estatura": 1.70, "edad": 41, "nivel": "Adulto", "cal_meta": 2000, "agua_meta": 8},
    "Nelida": {"estatura": 1.54, "edad": 51, "nivel": "Adulto", "cal_meta": 1600, "agua_meta": 7},
    "Sharon": {"estatura": 1.40, "edad": 11, "nivel": "Junior", "cal_meta": 1800, "agua_meta": 7}
}

alimentos_peru = {
    "huevo": {"cal": 78, "prot": 6.3, "medida": "unidad"},
    "pollo": {"cal": 165, "prot": 31, "medida": "presa med."},
    "arroz": {"cal": 240, "prot": 4.4, "medida": "taza cocida"},
    "menestra": {"cal": 230, "prot": 15, "medida": "porcion"},
    "pan frances": {"cal": 85, "prot": 2.5, "medida": "unidad"},
    "camote": {"cal": 115, "prot": 1.3, "medida": "unidad"},
    "jugo de papaya": {"cal": 120, "prot": 1, "medida": "vaso"},
    "papa": {"cal": 90, "prot": 2, "medida": "unidad"},
    "leche": {"cal": 150, "prot": 8, "medida": "taza"}
}

banco_ejercicios = {
    "Elite": [
        {"n": "Burpees Explosivos", "t": "reps", "v": 20, "d": 15, "icon": "🤸‍♂️", "guia": "Pecho al suelo y salto máximo."},
        {"n": "Flexiones Diamante", "t": "reps", "v": 15, "d": 15, "icon": "💎", "guia": "Manos juntas en forma de diamante."},
        {"n": "Sentadilla Búlgara", "t": "reps", "v": 12, "d": 20, "icon": "🍗", "guia": "Un pie en silla, baja cadera recta."},
        {"n": "Plancha Militar", "t": "tiempo", "v": 60, "d": 10, "icon": "🧗", "guia": "Sube y baja de antebrazos a manos."},
        {"n": "Zancadas con salto", "t": "reps", "v": 20, "d": 15, "icon": "💥", "guia": "Cambio de pierna explosivo en el aire."}
    ],
    "Adulto": [
        {"n": "Sentadilla en Pared", "t": "tiempo", "v": 45, "d": 30, "icon": "🧱", "guia": "90 grados. Espalda plana en pared."},
        {"n": "Flexiones Inclinadas", "t": "reps", "v": 12, "d": 40, "icon": "🆙", "guia": "Manos en mesa alta o pared."},
        {"n": "Puente de Glúteo", "t": "reps", "v": 20, "d": 30, "icon": "🍑", "guia": "Aprieta glúteos arriba 2 segundos."},
        {"n": "Caminata Rodillas Altas", "t": "tiempo", "v": 60, "d": 30, "icon": "🏃", "guia": "Braceo rítmico. Espalda derecha."}
    ],
    "Junior": [
        {"n": "Salto de Cuerda", "t": "tiempo", "v": 60, "d": 20, "icon": "➰", "guia": "Saltos cortos sobre puntas."},
        {"n": "Skipping Veloz", "t": "tiempo", "v": 40, "d": 20, "icon": "⚡", "guia": "Rodillas arriba muy rápido."},
        {"n": "Jumping Jacks", "t": "reps", "v": 30, "d": 20, "icon": "👐", "guia": "Abre y cierra brazos y piernas a la vez."}
    ]
}

# --- 3. LÓGICA DE SESIÓN ---
if 'ejercicio_actual' not in st.session_state: st.session_state.ejercicio_actual = 0
if 'entrenando' not in st.session_state: st.session_state.entrenando = False
if 'fase' not in st.session_state: st.session_state.fase = "Calentamiento"
if 'carrito_comida' not in st.session_state: st.session_state.carrito_comida = []
if 'rutina_dia' not in st.session_state: st.session_state.rutina_dia = []

conn = st.connection("gsheets", type=GSheetsConnection)
df_total = conn.read()

# --- 4. INTERFAZ ---
st.title("👨‍👩‍👧‍👦 Family Fitness Hub Pro")
usuario = st.selectbox("👤 ¿Quién eres?", ["Seleccionar..."] + list(perfiles.keys()))

if usuario != "Seleccionar...":
    datos_p = perfiles[usuario]
    dia_nombre = datetime.now().strftime('%A')
    
    # Datos históricos
    if not df_total.empty and 'Usuario' in df_total.columns:
        df_usuario = df_total[df_total['Usuario'] == usuario]
        ultimo_peso = df_usuario['Peso'].iloc[-1] if not df_usuario.empty else 60.0
    else:
        df_usuario = pd.DataFrame(); ultimo_peso = 60.0

    # Menú Lateral
    opcion = st.sidebar.radio("Ir a:", ["🍎 Nutrición y Peso", "💪 Entrenamiento IA Pro"])

    # --- SECCIÓN NUTRICIÓN ---
    if opcion == "🍎 Nutrición y Peso":
        st.header(f"Gestión Nutricional - {usuario}")
        
        cal_consumidas = sum(item['c'] for item in st.session_state.carrito_comida)
        cal_restantes = datos_p['cal_meta'] - cal_consumidas
        
        m1, m2, m3 = st.columns(3)
        if cal_consumidas > datos_p['cal_meta']:
            exceso = int(cal_consumidas - datos_p['cal_meta'])
            m1.metric("🔥 Calorías Hoy", f"{int(cal_consumidas)} kcal", f"Exceso: {exceso}", delta_color="inverse")
            st.error(f"⚠️ ¡Cuidado {usuario}! Has superado tu meta por {exceso} kcal.")
        else:
            m1.metric("🍎 Calorías Hoy", f"{int(cal_consumidas)} kcal", f"Faltan: {int(cal_restantes)}")
        m2.metric("🎯 Tu Meta", f"{datos_p['cal_meta']} kcal")
        m3.metric("💧 Meta Agua", f"{datos_p['agua_meta']} vasos")

        st.divider()

        col_in, col_res = st.columns([1, 1.2])
        with col_in:
            with st.expander("📝 Añadir al Plato", expanded=True):
                mom = st.selectbox("Momento:", ["Desayuno", "Almuerzo", "Cena", "Snack"])
                com = st.selectbox("Alimento:", list(alimentos_peru.keys()))
                can = st.number_input(f"Cantidad ({alimentos_peru[com]['medida']})", min_value=0.5, step=0.5)
                if st.button("➕ Añadir"):
                    info = alimentos_peru[com]
                    st.session_state.carrito_comida.append({"m": mom, "n": com, "c": info["cal"] * can, "p": info["prot"] * can})
                    st.rerun()
            
            v_agua = st.slider(f"Vasos tomados (Meta: {datos_p['agua_meta']})", 0, 15, 0)
            if v_agua >= datos_p['agua_meta']:
                st.success(f"✅ Meta de agua alcanzada ({v_agua}/{datos_p['agua_meta']})")
            else:
                st.warning(f"🚰 Te faltan {datos_p['agua_meta'] - v_agua} vasos.")

            n_peso = st.number_input("⚖️ Peso actual (kg):", value=float(ultimo_peso), step=0.1)
            f_reg = st.date_input("📅 Fecha:", datetime.now())

        with col_res:
            st.subheader("🍽️ Resumen del Plato")
            if st.session_state.carrito_comida:
                temp_df = pd.DataFrame(st.session_state.carrito_comida)
                st.dataframe(temp_df.rename(columns={'m':'Momento','n':'Alimento','c':'kcal','p':'Prot(g)'}), use_container_width=True)
                total_p = temp_df['p'].sum()
                if st.button("💾 GUARDAR DÍA COMPLETO"):
                    nueva_fila = pd.DataFrame({
                        "Usuario": [usuario], "Fecha": [str(f_reg)], "Peso": [n_peso],
                        "Calorias": [cal_consumidas], "Proteinas": [total_p],
                        "Detalle": [", ".join(temp_df['n'])], "Vasos_Agua": [v_agua]
                    })
                    df_final = pd.concat([df_total, nueva_fila], ignore_index=True)
                    conn.update(data=df_final)
                    st.session_state.carrito_comida = []
                    st.success("¡Datos guardados!")
                    st.rerun()
            else: st.info("Plato vacío.")

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
