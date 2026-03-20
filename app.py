import streamlit as st # Importamos la herramienta de sitios web

# Configuración de la página
st.set_page_config(page_title="Mi Entrenador AI", page_icon="💪")

st.title("🏋️‍♂️ Mi Entrenador & Nutricionista")
st.write("Registra tus datos para obtener tu plan personalizado.")

# --- Formulario en la barra lateral ---
with st.sidebar:
    st.header("Tus Datos")
    peso = st.number_input("Peso (kg)", min_value=40.0, max_value=200.0, value=70.0)
    altura = st.number_input("Altura (cm)", min_value=100, max_value=250, value=170)
    edad = st.number_input("Edad", min_value=15, max_value=100, value=25)
    objetivo = st.selectbox("Tu objetivo", ["Bajar de peso", "Mantener peso", "Ganar músculo"])

# --- Lógica de Cálculos ---
tmb = (10 * peso) + (6.25 * altura) - (5 * edad) + 5

if objetivo == "Bajar de peso":
    calorias_finales = tmb - 500
    dieta_tipo = "Baja en carbohidratos, alta en proteína."
    rutina_tipo = "Cardio 30 min + Pesas ligeras (15 reps)."
elif objetivo == "Ganar músculo":
    calorias_finales = tmb + 300
    dieta_tipo = "Alta en proteína y carbohidratos complejos."
    rutina_tipo = "Pesas pesadas (8 reps) + Descanso activo."
else:
    calorias_finales = tmb
    dieta_tipo = "Balanceada."
    rutina_tipo = "Caminata 10k pasos + Fuerza general."

# --- Mostrar Resultados en la Web ---
st.subheader(f"🔥 Tu objetivo diario: {int(calorias_finales)} calorías")

col1, col2 = st.columns(2)

with col1:
    st.info("🍎 **Dieta Sugerida**")
    st.write(dieta_tipo)

with col2:
    st.success("💪 **Rutina Sugerida**")
    st.write(rutina_tipo)

# Botón para guardar progreso (Simulado por ahora)
if st.button("Guardar progreso de hoy"):
    st.write(f"Guardado: {peso}kg el día de hoy. ¡Sigue así!")