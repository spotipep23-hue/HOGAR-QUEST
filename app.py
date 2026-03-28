import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

st.set_page_config(layout="centered", page_title="Hogar Quest Cloud", page_icon="☁️")

# --- CONEXIÓN A GOOGLE SHEETS ---
url = https://docs.google.com/spreadsheets/d/1g90SMibEDEW4_d4d1C2R08SzMfP6KboMtEo-XuDUi1s/edit?usp=sharing
conn = st.connection("gsheets", type=GSheetsConnection)

# --- CARGAR TAREAS LOCALES (Tu CSV) ---
@st.cache_data
def cargar_maestro():
    df = pd.read_csv("tareas.xlsx - Hoja1.csv")
    df['ÁMBITO'] = df['ÁMBITO'].ffill()
    df['PUNTOS'] = pd.to_numeric(df['PUNTOS'], errors='coerce').fillna(5).astype(int)
    return df

df_maestro = cargar_maestro()

# --- INTERFAZ ---
st.title("⚔️ HOGAR QUEST COMPARTIDO")

# Selector de usuario para saber quién suma
usuario = st.radio("¿Quién eres?", ["Jugador 1", "Jugador 2"], horizontal=True)

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
                    # Crear nueva fila
                    ahora = datetime.datetime.now()
                    nueva_fila = pd.DataFrame([{
                        "Fecha": ahora.strftime("%Y-%m-%d"),
                        "Semana": ahora.isocalendar()[1],
                        "Mes": ahora.strftime("%Y-%m"),
                        "Ámbito": ambito,
                        "Tarea": row['TAREA'],
                        "Puntos": row['PUNTOS'],
                        "Usuario": usuario
                    }])
                    
                    # Leer datos actuales, añadir nuevo y guardar
                    data_actual = conn.read(spreadsheet=url)
                    updated_df = pd.concat([data_actual, nueva_fila], ignore_index=True)
                    conn.update(spreadsheet=url, data=updated_df)
                    
                    st.success(f"¡{row['PUNTOS']} XP para {usuario}!")
                    st.balloons()
                    st.cache_data.clear() # Limpiar cache para ver datos nuevos

with tab2:
    try:
        df_h = conn.read(spreadsheet=url)
        if df_h.empty:
            st.info("El marcador está a cero. ¡A trabajar!")
        else:
            # Ranking por usuario
            st.subheader("🏆 Marcador Global")
            ranking = df_h.groupby("Usuario")["Puntos"].sum().reset_index()
            st.table(ranking)

            # Puntos por semana
            st.subheader("📅 Puntos por Semana")
            df_semana = df_h.groupby(["Semana", "Usuario"])["Puntos"].sum().unstack().fillna(0)
            st.bar_chart(df_semana)
            
    except:
        st.warning("Aún no hay datos en la nube.")
