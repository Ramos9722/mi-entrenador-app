import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
import random
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Family Fitness ULTRA v12", page_icon="🏋️‍♂️", layout="wide")

# 2. PERFILES Y ESTATURAS CORREGIDAS
perfiles = {
    "Anderson": {"estatura": 1.57, "edad": 22, "nivel": "Elite"},
    "Emerson": {"estatura": 1.57, "edad": 22, "nivel": "Elite"},
    "Jhon": {"estatura": 1.70, "edad": 41, "nivel": "Adulto"},
    "Nelida": {"estatura": 1.50, "edad": 51, "nivel": "Adulto"},
    "Sharon": {"estatura": 1.47, "edad": 11, "nivel": "Junior"}
}

# --- 3. BASE DE DATOS DE EJERCICIOS INTEGRADA ---
def nuevo_ejercicio(n, t, v, d, icon, guia, grupo, impacto, equipo, nivel, objetivo):
    return {"n": n, "t": t, "v": v, "d": d, "icon": icon, "guia": guia, "grupo": grupo, "impacto": impacto, "equipo": equipo, "nivel": nivel, "objetivo": objetivo}

banco_ejercicios = {
    "Elite": [
        nuevo_ejercicio("Burpees", "reps", 20, 15, "🤸‍♂️", "Pecho al suelo y salto completo.", "cardio_fuerza", "alto", "ninguno", "alto", "quema_grasa"),
        nuevo_ejercicio("Burpee con flexión", "reps", 15, 20, "🔥", "Añade flexión completa antes del salto.", "cardio_fuerza", "alto", "ninguno", "alto", "quema_grasa"),
        nuevo_ejercicio("Burpee con salto alto", "reps", 15, 20, "🚀", "Explota en el salto final.", "cardio_fuerza", "alto", "ninguno", "alto", "potencia"),
        nuevo_ejercicio("Sprint en sitio", "tiempo", 30, 20, "🏃", "Máxima intensidad controlada.", "cardio", "alto", "ninguno", "alto", "quema_grasa"),
        nuevo_ejercicio("High knees", "tiempo", 45, 20, "🔥", "Rodillas arriba y ritmo alto.", "cardio", "alto", "ninguno", "alto", "quema_grasa"),
        nuevo_ejercicio("Jumping jacks rápidos", "tiempo", 60, 20, "⭐", "Mantén un ritmo alto y constante.", "cardio", "medio", "ninguno", "medio", "resistencia"),
        nuevo_ejercicio("Jump rope veloz", "tiempo", 60, 25, "➰", "Saltos cortos y rápidos.", "cardio", "medio", "cuerda", "alto", "quema_grasa"),
        nuevo_ejercicio("Double unders", "reps", 40, 30, "🪢", "Haz pasar la cuerda dos veces por salto.", "cardio", "alto", "cuerda", "alto", "potencia"),
        nuevo_ejercicio("Mountain climbers", "tiempo", 40, 20, "⛰️", "Rápido, sin levantar la cadera.", "core_cardio", "alto", "ninguno", "alto", "quema_grasa"),
        nuevo_ejercicio("Mountain climbers cruzados", "tiempo", 40, 20, "❌", "Lleva rodilla al codo contrario.", "core_cardio", "alto", "ninguno", "alto", "quema_grasa"),
        nuevo_ejercicio("Tuck jumps", "reps", 15, 30, "🚀", "Lleva rodillas al pecho al saltar.", "tren_inferior", "alto", "ninguno", "alto", "potencia"),
        nuevo_ejercicio("Sentadilla con salto", "reps", 20, 20, "🦵", "Cae suave y mantén rodillas alineadas.", "tren_inferior", "alto", "ninguno", "alto", "potencia"),
        nuevo_ejercicio("Sentadilla profunda", "reps", 25, 20, "🏋️", "Baja con espalda neutra.", "tren_inferior", "medio", "ninguno", "alto", "fuerza"),
        nuevo_ejercicio("Sentadilla isométrica", "tiempo", 60, 25, "🧱", "Muslos paralelos al suelo.", "tren_inferior", "bajo", "ninguno", "medio", "resistencia"),
        nuevo_ejercicio("Jumping lunges", "reps", 20, 25, "🦿", "Alterna piernas con salto controlado.", "tren_inferior", "alto", "ninguno", "alto", "potencia"),
        nuevo_ejercicio("Zancadas alternas", "reps", 24, 20, "🚶", "Rodilla delantera alineada al pie.", "tren_inferior", "medio", "ninguno", "medio", "fuerza"),
        nuevo_ejercicio("Zancadas atrás", "reps", 20, 20, "↩️", "Paso atrás largo y estable.", "tren_inferior", "medio", "ninguno", "medio", "fuerza"),
        nuevo_ejercicio("Lunge lateral", "reps", 20, 25, "↔️", "Cadera atrás y pecho arriba.", "tren_inferior", "medio", "ninguno", "medio", "fuerza"),
        nuevo_ejercicio("Skater jumps", "tiempo", 40, 20, "⛸️", "Salto lateral amplio y estable.", "tren_inferior", "alto", "ninguno", "alto", "potencia"),
        nuevo_ejercicio("Step-up explosivo", "reps", 20, 20, "📦", "Impulsa con una pierna.", "tren_inferior", "alto", "banco", "alto", "potencia"),
        nuevo_ejercicio("Box jumps", "reps", 12, 30, "📦", "Sube y baja con control.", "tren_inferior", "alto", "caja", "alto", "potencia"),
        nuevo_ejercicio("Pistol squat asistida", "reps", 10, 30, "🎯", "Controla la bajada.", "tren_inferior", "medio", "banco", "alto", "fuerza"),
        nuevo_ejercicio("Wall sit a una pierna", "tiempo", 30, 25, "🧱", "Mantén pelvis estable.", "tren_inferior", "bajo", "pared", "alto", "resistencia"),
        nuevo_ejercicio("Elevación de talones unilaterales", "reps", 20, 20, "🦶", "Sube y baja con control.", "pantorrilla", "bajo", "ninguno", "medio", "fuerza"),
        nuevo_ejercicio("Flexiones", "reps", 20, 20, "💪", "Cuerpo recto, pecho cerca del suelo.", "tren_superior", "medio", "ninguno", "alto", "fuerza"),
        nuevo_ejercicio("Flexiones diamante", "reps", 15, 25, "💎", "Codos cerca al cuerpo.", "tren_superior", "medio", "ninguno", "alto", "fuerza"),
        nuevo_ejercicio("Flexiones declinadas", "reps", 15, 25, "📐", "Pies elevados, abdomen firme.", "tren_superior", "medio", "banco", "alto", "fuerza"),
        nuevo_ejercicio("Flexiones explosivas", "reps", 12, 30, "💥", "Empuja rápido y despega manos si puedes.", "tren_superior", "alto", "ninguno", "alto", "potencia"),
        nuevo_ejercicio("Fondos en banco", "reps", 18, 25, "🪑", "Baja con hombros estables.", "tren_superior", "medio", "banco", "medio", "fuerza"),
        nuevo_ejercicio("Pike push-ups", "reps", 15, 25, "🔺", "Empuja desde hombros.", "tren_superior", "medio", "ninguno", "alto", "fuerza"),
        nuevo_ejercicio("Dominadas", "reps", 10, 35, "🧗", "Controla subida y bajada.", "espalda", "medio", "barra", "alto", "fuerza"),
        nuevo_ejercicio("Chin-ups", "reps", 10, 35, "🧗‍♂️", "Agarre supino y pecho arriba.", "espalda", "medio", "barra", "alto", "fuerza"),
        nuevo_ejercicio("Remo invertido", "reps", 15, 25, "🚣", "Lleva pecho hacia la barra.", "espalda", "medio", "barra", "medio", "fuerza"),
        nuevo_ejercicio("Plancha frontal", "tiempo", 60, 25, "🪵", "No hundas la zona lumbar.", "core", "bajo", "ninguno", "medio", "resistencia"),
        nuevo_ejercicio("Plancha lateral", "tiempo", 40, 20, "↔️", "Cuerpo en línea recta.", "core", "bajo", "ninguno", "medio", "resistencia"),
        nuevo_ejercicio("Plancha con toques de hombro", "reps", 30, 20, "🤚", "Evita balancear la cadera.", "core", "medio", "ninguno", "alto", "estabilidad"),
        nuevo_ejercicio("Plancha con desplazamiento", "tiempo", 30, 25, "➡️", "Camina con antebrazos o manos.", "core", "medio", "ninguno", "alto", "estabilidad"),
        nuevo_ejercicio("Hollow hold", "tiempo", 30, 25, "🥚", "Espalda baja pegada al piso.", "core", "bajo", "ninguno", "alto", "resistencia"),
        nuevo_ejercicio("V-ups", "reps", 20, 20, "🔺", "Sube brazos y piernas al centro.", "core", "medio", "ninguno", "alto", "fuerza"),
        nuevo_ejercicio("Bicicleta abdominal", "reps", 30, 20, "🚴", "Gira el tronco, no solo el cuello.", "core", "medio", "ninguno", "medio", "resistencia"),
        nuevo_ejercicio("Russian twist", "reps", 30, 20, "🌀", "Abdomen firme, pies elevados opcional.", "core", "medio", "ninguno", "medio", "resistencia"),
        nuevo_ejercicio("Toe touches", "reps", 25, 20, "👣", "Sube recto, no jales el cuello.", "core", "bajo", "ninguno", "medio", "resistencia"),
        nuevo_ejercicio("Superman", "reps", 20, 20, "🦸", "Eleva brazos y piernas a la vez.", "cadena_posterior", "bajo", "ninguno", "medio", "estabilidad"),
        nuevo_ejercicio("Bear crawl", "tiempo", 30, 25, "🐻", "Rodillas cerca del suelo.", "full_body", "medio", "ninguno", "alto", "coordinacion"),
        nuevo_ejercicio("Crab walk", "tiempo", 30, 25, "🦀", "Cadera elevada y pasos cortos.", "full_body", "medio", "ninguno", "medio", "coordinacion"),
        nuevo_ejercicio("Battle ropes", "tiempo", 30, 25, "〰️", "Ondas rápidas y constantes.", "full_body", "alto", "cuerda_batalla", "alto", "quema_grasa"),
        nuevo_ejercicio("Thrusters con mancuernas", "reps", 15, 30, "🏋️‍♂️", "Sentadilla más press arriba.", "full_body", "medio", "mancuernas", "alto", "fuerza"),
        nuevo_ejercicio("Peso muerto con mancuernas", "reps", 15, 30, "🪓", "Bisagra de cadera, espalda recta.", "cadena_posterior", "medio", "mancuernas", "alto", "fuerza"),
        nuevo_ejercicio("Peso muerto rumano", "reps", 15, 30, "🪵", "Baja manteniendo espalda neutra.", "cadena_posterior", "medio", "mancuernas", "alto", "fuerza"),
        nuevo_ejercicio("Remo inclinado con mancuernas", "reps", 16, 25, "🚣", "Lleva codos hacia atrás.", "espalda", "medio", "mancuernas", "medio", "fuerza"),
        nuevo_ejercicio("Press militar con mancuernas", "reps", 15, 25, "⬆️", "Empuja sin arquear la espalda.", "tren_superior", "medio", "mancuernas", "medio", "fuerza"),
        nuevo_ejercicio("Push press", "reps", 15, 25, "⬆️", "Usa piernas para asistir el press.", "full_body", "medio", "mancuernas", "alto", "potencia"),
        nuevo_ejercicio("Kettlebell swings", "reps", 20, 30, "🔔", "Impulsa con cadera, no con brazos.", "cadena_posterior", "medio", "kettlebell", "alto", "potencia"),
        nuevo_ejercicio("Goblet squat", "reps", 18, 25, "🏋️", "Sostén el peso cerca al pecho.", "tren_inferior", "medio", "kettlebell", "medio", "fuerza"),
        nuevo_ejercicio("Snatch con mancuerna", "reps", 12, 30, "⚡", "Del suelo arriba en un solo gesto.", "full_body", "alto", "mancuernas", "alto", "potencia"),
        nuevo_ejercicio("Clean and press", "reps", 12, 30, "🔄", "Lleva el peso al hombro y presiona arriba.", "full_body", "medio", "mancuernas", "alto", "fuerza"),
        nuevo_ejercicio("Farmer carry", "tiempo", 45, 25, "🛍️", "Camina erguido con peso.", "full_body", "bajo", "mancuernas", "medio", "resistencia"),
        nuevo_ejercicio("Sled push", "tiempo", 25, 30, "🚜", "Empuja fuerte manteniendo el tronco firme.", "full_body", "alto", "trineo", "alto", "quema_grasa"),
        nuevo_ejercicio("Salto al cajón lateral", "reps", 12, 30, "↔️", "Impulso lateral con recepción estable.", "tren_inferior", "alto", "caja", "alto", "potencia"),
    ],

    "Adulto": [
        nuevo_ejercicio("Marcha en sitio", "tiempo", 60, 20, "🚶", "Brazos activos y ritmo continuo.", "cardio", "bajo", "ninguno", "bajo", "resistencia"),
        nuevo_ejercicio("Caminata rápida en sitio", "tiempo", 90, 25, "👟", "Respira sin detenerte.", "cardio", "bajo", "ninguno", "bajo", "resistencia"),
        nuevo_ejercicio("Step touch lateral", "tiempo", 60, 20, "↔️", "Paso lateral suave y continuo.", "cardio", "bajo", "ninguno", "bajo", "resistencia"),
        nuevo_ejercicio("Jumping jacks bajos", "tiempo", 45, 25, "⭐", "Sin salto, abriendo y cerrando piernas.", "cardio", "bajo", "ninguno", "bajo", "resistencia"),
        nuevo_ejercicio("Rodillas arriba suaves", "tiempo", 40, 25, "🔥", "Impacto moderado y ritmo estable.", "cardio", "medio", "ninguno", "medio", "quema_grasa"),
        nuevo_ejercicio("Talones a glúteos", "tiempo", 40, 25, "🏃", "Movimiento continuo y suave.", "cardio", "medio", "ninguno", "bajo", "resistencia"),
        nuevo_ejercicio("Skater bajo impacto", "tiempo", 45, 25, "⛸️", "Paso lateral amplio sin salto.", "cardio", "bajo", "ninguno", "medio", "quema_grasa"),
        nuevo_ejercicio("Subir escaleras", "tiempo", 60, 30, "🪜", "Mantén ritmo que puedas sostener.", "cardio", "medio", "escaleras", "medio", "quema_grasa"),
        nuevo_ejercicio("Step-ups en escalón", "reps", 16, 25, "📦", "Sube con control, baja lento.", "cardio", "medio", "escalon", "medio", "quema_grasa"),
        nuevo_ejercicio("Caminata con elevación de rodillas", "tiempo", 60, 20, "🚶‍♂️", "Activa abdomen y eleva rodillas.", "cardio", "bajo", "ninguno", "bajo", "resistencia"),
        nuevo_ejercicio("Sentadilla a silla", "reps", 15, 30, "🪑", "Toca la silla y vuelve a subir.", "tren_inferior", "bajo", "silla", "bajo", "fuerza"),
        nuevo_ejercicio("Semi sentadilla", "reps", 18, 25, "🦵", "Baja hasta donde haya control.", "tren_inferior", "bajo", "ninguno", "bajo", "fuerza"),
        nuevo_ejercicio("Sentadilla pared", "tiempo", 45, 30, "🧱", "Mantén 90 grados si toleras.", "tren_inferior", "bajo", "pared", "medio", "resistencia"),
        nuevo_ejercicio("Sentadilla sumo", "reps", 15, 25, "🦿", "Pies abiertos y puntas afuera.", "tren_inferior", "bajo", "ninguno", "medio", "fuerza"),
        nuevo_ejercicio("Desplante atrás asistido", "reps", 12, 30, "↩️", "Apóyate si hace falta.", "tren_inferior", "bajo", "silla", "bajo", "fuerza"),
        nuevo_ejercicio("Desplante alterno", "reps", 14, 30, "🚶", "Paso largo y rodilla estable.", "tren_inferior", "medio", "ninguno", "medio", "fuerza"),
        nuevo_ejercicio("Lunge lateral asistido", "reps", 12, 30, "↔️", "Cadera atrás y apoyo si es necesario.", "tren_inferior", "bajo", "silla", "medio", "movilidad"),
        nuevo_ejercicio("Step-up bajo", "reps", 14, 30, "📦", "Sube con control y baja lento.", "tren_inferior", "bajo", "banco", "medio", "fuerza"),
        nuevo_ejercicio("Elevación de talones", "reps", 20, 20, "🦶", "Sube y baja lentamente.", "pantorrilla", "bajo", "ninguno", "bajo", "fuerza"),
        nuevo_ejercicio("Elevación de talones sentado", "reps", 20, 20, "🪑", "Movimiento corto y controlado.", "pantorrilla", "bajo", "silla", "bajo", "resistencia"),
        nuevo_ejercicio("Puente de glúteos", "reps", 18, 25, "🌉", "Aprieta glúteos arriba.", "cadena_posterior", "bajo", "ninguno", "bajo", "fuerza"),
        nuevo_ejercicio("Puente de glúteos isométrico", "tiempo", 30, 25, "⏸️", "Mantén pelvis elevada.", "cadena_posterior", "bajo", "ninguno", "bajo", "resistencia"),
        nuevo_ejercicio("Puente unilateral asistido", "reps", 10, 25, "🌉", "Mantén pelvis estable.", "cadena_posterior", "bajo", "ninguno", "medio", "fuerza"),
        nuevo_ejercicio("Peso muerto con mochila", "reps", 15, 30, "🎒", "Espalda recta y cada atrás.", "cadena_posterior", "bajo", "mochila", "medio", "fuerza"),
        nuevo_ejercicio("Buenos días sin peso", "reps", 15, 20, "🙇", "Bisagra de cadera con espalda neutra.", "cadena_posterior", "bajo", "ninguno", "bajo", "movilidad"),
        nuevo_ejercicio("Bird-dog", "reps", 16, 20, "🐦", "Extiende brazo y pierna contraria.", "core", "bajo", "ninguno", "bajo", "estabilidad"),
        nuevo_ejercicio("Dead bug", "reps", 16, 20, "🐞", "Espalda baja pegada al piso.", "core", "bajo", "ninguno", "bajo", "estabilidad"),
        nuevo_ejercicio("Plancha apoyando rodillas", "tiempo", 30, 25, "🪵", "Cuerpo alineado desde hombros a rodillas.", "core", "bajo", "ninguno", "bajo", "resistencia"),
        nuevo_ejercicio("Plancha frontal", "tiempo", 40, 25, "📏", "Activa abdomen y glúteos.", "core", "bajo", "ninguno", "medio", "resistencia"),
        nuevo_ejercicio("Plancha lateral con rodillas", "tiempo", 25, 25, "↔️", "No dejes caer la cadera.", "core", "bajo", "ninguno", "bajo", "estabilidad"),
        nuevo_ejercicio("Abdominal crunch", "reps", 18, 20, "🔺", "Sube hombros, no jales el cuello.", "core", "bajo", "ninguno", "bajo", "fuerza"),
        nuevo_ejercicio("Toques de punta alternos", "reps", 20, 20, "👣", "Activa abdomen al subir.", "core", "bajo", "ninguno", "bajo", "resistencia"),
        nuevo_ejercicio("Giros de tronco de pie", "tiempo", 45, 20, "🌀", "Movimiento controlado, sin brusquedad.", "core", "bajo", "ninguno", "bajo", "movilidad"),
        nuevo_ejercicio("Mountain climbers lentos", "tiempo", 30, 30, "⛰️", "Lleva rodillas al pecho con control.", "core_cardio", "medio", "ninguno", "medio", "quema_grasa"),
        nuevo_ejercicio("Flexiones en pared", "reps", 15, 25, "🧍", "Empuja con pecho y tríceps.", "tren_superior", "bajo", "pared", "bajo", "fuerza"),
        nuevo_ejercicio("Flexiones inclinadas", "reps", 12, 30, "📐", "Usa mesa o banco firme.", "tren_superior", "bajo", "banco", "medio", "fuerza"),
        nuevo_ejercicio("Remo con banda", "reps", 15, 25, "🎽", "Junta escápulas al tirar.", "espalda", "bajo", "banda", "medio", "fuerza"),
        nuevo_ejercicio("Press de hombros con banda", "reps", 15, 25, "⬆️", "Empuja sin elevar hombros.", "tren_superior", "bajo", "banda", "medio", "fuerza"),
        nuevo_ejercicio("Curl de bíceps con banda", "reps", 15, 20, "💪", "Codos pegados al cuerpo.", "tren_superior", "bajo", "banda", "bajo", "fuerza"),
        nuevo_ejercicio("Extensión de tríceps con banda", "reps", 15, 20, "🔁", "Estira completo sin impulso.", "tren_superior", "bajo", "banda", "bajo", "fuerza"),
        nuevo_ejercicio("Press pecho con banda", "reps", 15, 25, "🫷", "Empuja al frente controlando el retorno.", "tren_superior", "bajo", "banda", "medio", "fuerza"),
        nuevo_ejercicio("Face pull con banda", "reps", 15, 20, "🎯", "Lleva banda hacia la cara con codos altos.", "espalda", "bajo", "banda", "medio", "postura"),
        nuevo_ejercicio("Caminata lateral con banda", "reps", 20, 25, "➡️", "Pasos cortos con tensión constante.", "cadera_gluteos", "bajo", "banda", "medio", "fuerza"),
        nuevo_ejercicio("Monster walks", "reps", 20, 25, "👣", "Camina en diagonal manteniendo tensión.", "cadera_gluteos", "bajo", "banda", "medio", "fuerza"),
        nuevo_ejercicio("Abducción de cadera de pie", "reps", 15, 20, "🦵", "Eleva la pierna lateralmente sin inclinarte.", "cadera_gluteos", "bajo", "ninguno", "bajo", "fuerza"),
        nuevo_ejercicio("Extensión de cadera de pie", "reps", 15, 20, "⬅️", "Lleva pierna atrás sin arquear espalda.", "cadera_gluteos", "bajo", "ninguno", "bajo", "fuerza"),
        nuevo_ejercicio("Sentarse y pararse rápido", "tiempo", 30, 25, "🪑", "Mantén técnica y ritmo continuo.", "full_body", "medio", "silla", "medio", "quema_grasa"),
        nuevo_ejercicio("Farmer carry con peso", "tiempo", 40, 30, "🛍️", "Camina erguido y firme.", "full_body", "bajo", "mancuernas", "medio", "resistencia"),
        nuevo_ejercicio("Golpes al frente", "tiempo", 45, 20, "🥊", "Activa abdomen y mantén ritmo.", "full_body", "bajo", "ninguno", "bajo", "quema_grasa"),
        nuevo_ejercicio("Golpes con giro suave", "tiempo", 45, 20, "🥊", "Rota el tronco sin brusquedad.", "full_body", "bajo", "ninguno", "bajo", "resistencia"),
        nuevo_ejercicio("Remo con mochila", "reps", 15, 25, "🎒", "Tira hacia el ombligo con espalda recta.", "espalda", "bajo", "mochila", "medio", "fuerza"),
        nuevo_ejercicio("Press militar con botellas", "reps", 15, 25, "🧴", "Empuja arriba sin arquear la espalda.", "tren_superior", "bajo", "botellas", "bajo", "fuerza"),
        nuevo_ejercicio("Sentadilla con mochila", "reps", 15, 25, "🎒", "Peso cerca al pecho y tronco erguido.", "tren_inferior", "bajo", "mochila", "medio", "fuerza"),
        nuevo_ejercicio("Peso muerto con botellas", "reps", 15, 25, "🧴", "Bisagra de cadera lenta y controlada.", "cadena_posterior", "bajo", "botellas", "bajo", "fuerza"),
        nuevo_ejercicio("Paso cruzado lateral", "tiempo", 45, 20, "🔀", "Cruza un pie delante y luego detrás.", "coordinacion", "bajo", "ninguno", "bajo", "coordinacion"),
        nuevo_ejercicio("Equilibrio en un pie", "tiempo", 25, 15, "🎯", "Cambia de pierna después.", "equilibrio", "bajo", "ninguno", "bajo", "equilibrio"),
        nuevo_ejercicio("Equilibrio punta-talón", "tiempo", 30, 15, "🚶", "Camina en línea recta.", "equilibrio", "bajo", "ninguno", "bajo", "equilibrio"),
        nuevo_ejercicio("Alcance frontal en equilibrio", "reps", 12, 15, "🤲", "Mantén una pierna mientras alcanzas al frente.", "equilibrio", "bajo", "ninguno", "medio", "estabilidad"),
    ],

    "Junior": [
        nuevo_ejercicio("Salto cuerda", "tiempo", 60, 20, "➰", "Cae en puntas de pies.", "cardio_coordinacion", "medio", "cuerda", "medio", "coordinacion"),
        nuevo_ejercicio("Jumping jacks", "tiempo", 40, 20, "⭐", "Abre brazos y piernas con ritmo.", "cardio", "medio", "ninguno", "bajo", "resistencia"),
        nuevo_ejercicio("Saltos en línea", "tiempo", 30, 20, "📏", "Salta adelante y atrás sin perder equilibrio.", "coordinacion", "medio", "ninguno", "bajo", "coordinacion"),
        nuevo_ejercicio("Saltos laterales", "tiempo", 30, 20, "↔️", "Pies juntos y caída suave.", "coordinacion", "medio", "ninguno", "bajo", "coordinacion"),
        nuevo_ejercicio("Saltos estrella", "reps", 15, 20, "🌟", "Abre todo el cuerpo al saltar.", "coordinacion", "medio", "ninguno", "bajo", "coordinacion"),
        nuevo_ejercicio("Rodillas arriba", "tiempo", 30, 20, "🔥", "Sube rodillas y mueve brazos.", "cardio", "medio", "ninguno", "bajo", "resistencia"),
        nuevo_ejercicio("Talones a glúteos", "tiempo", 30, 20, "🏃", "Corre en sitio tocando glúteos.", "cardio", "medio", "ninguno", "bajo", "resistencia"),
        nuevo_ejercicio("Marcha rápida", "tiempo", 60, 20, "🚶", "Postura recta y respiración continua.", "cardio", "bajo", "ninguno", "bajo", "resistencia"),
        nuevo_ejercicio("Skipping", "tiempo", 40, 20, "🎽", "Paso dinámico elevando rodilla.", "cardio", "medio", "ninguno", "medio", "resistencia"),
        nuevo_ejercicio("Carrera en zigzag", "tiempo", 30, 25, "⚡", "Cambios de dirección cortos y rápidos.", "cardio", "medio", "conos", "medio", "agilidad"),
        nuevo_ejercicio("Carrera lateral", "tiempo", 30, 20, "➡️", "Muévete de lado sin cruzar pies al inicio.", "cardio", "medio", "ninguno", "bajo", "agilidad"),
        nuevo_ejercicio("Saltar en un pie", "tiempo", 20, 20, "🦶", "Cambia de pierna al terminar.", "equilibrio", "medio", "ninguno", "bajo", "equilibrio"),
        nuevo_ejercicio("Tijeras de piernas", "tiempo", 30, 20, "✂️", "Alterna piernas al frente y atrás.", "coordinacion", "medio", "ninguno", "bajo", "coordinacion"),
        nuevo_ejercicio("Paso del oso rápido", "tiempo", 20, 20, "🐻", "Avanza con manos y pies coordinados.", "full_body", "medio", "ninguno", "medio", "coordinacion"),
        nuevo_ejercicio("Sentadillas", "reps", 15, 20, "🦵", "Baja con control y pecho arriba.", "tren_inferior", "bajo", "ninguno", "bajo", "fuerza"),
        nuevo_ejercicio("Sentadilla con brazos al frente", "reps", 15, 20, "🤲", "Mantén equilibrio y espalda recta.", "tren_inferior", "bajo", "ninguno", "bajo", "fuerza"),
        nuevo_ejercicio("Sentadilla sumo", "reps", 15, 20, "🦿", "Pies abiertos y rodillas alineadas.", "tren_inferior", "bajo", "ninguno", "bajo", "fuerza"),
        nuevo_ejercicio("Desplantes alternos", "reps", 12, 25, "🚶", "Paso largo y estable.", "tren_inferior", "bajo", "ninguno", "bajo", "fuerza"),
        nuevo_ejercicio("Desplante atrás", "reps", 12, 25, "↩️", "Regresa al centro con control.", "tren_inferior", "bajo", "ninguno", "bajo", "fuerza"),
        nuevo_ejercicio("Subir y bajar escalón", "reps", 20, 20, "📦", "Usa un escalón seguro.", "tren_inferior", "bajo", "escalon", "bajo", "resistencia"),
        nuevo_ejercicio("Elevación de talones", "reps", 20, 15, "🦶", "Sube en puntas y baja lento.", "pantorrilla", "bajo", "ninguno", "bajo", "fuerza"),
        nuevo_ejercicio("Saltos cortos en puntas", "tiempo", 20, 20, "🪶", "Salta suave con tobillos activos.", "pantorrilla", "medio", "ninguno", "bajo", "potencia"),
        nuevo_ejercicio("Puente de glúteos", "reps", 15, 20, "🌉", "Eleva cadera y aprieta glúteos.", "cadena_posterior", "bajo", "ninguno", "bajo", "fuerza"),
        nuevo_ejercicio("Puente con una pierna alterna", "reps", 10, 20, "🌉", "Mantén cadera estable al subir.", "cadena_posterior", "bajo", "ninguno", "medio", "fuerza"),
        nuevo_ejercicio("Buenos días sin peso", "reps", 12, 15, "🙇", "Dobla cadera con espalda neutra.", "cadena_posterior", "bajo", "ninguno", "bajo", "movilidad"),
        nuevo_ejercicio("Flexiones en pared", "reps", 12, 20, "🧍", "Empuja firme y controlado.", "tren_superior", "bajo", "pared", "bajo", "fuerza"),
        nuevo_ejercicio("Flexiones inclinadas", "reps", 10, 25, "📐", "Usa una superficie estable.", "tren_superior", "bajo", "banco", "bajo", "fuerza"),
        nuevo_ejercicio("Fondos en banco asistidos", "reps", 10, 25, "🪑", "Flexiona codos con control.", "tren_superior", "bajo", "banco", "medio", "fuerza"),
        nuevo_ejercicio("Remo con banda", "reps", 12, 20, "🎽", "Lleva codos atrás y junta espalda.", "espalda", "bajo", "banda", "bajo", "fuerza"),
        nuevo_ejercicio("Press con banda", "reps", 12, 20, "⬆️", "Empuja al frente o arriba con control.", "tren_superior", "bajo", "banda", "bajo", "fuerza"),
        nuevo_ejercicio("Lanzar y atrapar balón", "tiempo", 45, 15, "🏀", "Coordina ojos y manos.", "coordinacion", "bajo", "balon", "bajo", "coordinacion"),
        nuevo_ejercicio("Pase de balón contra pared", "tiempo", 45, 15, "🏐", "Lanza y recibe sin perder postura.", "coordinacion", "bajo", "balon", "bajo", "coordinacion"),
        nuevo_ejercicio("Plancha corta", "tiempo", 20, 20, "🪵", "Abdomen firme y espalda recta.", "core", "bajo", "ninguno", "bajo", "estabilidad"),
        nuevo_ejercicio("Plancha con rodillas", "tiempo", 25, 20, "📏", "No dejes caer la cadera.", "core", "bajo", "ninguno", "bajo", "estabilidad"),
        nuevo_ejercicio("Bird-dog", "reps", 12, 20, "🐦", "Brazo y pierna contraria al mismo tiempo.", "core", "bajo", "ninguno", "bajo", "estabilidad"),
        nuevo_ejercicio("Dead bug", "reps", 12, 20, "🐞", "Movimiento lento y coordinado.", "core", "bajo", "ninguno", "bajo", "estabilidad"),
        nuevo_ejercicio("Abdominales cortos", "reps", 15, 20, "🔺", "No tires del cuello.", "core", "bajo", "ninguno", "bajo", "fuerza"),
        nuevo_ejercicio("Toques de punta", "reps", 16, 20, "👣", "Sube con el abdomen.", "core", "bajo", "ninguno", "bajo", "resistencia"),
        nuevo_ejercicio("Escalador lento", "tiempo", 20, 20, "⛰️", "Lleva rodillas al pecho sin apuro.", "core_cardio", "bajo", "ninguno", "bajo", "resistencia"),
        nuevo_ejercicio("Bear crawl", "tiempo", 20, 25, "🐻", "Camina con manos y pies.", "full_body", "medio", "ninguno", "medio", "coordinacion"),
        nuevo_ejercicio("Crab walk", "tiempo", 20, 25, "🦀", "Cadera arriba y mirada al frente.", "full_body", "medio", "ninguno", "medio", "coordinacion"),
        nuevo_ejercicio("Caminar como rana", "tiempo", 20, 25, "🐸", "Mantén posición baja.", "full_body", "medio", "ninguno", "bajo", "coordinacion"),
        nuevo_ejercicio("Caminar como oso", "tiempo", 20, 25, "🐾", "Pasos cortos y controlados.", "full_body", "medio", "ninguno", "bajo", "coordinacion"),
        nuevo_ejercicio("Caminar como cangrejo lateral", "tiempo", 20, 25, "🦀", "Desplázate de lado con control.", "full_body", "medio", "ninguno", "bajo", "coordinacion"),
        nuevo_ejercicio("Mini burpees", "reps", 10, 25, "🤸", "Versión sin flexión completa.", "full_body", "medio", "ninguno", "medio", "quema_grasa"),
        nuevo_ejercicio("Burpee paso a paso", "reps", 8, 20, "🤸‍♀️", "Sin salto atrás, con control.", "full_body", "bajo", "ninguno", "bajo", "resistencia"),
        nuevo_ejercicio("Equilibrio en un pie", "tiempo", 20, 15, "🎯", "Cambia de pierna después.", "equilibrio", "bajo", "ninguno", "bajo", "equilibrio"),
        nuevo_ejercicio("Equilibrio punta-talón", "tiempo", 30, 15, "🚶‍♂️", "Camina en línea recta.", "equilibrio", "bajo", "ninguno", "bajo", "equilibrio"),
        nuevo_ejercicio("Equilibrio con ojos al frente", "tiempo", 20, 15, "👀", "Mantén un punto fijo.", "equilibrio", "bajo", "ninguno", "bajo", "equilibrio"),
        nuevo_ejercicio("Salto dentro-fuera", "tiempo", 25, 20, "🟦", "Entra y sale de una línea o cuadro.", "coordinacion", "medio", "ninguno", "bajo", "coordinacion"),
        nuevo_ejercicio("Paso cruzado", "tiempo", 30, 20, "🔀", "Cruza un pie delante y luego detrás.", "coordinacion", "bajo", "ninguno", "bajo", "coordinacion"),
        nuevo_ejercicio("Escalera de agilidad", "tiempo", 30, 20, "🪜", "Pisa rápido y con precisión.", "coordinacion", "medio", "escalera_agilidad", "medio", "agilidad"),
        nuevo_ejercicio("Saltos por cuadros", "tiempo", 25, 20, "🔲", "Salta siguiendo una secuencia.", "coordinacion", "medio", "cuadros", "bajo", "coordinacion"),
        nuevo_ejercicio("Reacción por palmadas", "tiempo", 30, 15, "👏", "Cambia de movimiento al oír señal.", "coordinacion", "bajo", "ninguno", "bajo", "reaccion"),
        nuevo_ejercicio("Lateral shuffle", "tiempo", 25, 20, "↔️", "Desplázate lateralmente rápido.", "cardio", "medio", "ninguno", "medio", "agilidad"),
        nuevo_ejercicio("Skipping con cuerda imaginaria", "tiempo", 30, 20, "🪢", "Simula cuerda y mantén ritmo.", "cardio", "bajo", "ninguno", "bajo", "resistencia"),
        nuevo_ejercicio("Sentadilla con salto suave", "reps", 10, 25, "🦘", "Salto pequeño y recepción estable.", "tren_inferior", "medio", "ninguno", "medio", "potencia"),
        nuevo_ejercicio("Hops adelante-atrás", "tiempo", 20, 20, "↕️", "Pequeños saltos rápidos en una línea.", "coordinacion", "medio", "ninguno", "bajo", "agilidad"),
    ],
}

