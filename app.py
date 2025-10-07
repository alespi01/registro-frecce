import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image, ImageDraw
from streamlit_drawable_canvas import st_canvas

# === Config pagina ===
st.set_page_config(layout="centered", page_title="Registro Frecce")
st.title("🎯 Registro Frecce - Allenamento")

# === File dati ===
STORICO_FILE = "storico_frecce.csv"

# === Inizializza file se non esiste ===
if not os.path.exists(STORICO_FILE):
    df_vuoto = pd.DataFrame(columns=["datetime", "session_id", "volee", "freccia", "x", "y", "punteggio", "distanza"])
    df_vuoto.to_csv(STORICO_FILE, index=False)

# === Selezione distanza e n. frecce ===
distanza = st.selectbox("📏 Seleziona la distanza", ["18", "20", "25", "30", "40", "50", "60", "70"])
frecce_per_volee = st.selectbox("🏹 Frecce per volee", [3, 6])

# === ID sessione ===
session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# === Funzione bersaglio ===
def genera_bersaglio_img(size=500):
    img = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(img)
    colori = ["#FFD700", "red", "blue", "black", "white"]
    raggio = size // 2
    step = raggio // 5

    for i, colore in enumerate(colori):
        draw.ellipse(
            [
                (size/2 - raggio + i*step, size/2 - raggio + i*step),
                (size/2 + raggio - i*step, size/2 + raggio - i*step)
            ],
            fill=colore,
            outline="black"
        )
    return img

# === Sessione colpi ===
if "colpi" not in st.session_state:
    st.session_state.colpi = []

st.subheader("🖐️ Tocca il bersaglio per registrare una freccia")
canvas_size = 500
image = genera_bersaglio_img(size=canvas_size)

# === Canvas interattivo ===
canvas_result = st_canvas(
    fill_color="rgba(255, 0, 0, 0.3)",
    stroke_width=0,
    background_image=image,
    update_streamlit=True,
    height=canvas_size,
    width=canvas_size,
    drawing_mode="point",
    point_display_radius=5,
    key="canvas"
)

# === Gestione clic sul bersaglio ===
if canvas_result.json_data is not None and len(canvas_result.json_data["objects"]) > 0:
    last_point = canvas_result.json_data["objects"][-1]
    x = round(last_point["left"])
    y = round(last_point["top"])
    st.write(f"🧭 Coordinate: x={x}, y={y}")

    def calcola_punteggio(x, y):
        dx = x - canvas_size / 2
        dy = y - canvas_size / 2
        distanza = (dx**2 + dy**2)**0.5
        step = (canvas_size / 2) / 5
        zone = [step * i for i in range(1, 6)]
        for i, limite in enumerate(reversed(zone)):
            if distanza <= limite:
                return 10 - i * 2
        return 0

    punteggio = calcola_punteggio(x, y)
    st.write(f"🎯 Punteggio: {punteggio}")

    if st.button("➕ Aggiungi Freccia"):
        if len(st.session_state.colpi) < frecce_per_volee:
            st.session_state.colpi.append((x, y, punteggio))
            st.success("✅ Freccia aggiunta!")
        else:
            st.warning("Hai già registrato tutte le frecce per questa volee.")

# === Mostra frecce registrate ===
if st.session_state.colpi:
    st.markdown("### 📌 Frecce registrate:")
    for i, (x, y, p) in enumerate(st.session_state.colpi):
        st.write(f"Freccia {i+1}: x={x}, y={y}, punteggio={p}")

# === Salvataggio ===
if st.button("💾 Salva volee"):
    if not st.session_state.colpi:
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
                "punteggio": p,
                "distanza": distanza
            }
            for i, (x, y, p) in enumerate(st.session_state.colpi)
        ])
        df_storico = pd.read_csv(STORICO_FILE)
        df_finale = pd.concat([df_storico, df_nuovo], ignore_index=True)
        df_finale.to_csv(STORICO_FILE, index=False)
        st.success("📁 Volee salvata!")
        st.session_state.colpi = []
