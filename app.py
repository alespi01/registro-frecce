import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from streamlit_drawable_canvas import st_canvas
from datetime import datetime
from PIL import Image
import io
import os

# === Config pagina ===
st.set_page_config(layout="centered", page_title="Registro Frecce")

st.title("🎯 Registro Frecce - Allenamento")

STORICO_FILE = "storico_frecce.csv"

# === Inizializza file CSV se non esiste ===
if not os.path.exists(STORICO_FILE):
    df_vuoto = pd.DataFrame(columns=["datetime", "session_id", "volee", "freccia", "x", "y", "punteggio", "distanza"])
    df_vuoto.to_csv(STORICO_FILE, index=False)

# === Parametri iniziali ===
distanza = st.selectbox("📏 Seleziona la distanza (metri)", ["18", "20", "25", "30", "40", "50", "60", "70"])
frecce_per_volee = st.selectbox("🏹 Frecce per volee", [3, 6])
session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# === Funzione punteggio ===
def calcola_punteggio(x, y):
    d = (x**2 + y**2)**0.5
    for raggio, punti in zip(range(10, 0, -1), range(1, 11)):
        if d <= raggio:
            return punti
    return 0

# === Genera bersaglio ===
def genera_bersaglio():
    fig, ax = plt.subplots(figsize=(6, 6))
    colori = ['white', 'black', 'blue', 'red', 'yellow']
    r = 10
    for colore in colori:
        for _ in range(2):
            ax.add_patch(patches.Circle((0, 0), r, color=colore, ec='black'))
            r -= 1
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.set_aspect('equal')
    ax.axis('off')

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight', dpi=150)
    buf.seek(0)
    plt.close(fig)
    return Image.open(buf)

# === Bersaglio interattivo ===
st.subheader("🖐️ Tocca sul bersaglio per segnare le frecce")

img = genera_bersaglio()

canvas_result = st_canvas(
    fill_color="rgba(0, 255, 0, 0.3)",
    background_image=img,
    update_streamlit=True,
    height=500,
    width=500,
    drawing_mode="point",
    point_display_radius=5,
    key="canvas"
)

# === Estrai coordinate ===
if canvas_result.json_data is not None:
    colpi = []
    for obj in canvas_result.json_data["objects"]:
        cx = obj["left"]
        cy = obj["top"]
        x = (cx / 500) * 20 - 10  # da canvas a -10/10
        y = (500 - cy) / 500 * 20 - 10
        colpi.append((x, y))
    st.session_state.colpi = colpi

# === Mostra frecce registrate ===
if "colpi" in st.session_state and st.session_state.colpi:
    st.subheader("📌 Frecce registrate:")
    for i, (x, y) in enumerate(st.session_state.colpi):
        punteggio = calcola_punteggio(x, y)
        st.write(f"• Freccia {i+1}: x={x:.2f}, y={y:.2f} → punti: {punteggio}")
else:
    st.info("Tocca il bersaglio per iniziare a registrare.")

# === Salvataggio ===
if st.button("💾 Salva volee"):
    if "colpi" not in st.session_state or not st.session_state.colpi:
        st.error("⚠️ Nessuna freccia da salvare.")
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