GRUPOS_COMPATIBLES = {
    "cardio": ["core", "tren_superior", "equilibrio"],
    "cardio_fuerza": ["core", "equilibrio"],
    "core": ["cardio", "tren_inferior", "tren_superior", "equilibrio"],
    "core_cardio": ["tren_superior", "equilibrio"],
    "tren_inferior": ["core", "tren_superior", "equilibrio"],
    "tren_superior": ["cardio", "core", "tren_inferior", "equilibrio"],
    "espalda": ["cardio", "core", "tren_inferior", "equilibrio"],
    "pantorrilla": ["core", "tren_superior", "equilibrio"],
    "cadena_posterior": ["cardio", "core", "tren_superior"],
    "cadera_gluteos": ["cardio", "core", "tren_superior"],
    "full_body": ["equilibrio", "core"],
    "equilibrio": ["cardio", "core", "tren_superior", "tren_inferior"],
    "coordinacion": ["core", "tren_superior", "equilibrio"],
    "cardio_coordinacion": ["core", "equilibrio"],
}

# --- 4. LÓGICA DE SELECCIÓN INTELIGENTE ---
def es_compatible(ejercicio, ultimo):
    if ultimo is None: return True
    if ejercicio["grupo"] == ultimo["grupo"] and ejercicio["impacto"] == ultimo["impacto"]: return False
    compatibles = GRUPOS_COMPATIBLES.get(ultimo["grupo"])
    if compatibles is None: return ejercicio["grupo"] != ultimo["grupo"]
    return ejercicio["grupo"] in compatibles

