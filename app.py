import streamlit as st
import pandas as pd
import datetime
import requests

st.set_page_config(layout="centered", page_title="Hogar Quest", page_icon="⚔️")

# --- 1. CONFIGURACIÓN ---
URL_GSHEET = "https://docs.google.com/spreadsheets/d/1g90SMibEDEW4_d4d1C2R08SzMfP6KboMtEo-XuDUi1s/edit?usp=sharing"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbxIsargp4yKpKomsxPvm12346hDEOQd_foda9tAaD30h2qMvp7JT4DH9Ynor4_Q9KcW/exec"

# --- 2. FUNCIONES DE CARGA (Con caché para ir rápido) ---
@st.cache_data(ttl=60) # Solo actualiza los datos de la nube cada 60 segundos
def cargar_datos_nube(url):
    csv_url = url.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit#gid=', '/export?format=csv&gid=')
    try:
        return pd.read_csv(csv_url)
    except:
        return pd.DataFrame()

@st.cache_data
def cargar_maestro():
    df = pd.read_csv("tareas.xlsx - Hoja1.csv")
    df['ÁMBITO'] = df['ÁMBITO'].ffill()
    df['PUNTOS'] = pd.to_numeric(df['PUNTOS'], errors='coerce').fillna(5).astype(int)
    return df

# --- 3. LÓGICA DE DATOS ---
df_h = cargar_datos_nube(URL_GSHEET)
df_maestro = cargar_maestro()
hoy = datetime.datetime.now().strftime("%Y-%m-%d")

# --- 4. INTERFAZ ---
st.title("⚔️ HOGAR QUEST")

# Marcador superior (Calculado localmente para que no pete)
if not df_h.empty and 'Fecha' in df_h.columns:
    df_hoy = df_h[df_h['Fecha'] == hoy]
    p1 = df_hoy[df_hoy['Usuario'] == "Sandra"]['Puntos'].sum()
    p2 = df_hoy[df_hoy['Usuario'] == "Juan"]['Puntos'].sum()
    
    c1, c2 = st.columns(2)
    c1.metric("Sandra (Hoy)", f"{p1} XP")
    c2.metric("Juan (Hoy)", f"{p2} XP")
else:
    st.info("🎯 ¡Marcador a 0! Completa una tarea para empezar el día.")

st.divider()
user = st.radio("¿Quién eres?", ["Sandra", "Juan"], horizontal=True)

t1, t2 = st.tabs(["🎮 Misiones", "📊 Ranking"])

with t1:
    for ambito in df_maestro['ÁMBITO'].unique():
        with st.expander(f"📍 {ambito}"):
            tareas = df_maestro[df_maestro['ÁMBITO'] == ambito]
            for idx, row in tareas.iterrows():
                col_t, col_p, col_b = st.columns([3, 1, 1])
                col_t.write(row['TAREA'])
                col_p.write(f"{row['PUNTOS']} XP")
                
                if col_b.button("✅", key=f"btn_{idx}"):
                    params = {
                        "Fecha": hoy,
                        "Semana": datetime.datetime.now().isocalendar()[1],
                        "Mes": datetime.datetime.now().strftime("%Y-%m"),
                        "Ambito": ambito, "Tarea": row['TAREA'], "Puntos": row['PUNTOS'], "Usuario": user
                    }
                    # Enviamos el punto
                    requests.get(URL_SCRIPT, params=params)
                    st.success(f"¡Guardado!")
                    # Limpiamos caché para que al recargar lea el nuevo punto
                    st.cache_data.clear()
                    st.rerun()

with t2:
    if not df_h.empty:
        st.subheader("🏆 Global")
        st.table(df_h.groupby("Usuario")["Puntos"].sum())
        st.subheader("📈 Semanal")
        st.bar_chart(df_h.groupby(["Semana", "Usuario"])["Puntos"].sum().unstack().fillna(0))
