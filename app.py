import streamlit as st
import pandas as pd
import datetime
import requests

st.set_page_config(layout="centered", page_title="Hogar Quest Cloud", page_icon="⚔️")

# --- 1. CONFIGURACIÓN (RELLENA ESTO CON TUS URLS) ---
URL_GSHEET = "https://docs.google.com/spreadsheets/d/1g90SMibEDEW4_d4d1C2R08SzMfP6KboMtEo-XuDUi1s/edit?usp=sharing"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbxIsargp4yKpKomsxPvm12346hDEOQd_foda9tAaD30h2qMvp7JT4DH9Ynor4_Q9KcW/exec"

# --- 2. CARGAR TAREAS DEL CSV LOCAL ---
@st.cache_data
def cargar_maestro():
    df = pd.read_csv("tareas.xlsx - Hoja1.csv")
    df['ÁMBITO'] = df['ÁMBITO'].ffill()
    df['PUNTOS'] = pd.to_numeric(df['PUNTOS'], errors='coerce').fillna(5).astype(int)
    return df

df_maestro = cargar_maestro()

# --- 3. INTERFAZ PRINCIPAL ---
st.title("⚔️ HOGAR QUEST")

# Marcador de XP de Hoy (Lectura en tiempo real)
try:
    csv_url = URL_GSHEET.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit#gid=', '/export?format=csv&gid=')
    df_h = pd.read_csv(csv_url)
    hoy = datetime.datetime.now().strftime("%Y-%m-%d")
    df_hoy = df_h[df_h['Fecha'] == hoy]
    
    puntos_j1 = df_hoy[df_hoy['Usuario'] == "Sandra"]['Puntos'].sum()
    puntos_j2 = df_hoy[df_hoy['Usuario'] == "Juan"]['Puntos'].sum()

    c1, c2 = st.columns(2)
    c1.metric("Sandra (Hoy)", f"{puntos_j1} XP")
    c2.metric("Juan (Hoy)", f"{puntos_j2} XP")
except:
    st.info("¡A por la primera misión del día!")

st.divider()

# Selector de usuario
usuario = st.radio("¿Quién eres?", ["Sandra", "Juan"], horizontal=True)

# Pestañas
tab1, tab2 = st.tabs(["🎮 Misiones", "📊 Ranking y Datos"])

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
                    # Enviar datos al Script de Google
                    params = {
                        "Fecha": datetime.datetime.now().strftime("%Y-%m-%d"),
                        "Semana": datetime.datetime.now().isocalendar()[1],
                        "Mes": datetime.datetime.now().strftime("%Y-%m"),
                        "Ambito": ambito,
                        "Tarea": row['TAREA'],
                        "Puntos": row['PUNTOS'],
                        "Usuario": usuario
                    }
                    res = requests.get(URL_SCRIPT, params=params)
                    if res.status_code == 200:
                        st.success(f"¡{row['PUNTOS']} XP para {usuario}!")
                        st.balloons()
                        # Esto recarga la app para que el marcador de arriba se actualice
                        st.rerun()

with tab2:
    try:
        if not df_h.empty:
            st.subheader("🏆 Marcador Histórico")
            st.table(df_h.groupby("Usuario")["Puntos"].sum())
            
            st.subheader("📈 Progreso Semanal")
            grafico = df_h.groupby(["Semana", "Usuario"])["Puntos"].sum().unstack().fillna(0)
            st.bar_chart(grafico)
            
            with st.expander("Ver lista completa de tareas"):
                st.dataframe(df_h.sort_values(by="Fecha", ascending=False))
    except:
        st.write("Aún no hay datos guardados.")