def seleccionar_rutina_inteligente(categoria, cantidad=6):
    candidatos = banco_ejercicios.get(categoria, []).copy()
    random.shuffle(candidatos)
    seleccion = []
    intentos = 0
    while candidatos and len(seleccion) < cantidad and intentos < 100:
        agregado = False
        for i, ej in enumerate(candidatos):
            if es_compatible(ej, seleccion[-1] if seleccion else None):
                seleccion.append(candidatos.pop(i))
                agregado = True
                break
        if not agregado:
            seleccion.append(candidatos.pop(0))
        intentos += 1
    return seleccion

# --- 5. SESIÓN Y DATOS ---
for key in ['ejercicio_actual', 'entrenando', 'fase', 'rutina_dia', 'f_descanso']:
    if key not in st.session_state:
        if key == 'fase': st.session_state[key] = "Calentamiento"
        elif key == 'entrenando': st.session_state[key] = False
        else: st.session_state[key] = 0

conn = st.connection("gsheets", type=GSheetsConnection)
df_total = conn.read(ttl=0)

st.title("🏆 Family Fitness ULTRA v12")

# --- RANKING FAMILIAR IMC ---
with st.expander("📊 Ranking Familiar IMC", expanded=False):
    if not df_total.empty:
        df_ultimos = df_total.sort_values('Fecha').groupby('Usuario').last().reset_index()
        def calc_imc(row): return round(row['Peso'] / (perfiles[row['Usuario']]['estatura']**2), 1)
        df_ultimos['IMC'] = df_ultimos.apply(calc_imc, axis=1)
        c_g1, c_g2 = st.columns(2)
        c_g1.write("**Peso Actual (kg)**"); c_g1.bar_chart(df_ultimos, x="Usuario", y="Peso")
        c_g2.write("**IMC Actual (Saludable 18.5 - 24.9)**"); c_g2.bar_chart(df_ultimos, x="Usuario", y="IMC")

