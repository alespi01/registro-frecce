import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import os

# === CONFIGURAZIONE ===
STORICO_FILE = "storico_frecce.csv"
GRID_SIZE = 100  # numero di quadrati per lato
MAX_SCORE = 10
CENTER = GRID_SIZE // 2
RING_WIDTH = GRID_SIZE / (2 * MAX_SCORE)

# === INIZIALIZZAZIONE FILE STORICO ===
if not os.path.exists(STORICO_FILE):
    df_vuoto = pd.DataFrame(columns=["datetime", "session_id", "volee", "freccia", "x", "y", "punteggio", "distanza"])
    df_vuoto.to_csv(STORICO_FILE, index=False)

# === TITOLO E SCELTE ===
st.set_page_config(page_title="Registro Frecce", layout="wide")
st.title("🎯 Registro Frecce - Allenamento")

distanza = st.selectbox("📏 Seleziona la distanza (metri)", ["18", "20", "25", "30", "40", "50", "60", "70"])
frecce_per_volee = st.selectbox("🏹 Frecce per volee", [3, 6])
session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# === CALCOLO PUNTEGGIO IN BASE ALLA DISTANZA DAL CENTRO ===
def calcola_punteggio(x, y):
    dx = x - CENTER
    dy = y - CENTER
    distanza = np.sqrt(dx**2 + dy**2)
    punteggio = MAX_SCORE - int(distanza // RING_WIDTH)
    return max(punteggio, 0)

# === CREA GRIGLIA DI QUADRATINI CON PUNTEGGI ===
x_vals = np.arange(GRID_SIZE)
y_vals = np.arange(GRID_SIZE)
X, Y = np.meshgrid(x_vals, y_vals)
Z = np.vectorize(calcola_punteggio)(X, Y)

df = pd.DataFrame({
    "x": X.ravel(),
    "y": Y.ravel(),
    "punteggio": Z.ravel()
})

# === MOSTRA GRAFICO INTERATTIVO ===
st.subheader("🖐️ Clicca su un quadrato per registrare la freccia")
fig = px.imshow(Z, origin='lower', color_continuous_scale="YlOrRd", width=600, height=600)
fig.update_layout(
    dragmode="select",
    margin=dict(l=10, r=10, t=10, b=10),
    coloraxis_showscale=False
)
selected = st.plotly_chart(fig, use_container_width=False)

# === INIZIALIZZA SESSIONE ===
if "colpi" not in st.session_state:
    st.session_state.colpi = []

# === INSERIMENTO MANUALE (FINO A CLICK DIRETTO) ===
x = st.slider("🔧 Oppure regola X", 0, GRID_SIZE-1, CENTER)
y = st.slider("🔧 Oppure regola Y", 0, GRID_SIZE-1, CENTER)

if st.button("➕ Aggiungi freccia"):
    if len(st.session_state.colpi) < frecce_per_volee:
        st.session_state.colpi.append((x, y))
    else:
        st.warning("Hai già inserito tutte le frecce della volee.")

# === MOSTRA COLPI ===
if st.session_state.colpi:
    st.write("📌 Frecce registrate:")
    for i, (x, y) in enumerate(st.session_state.colpi, 1):
        p = calcola_punteggio(x, y)
        st.write(f"Freccia {i}: ({x}, {y}) → {p} punti")

# === SALVA ===
if st.button("💾 Salva volee"):
    if not st.session_state.colpi:
        st.error("⚠️ Nessuna freccia registrata.")
    else:
        df_nuovo = pd.DataFrame([
            {
                "datetime": datetime.now().isoformat(),
                "session_id": session_id,
                "volee": 1,
                "freccia": i + 1,
                "x": x,
                "y": y,
                "punteggio": calcola_punteggio(x, y),
                "distanza": distanza
            }
            for i, (x, y) in enumerate(st.session_state.colpi)
        ])
        df_storico = pd.read_csv(STORICO_FILE)
        df_finale = pd.concat([df_storico, df_nuovo], ignore_index=True)
        df_finale.to_csv(STORICO_FILE, index=False)
        st.success("✅ Volee salvata!")
        st.session_state.colpi = []
