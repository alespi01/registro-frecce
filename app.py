import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime
import os

# === Configura pagina ===
st.set_page_config(layout="centered", page_title="Registro Frecce")
st.title("🎯 Registro Frecce - Allenamento")

# === File dati ===
STORICO_FILE = "storico_frecce.csv"

# === Inizializza file se non esiste ===
if not os.path.exists(STORICO_FILE):
    df_vuoto = pd.DataFrame(columns=["datetime", "session_id", "volee", "freccia", "x", "y", "punteggio", "distanza"])
    df_vuoto.to_csv(STORICO_FILE, index=False)

# === Input iniziali ===
distanze_disponibili = ["18", "20", "25", "30", "40", "50", "60", "70"]
distanza = st.selectbox("📏 Seleziona la distanza", distanze_disponibili)
frecce_per_volee = st.selectbox("🏹 Numero di frecce per volee", [3, 6])
st.write("👇 Registra le frecce con i cursori")

# === Sessione ===
session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# === Funzioni ===
def calcola_punteggio(x, y):
    d = (x**2 + y**2)**0.5
    for raggio, punti in zip(range(10, 0, -1), range(1, 11)):
        if d <= raggio:
            return punti
    return 0

def disegna_bersaglio(colpi):
    fig, ax = plt.subplots(figsize=(6, 6))
    colori = ['white', 'black', 'blue', 'red', 'yellow']
    r = 10
    for c in colori:
        for _ in range(2):
            ax.add_patch(patches.Circle((0, 0), r, color=c, ec='black'))
            r -= 1

    for i, (x, y) in enumerate(colpi):
        ax.plot(x, y, 'x', color='limegreen', markersize=8)
        ax.text(x + 0.3, y + 0.3, str(i+1), fontsize=10)

    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    return fig

# === Interfaccia interattiva ===
if "colpi" not in st.session_state:
    st.session_state.colpi = []

st.subheader("🖐️ Registra ogni freccia")

x = st.slider("🔄 Coordinata X", -10.0, 10.0, 0.0, 0.1)
y = st.slider("🔽 Coordinata Y", -10.0, 10.0, 0.0, 0.1)

if st.button("➕ Aggiungi Freccia"):
    if len(st.session_state.colpi) < frecce_per_volee:
        st.session_state.colpi.append((x, y))
    else:
        st.warning("Hai già registrato tutte le frecce per questa volee.")

# === Visualizza bersaglio ===
fig = disegna_bersaglio(st.session_state.colpi)
st.pyplot(fig, clear_figure=True)

# === Salvataggio ===
if st.button("💾 Salva volee"):
    if not st.session_state.colpi:
        st.error("Nessuna freccia registrata.")
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
