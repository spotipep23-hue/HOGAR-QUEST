import streamlit as st
import pandas as pd
import datetime
import requests

st.set_page_config(layout="centered", page_title="Hogar Quest Cloud", page_icon="☁️")

# --- CONFIGURACIÓN ---
# Tu URL de Google Sheets (la misma de antes)
URL_GSHEET = "https://docs.google.com/spreadsheets/d/1g90SMibEDEW4_d4d1C2R08SzMfP6KboMtEo-XuDUi1s/edit?usp=sharing"

# --- CARGAR TAREAS LOCALES (Tu CSV) ---
@st.cache_data
def cargar_maestro():
    df = pd.read_csv("tareas.xlsx - Hoja1.csv")
    df['ÁMBITO'] = df['ÁMBITO'].ffill()
    df['PUNTOS'] = pd.to_numeric(df['PUNTOS'], errors='coerce').fillna(5).astype(int)
    return df

df_maestro = cargar_maestro()

# --- FUNCIÓN PARA LEER DATOS ---
def leer_datos():
    # Convertimos la URL de "edit" a "export" para leerla como CSV fácilmente
    csv_url = URL_GSHEET.replace('/edit?usp=sharing', '/export?format=csv')
    csv_url = csv_url.replace('/edit#gid=', '/export?format=csv&gid=')
    try:
        return pd.read_csv(csv_url)
    except:
        return pd.DataFrame(columns=["Fecha", "Semana", "Mes", "Ámbito", "Tarea", "Puntos", "Usuario"])

# --- INTERFAZ ---
st.title("⚔️ HOGAR QUEST COMPARTIDO")

usuario = st.radio("¿Quién eres?", ["Sandra", "Juan"], horizontal=True)

tab1, tab2 = st.tabs(["🎮 Misiones", "📊 Ranking"])

with tab1:
    ambitos = df_maestro['ÁMBITO'].unique()
    for ambito in ambitos:
        with st.expander(f"📍 {ambito}"):
            tareas_ambito = df_maestro[df_maestro['ÁMBITO'] == ambito]
            for idx, row in tareas_ambito.iterrows():
                col_t, col_p, col_b = st.columns([3, 1, 1])
                col_t.write(row['TAREA'])
                col_p.write(f"{row['PUNTOS']} XP")
                
                if col_b.button("✅", key=f"btn_{idx}"):
                    st.warning("⚠️ Para escribir en Google Sheets de forma gratuita y fácil, necesitamos usar un pequeño 'Script'.")
                    st.info("¿Prefieres que lo dejemos guardando solo en el dispositivo (sin compartir) o te ayudo con el último paso de Google?")
                    
                    # Como el error es persistente con esa librería, 
                    # te propongo un cambio de estrategia si esto se complica:
                    # ¿Quieres que la app simplemente guarde los datos en el navegador?
