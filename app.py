import streamlit as st
import pandas as pd
import datetime

st.set_page_config(layout="centered", page_title="Hogar Quest", page_icon="⚔️")

# --- 1. INICIALIZAR LA MEMORIA DEL DÍA ---
if 'historial' not in st.session_state:
    st.session_state.historial = []

# --- 2. CARGAR TAREAS DEL CSV ---
@st.cache_data
def cargar_maestro():
    df = pd.read_csv("tareas.xlsx - Hoja1.csv")
    df['ÁMBITO'] = df['ÁMBITO'].ffill()
    df['PUNTOS'] = pd.to_numeric(df['PUNTOS'], errors='coerce').fillna(5).astype(int)
    return df

df_maestro = cargar_maestro()

# --- 3. INTERFAZ Y MARCADOR ---
st.title("⚔️ HOGAR QUEST")

# Calcular puntos sumando el historial de la memoria
puntos_totales = sum(tarea['Puntos'] for tarea in st.session_state.historial)

# Marcador superior
st.metric("🏆 Puntos de Hoy", f"{puntos_totales} XP")
st.divider()

# --- 4. PESTAÑAS ---
tab1, tab2 = st.tabs(["🎮 Misiones", "📜 Histórico y Reset"])

with tab1:
    st.subheader("Misiones Disponibles")
    for ambito in df_maestro['ÁMBITO'].unique():
        with st.expander(f"📍 {ambito}"):
            tareas = df_maestro[df_maestro['ÁMBITO'] == ambito]
            for idx, row in tareas.iterrows():
                col_t, col_p, col_b = st.columns([3, 1, 1])
                col_t.write(row['TAREA'])
                col_p.write(f"**{row['PUNTOS']} XP**")
                
                if col_b.button("✅", key=f"btn_{idx}"):
                    # Guardar la tarea en la memoria temporal
                    st.session_state.historial.append({
                        "Hora": datetime.datetime.now().strftime("%H:%M"),
                        "Ámbito": ambito,
                        "Tarea": row['TAREA'],
                        "Puntos": row['PUNTOS']
                    })
                    st.success(f"¡{row['PUNTOS']} XP conseguidos!")
                    st.balloons()  # Los globos clásicos
                    st.rerun()     # Recarga para actualizar el marcador arriba

with tab2:
    st.subheader("📜 Histórico de Hoy")
    
    if len(st.session_state.historial) == 0:
        st.info("Aún no has completado ninguna misión hoy.")
    else:
        # Mostrar tabla con el registro de lo que se ha hecho
        df_historial = pd.DataFrame(st.session_state.historial)
        st.dataframe(df_historial, use_container_width=True)
    
    st.divider()
    st.warning("⚠️ Al final del día, pulsa aquí para volver a empezar.")
    
    # Botón de Reset
    if st.button("🔄 Resetear Día (Volver a 0)"):
        st.session_state.historial = []
        st.rerun()
