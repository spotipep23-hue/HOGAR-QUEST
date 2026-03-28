import streamlit as st
import pandas as pd
import datetime
import requests

st.set_page_config(layout="centered", page_title="Hogar Quest Cloud", page_icon="⚔️")

# --- CONFIGURACIÓN ---
# 1. Tu URL de Google Sheets para LEER
URL_LECTURA = "https://docs.google.com/spreadsheets/d/1g90SMibEDEW4_d4d1C2R08SzMfP6KboMtEo-XuDUi1s/edit?usp=sharing" 
# 2. La URL del Script que acabas de copiar para ESCRIBIR
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbxIsargp4yKpKomsxPvm12346hDEOQd_foda9tAaD30h2qMvp7JT4DH9Ynor4_Q9KcW/exec"

@st.cache_data
def cargar_maestro():
    df = pd.read_csv("tareas.xlsx - Hoja1.csv")
    df['ÁMBITO'] = df['ÁMBITO'].ffill()
    df['PUNTOS'] = pd.to_numeric(df['PUNTOS'], errors='coerce').fillna(5).astype(int)
    return df

df_maestro = cargar_maestro()

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
                col_p.write(f"**{row['PUNTOS']} XP**")
                if col_b.button("✅", key=f"btn_{idx}"):
                    # ENVIAR DATOS AL SCRIPT
                    params = {
                        "Fecha": datetime.datetime.now().strftime("%Y-%m-%d"),
                        "Semana": datetime.datetime.now().isocalendar()[1],
                        "Mes": datetime.datetime.now().strftime("%Y-%m"),
                        "Ambito": ambito,
                        "Tarea": row['TAREA'],
                        "Puntos": row['PUNTOS'],
                        "Usuario": usuario
                    }
                    response = requests.get(URL_SCRIPT, params=params)
                    if response.status_code == 200:
                        st.success(f"¡Puntos guardados para {usuario}!")
                        st.balloons()
                    else:
                        st.error("Error al conectar con la nube.")

with tab2:
    # LEER DATOS PARA LAS GRÁFICAS
    csv_url = URL_LECTURA.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit#gid=', '/export?format=csv&gid=')
    try:
        df_h = pd.read_csv(csv_url)
        if not df_h.empty:
            st.subheader("🏆 Marcador Global")
            st.table(df_h.groupby("Usuario")["Puntos"].sum())
            
            st.subheader("📈 Progreso Semanal")
            grafico = df_h.groupby(["Semana", "Usuario"])["Puntos"].sum().unstack().fillna(0)
            st.bar_chart(grafico)
        else:
            st.info("Aún no hay datos.")
    except:
        st.write("Esperando datos...")
