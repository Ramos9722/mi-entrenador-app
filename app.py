import streamlit as st

st.set_page_config(page_title="Coach AI Pro", page_icon="⚖️")

st.title("⚖️ Mi Coach de Transformación")

# --- Nueva entrada de datos más precisa ---
with st.sidebar:
    st.header("Perfil de Usuario")
    genero = st.radio("Género", ["Hombre", "Mujer"])
    peso = st.number_input("Peso actual (kg)", value=70.0)
    altura = st.number_input("Altura (cm)", value=170)
    edad = st.number_input("Edad", value=25)
    
    actividad = st.select_slider(
        "Nivel de actividad",
        options=["Sedentario", "Ligero", "Moderado", "Intenso"]
    )

# --- Lógica de cálculo avanzada (Mifflin-St Jeor) ---
if genero == "Hombre":
    tmb = (10 * peso) + (6.25 * altura) - (5 * edad) + 5
else:
    tmb = (10 * peso) + (6.25 * altura) - (5 * edad) - 161

# Ajuste por actividad
multiplicadores = {"Sedentario": 1.2, "Ligero": 1.375, "Moderado": 1.55, "Intenso": 1.725}
calorias_mantenimiento = tmb * multiplicadores[actividad]
calorias_perder_peso = calorias_mantenimiento - 500

# --- Mostrar resultados ---
st.metric(label="Calorías para bajar de peso", value=f"{int(calorias_perder_peso)} kcal")

# --- Generador de Lista de Compras ---
st.subheader("🛒 Lista de compras recomendada")
lista_compras = {
    "Proteínas": ["Pechuga de pollo", "Huevos", "Tofu", "Pescado blanco"],
    "Carbohidratos": ["Avena", "Arroz integral", "Camote (Batata)"],
    "Grasas": ["Aguacate", "Nueces", "Aceite de oliva"]
}

col1, col2, col3 = st.columns(3)
with col1:
    st.write("**Proteínas**")
    for p in lista_compras["Proteínas"]: st.write(f"- {p}")
with col2:
    st.write("**Carbos**")
    for c in lista_compras["Carbohidratos"]: st.write(f"- {c}")
with col3:
    st.write("**Grasas**")
    for g in lista_compras["Grasas"]: st.write(f"- {g}")

st.info("💡 Consejo: Bebe 35ml de agua por cada kilo de peso.")
