import streamlit as st
import pandas as pd
import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(layout="centered", page_title="Hogar Quest", page_icon="🏠")

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .main-title { color: #2e7d32; text-align: center; font-family: monospace; font-weight: bold; }
    .score-box { background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); text-align: center; border: 2px solid #2e7d32; margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

# --- TÍTULO ---
st.markdown("<h1 class='main-title'>⚔️ HOGAR QUEST ⚔️<br>La Batalla del Orden</h1>", unsafe_allow_html=True)

# --- 1. CARGAR DATOS DESDE TU CSV ---
@st.cache_data
def cargar_tareas():
    try:
        # Leemos el archivo CSV
        df = pd.read_csv("tareas.xlsx - Hoja1.csv")
        
        # 1. Rellenar los "Ámbitos" vacíos (por las celdas combinadas de Excel)
        df['ÁMBITO'] = df['ÁMBITO'].ffill()
        
        # 2. Si alguna tarea no tiene puntos, le ponemos 5 por defecto y aseguramos que sea número
        df['PUNTOS'] = pd.to_numeric(df['PUNTOS'], errors='coerce').fillna(5).astype(int)
        
        # 3. Limpiamos nombres de columnas por si acaso tienen espacios
        df.columns = df.columns.str.strip()
        
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo CSV. Asegúrate de que se llama 'tareas.xlsx - Hoja1.csv' y está en la misma carpeta. Error: {e}")
        return pd.DataFrame()

df_tareas = cargar_tareas()

# --- 2. GESTIÓN DEL ESTADO (Puntuación e Historial) ---
if 'total_puntos' not in st.session_state:
    st.session_state.total_puntos = 0
if 'historial_tareas' not in st.session_state:
    st.session_state.historial_tareas = []

# --- 3. ÁREA DE MARCADOR ---
if not df_tareas.empty:
    st.markdown("<div class='score-box'>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("## 🏆\nPuntos Actuales")
    with c2:
        st.markdown(f"<h1 style='color: #2e7d32; font-size: 50px; margin:0;'>{st.session_state.total_puntos} XP</h1>", unsafe_allow_html=True)
        
    # Sistema de Rangos
    rango = "Novato del Orden 🥉"
    if st.session_state.total_puntos >= 50: rango = "Aprendiz de la Limpieza 🥈"
    if st.session_state.total_puntos >= 150: rango = "Guerrero del Hogar 🥇"
    if st.session_state.total_puntos >= 300: rango = "Maestro del Esponja 💎"
    if st.session_state.total_puntos >= 500: rango = "Leyenda Suprema (Nivel Dios) 👑"
        
    st.markdown(f"**Rango Actual:** {rango}")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- 4. ÁREA DE MISIONES (Agrupadas por Ámbito) ---
    st.subheader("🗺️ Mapa de Misiones")
    
    # Agrupamos por ámbito (Cocina, Baño, Rita, etc.)
    ambitos = df_tareas['ÁMBITO'].dropna().unique()
    
    for ambito in ambitos:
        # Usamos un "expander" (acordeón) para que no sea una lista gigante
        with st.expander(f"📍 {ambito}"):
            tareas_ambito = df_tareas[df_tareas['ÁMBITO'] == ambito]
            
            for index, row in tareas_ambito.iterrows():
                col_text, col_pts, col_btn = st.columns([3, 1, 1])
                
                with col_text:
                    st.write(f"**{row['TAREA']}**")
                with col_pts:
                    st.markdown(f"<span style='color:#2e7d32; font-weight:bold;'>+{row['PUNTOS']} XP</span>", unsafe_allow_html=True)
                with col_btn:
                    # Botón para completar
                    if st.button("Completar", key=f"btn_{index}"):
                        st.session_state.total_puntos += row['PUNTOS']
                        hora_actual = datetime.datetime.now().strftime("%H:%M")
                        st.session_state.historial_tareas.insert(0, {
                            "Hora": hora_actual,
                            "Zona": ambito,
                            "Misión": row['TAREA'],
                            "XP": row['PUNTOS']
                        })
                        st.rerun()

    st.write("---")

    # --- 5. HISTORIAL DE BATALLA ---
    st.subheader("📜 Historial de Batalla (Hoy)")
    if not st.session_state.historial_tareas:
        st.info("Aún no has completado ninguna misión hoy. ¡Ve a por tu primera victoria!")
    else:
        df_historial = pd.DataFrame(st.session_state.historial_tareas)
        st.dataframe(df_historial, use_container_width=True, hide_index=True)
        
        if st.button("🔄 Terminar Día (Reiniciar Marcador)"):
            st.session_state.total_puntos = 0
            st.session_state.historial_tareas = []
            st.rerun()
