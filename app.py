import streamlit as st
from streamlit_drawable_canvas import st_canvas
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime
import os
from io import BytesIO
from PIL import Image

st.set_page_config(layout="centered", page_title="Registro Frecce")

STORICO_FILE = "storico_frecce.csv"

# === Inizializza file se non esiste ===
if not os.path.exists(STORICO_FILE):
    df_vuoto = pd.DataFrame(columns=["datetime", "session_id", "x", "y", "punteggio", "distanza"])
    df_vuoto.to_csv(STORICO_FILE, index=False)

# === Input iniziali ===
st.title("🎯 Registro Frecce Interattivo")
distanze_disponibili = ["18", "20", "25", "30", "40", "50", "60", "70"]
distanza = st.selectbox("📏 Seleziona la distanza", distanze_disponibili)
session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# === Funzione: disegna bersaglio e restituisce immagine ===
def genera_bersaglio_image():
    fig, ax = plt.subplots(figsize=(5, 5), dpi=100)
    colori = ['white', 'black', 'blue', 'red', 'yellow']
    r = 10
    for c in colori:
        for _ in range(2):
            ax.add_patch(patches.Circle((250, 250), r * 25, color=c, ec='black'))
            r -= 1
    ax.set_xlim(0, 500)
    ax.set_ylim(0, 500)
    ax.axis('off')
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf)

# === Sfondo del bersaglio ===
img = genera_bersaglio_image()

# === Canvas interattivo ===
st.subheader("🖐️ Trascina la X sul bersaglio")
canvas_result = st_canvas(
    fill_color="rgba(0, 255, 0, 0.3)",
    stroke_width=3,
    background_image=img,
    update_streamlit=True,
    height=500,
    width=500,
    drawing_mode="transform",
    key="canvas",
    initial_drawing=[
        {"type": "path", "path": [{"x": 250, "y": 250}], "stroke": "green", "width": 0},
        {"type": "text", "left": 245, "top": 245, "text": "X", "font": "20px serif", "fill": "green"}
    ],
)

# === Leggi coordinate ===
if canvas_result.json_data and len(canvas_result.json_data["objects"]) >= 2:
    pos = canvas_result.json_data["objects"][1]
    x = round(pos["left"] - 250, 1) / 25
    y = round(250 - pos["top"], 1) / 25
    st.write(f"📍 Coordinata registrata: **X = {x}**, **Y = {y}**")
else:
    x, y = 0.0, 0.0

# === Slider (sincronizzati) ===
st.slider("🔄 X", -10.0, 10.0, value=x, step=0.1, disabled=True)
st.slider("🔽 Y", -10.0, 10.0, value=y, step=0.1, disabled=True)

# === Calcola punteggio ===
def calcola_punteggio(x, y):
    d = (x**2 + y**2)**0.5
    for raggio, punti in zip(range(10, 0, -1), range(1, 11)):
        if d <= raggio:
            return punti
    return 0

# === Salvataggio ===
if st.button("💾 Salva Freccia"):
    punteggio = calcola_punteggio(x, y)
    nuova = pd.DataFrame([{
        "datetime": datetime.now().isoformat(),
        "session_id": session_id,
        "x": x,
        "y": y,
        "punteggio": punteggio,
        "distanza": distanza
    }])
    df = pd.read_csv(STORICO_FILE)
    df = pd.concat([df, nuova], ignore_index=True)
    df.to_csv(STORICO_FILE, index=False)
    st.success(f"✅ Freccia salvata con punteggio {punteggio}")