# --- PERFIL ---
usuario = st.selectbox("👤 ¿Quién eres?", ["Seleccionar..."] + list(perfiles.keys()))

if usuario != "Seleccionar...":
    datos_p = perfiles[usuario]
    df_u = df_total[df_total['Usuario'] == usuario].copy() if not df_total.empty else pd.DataFrame()
    u_peso = df_u['Peso'].iloc[-1] if not df_u.empty else 0.0
    imc_act = round(u_peso / (datos_p['estatura']**2), 1) if u_peso > 0 else 0.0
    p_meta = round(22 * (datos_p['estatura']**2), 1)

    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("⚖️ PESO", f"{u_peso} kg")
    m2.metric("📊 IMC", f"{imc_act}", delta_color="normal" if 18.5 <= imc_act <= 24.9 else "inverse")
    m3.metric("🎯 META (IMC 22)", f"{p_meta} kg", f"{round(u_peso - p_meta, 1)} kg de diferencia")

    st.divider()
    opcion = st.sidebar.radio("Menú:", ["📈 Registro e Historial", "💪 Entrenamiento IA Pro"])

    if opcion == "📈 Registro e Historial":
        col_reg, col_gra = st.columns([1, 1.5])
        with col_reg:
            st.subheader("📝 Pesaje Dominical")
            n_peso = st.number_input("Peso (kg):", value=float(u_peso), step=0.1)
            fecha = st.date_input("Fecha:", datetime.now())
            if st.button("💾 GUARDAR", type="primary", use_container_width=True):
                nueva = pd.DataFrame({"Usuario":[usuario], "Fecha":[fecha.strftime('%Y-%m-%d')], "Peso":[n_peso], "Calorias":[0], "Proteinas":[0], "Detalle":["Pesaje"], "Vasos_Agua":[0]})
                conn.update(data=pd.concat([df_total, nueva], ignore_index=True))
                st.success("¡Registrado!"); time.sleep(1); st.rerun()
        with col_gra:
            if not df_u.empty:
                df_u['Fecha'] = pd.to_datetime(df_u['Fecha'])
                st.line_chart(df_u.sort_values('Fecha'), x="Fecha", y="Peso")

    elif opcion == "💪 Entrenamiento IA Pro":
        st.header(f"Plan para {usuario} ({datos_p['nivel']})")
        with st.container(border=True):
            col_s1, col_s2 = st.columns(2)
            sueño = col_s1.select_slider("😴 Sueño", options=range(1,11), value=8)
            dolor = col_s2.select_slider("🤕 Dolor", options=range(0,11), value=2)
            factor = 2 if (sueño < 6 or dolor > 7) else 1

        if not st.session_state.entrenando:
            if st.button("🚀 GENERAR RUTINA INTELIGENTE", use_container_width=True, type="primary"):
                random.seed(usuario + datetime.now().strftime('%Y-%m-%d'))
                st.session_state.rutina_dia = seleccionar_rutina_inteligente(datos_p["nivel"], 6)
                st.session_state.entrenando = True
                st.session_state.fase = "Calentamiento"
                st.session_state.ejercicio_actual = 0
                st.session_state.f_descanso = factor
                st.rerun()
        else:
            if st.session_state.fase == "Calentamiento":
                st.subheader("🔥 Fase 1: Calentamiento"); st.write("Movilidad articular y activación (5 min).")
                if st.button("✅ ¡Listo! Empezar"): st.session_state.fase = "Circuito"; st.rerun()
            elif st.session_state.fase == "Circuito":
                prog = (st.session_state.ejercicio_actual + 1) / len(st.session_state.rutina_dia)
                st.progress(prog)
                ej = st.session_state.rutina_dia[st.session_state.ejercicio_actual]
                st.markdown(f"## {ej['icon']} {ej['n']}")
                st.info(f"Técnica: {ej['guia']} | Grupo: {ej['grupo']}")
                if ej['t'] == 'reps':
                    st.write(f"🔢 Objetivo: **{ej['v']} reps**")
                    if st.button("✅ SIGUIENTE"):
                        with st.empty():
                            for s in range(ej['d']*st.session_state.f_descanso, 0, -1):
                                st.warning(f"⏳ Descanso: {s}s"); time.sleep(1)
                        st.session_state.ejercicio_actual += 1
                        if st.session_state.ejercicio_actual >= len(st.session_state.rutina_dia): st.session_state.fase = "Estiramiento"
                        st.rerun()
                else:
                    st.write(f"⏱️ Tiempo: **{ej['v']} seg**")
                    if st.button("▶️ START"):
                        with st.empty():
                            for s in range(ej['v'], 0, -1): st.error(f"🔥 {s}s"); time.sleep(1)
                        st.session_state.ejercicio_actual += 1
                        if st.session_state.ejercicio_actual >= len(st.session_state.rutina_dia): st.session_state.fase = "Estiramiento"
                        st.rerun()
            elif st.session_state.fase == "Estiramiento":
                st.success("🧘 ¡Felicidades! Rutina terminada."); st.balloons()
                if st.button("🏆 FINALIZAR"): st.session_state.entrenando = False; st.rerun()
