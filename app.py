import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
import os

st.set_page_config(layout="centered", page_title="Registro Frecce")
st.title("🎯 Registro Frecce - Allenamento")

STORICO_FILE = "storico_frecce.csv"
if not os.path.exists(STORICO_FILE):
    df_vuoto = pd.DataFrame(columns=["datetime", "session_id", "volee", "freccia", "x", "y", "punteggio", "distanza"])
    df_vuoto.to_csv(STORICO_FILE, index=False)

# Selezioni iniziali
distanze = ["18", "20", "25", "30", "40", "50", "60", "70"]
distanza = st.selectbox("📏 Seleziona la distanza", distanze)
frecce_per_volee = st.selectbox("🏹 Numero di frecce per volee", [3, 6])
session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Funzione per calcolo punteggio
def calcola_punti(x, y):
    r = np.sqrt(x**2 + y**2)
    zone = [1,2,3,4,5,6,7,8,9,10]
    for i, val in enumerate(reversed(zone)):
        if r <= val:
            return 10 - i
    return 0

# Genera griglia
res = 0.2  # risoluzione della griglia: più basso = più quadratini
x_vals = np.arange(-10, 10+res, res)
y_vals = np.arange(-10, 10+res, res)
data = []

for x in x_vals:
    for y in y_vals:
        score = calcola_punti(x, y)
        data.append({"x": x, "y": y, "score": score})

df = pd.DataFrame(data)

# Plot griglia
fig = px.density_heatmap(
    df, x="x", y="y", z="score", nbinsx=len(x_vals), nbinsy=len(y_vals),
    color_continuous_scale="YlOrRd", range_color=[0,10],
    labels={"score": "Punteggio"}
)

fig.update_layout(
    width=500, height=500,
    clickmode='event+select',
    dragmode=False,
    margin=dict(l=0, r=0, t=0, b=0)
)

st.write("🖐️ Clicca su un punto del bersaglio per aggiungere una freccia")

# Mostra grafico e gestisci click
click = st.plotly_chart(fig, use_container_width=True)

if "colpi" not in st.session_state:
    st.session_state.colpi = []

# Gestione clic
clicked_point = st.session_state.get("clicked_point", None)
selected_data = st.session_state.get("selected_data", None)

selected = st.get_query_params().get("selected")

if "plotly_click_data" in st.session_state:
    point = st.session_state["plotly_click_data"]["points"][0]
    x, y = point["x"], point["y"]

    if len(st.session_state.colpi) < frecce_per_volee:
        st.session_state.colpi.append((x, y))
        st.success(f"Freccia registrata in posizione ({x:.1f}, {y:.1f}) - Punteggio: {calcola_punti(x, y)}")
    else:
        st.warning("Hai già registrato tutte le frecce per questa volee.")

# Mostra frecce registrate
if st.session_state.colpi:
    st.markdown("### 🏹 Frecce registrate:")
    for i, (x, y) in enumerate(st.session_state.colpi, 1):
        st.write(f"{i}. x = {x:.1f}, y = {y:.1f}, punteggio = {calcola_punti(x, y)}")

# Salva volee
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
                "punteggio": calcola_punti(x, y),
                "distanza": distanza
            }
            for i, (x, y) in enumerate(st.session_state.colpi)
        ])
        df_storico = pd.read_csv(STORICO_FILE)
        df_finale = pd.concat([df_storico, df_nuovo], ignore_index=True)
        df_finale.to_csv(STORICO_FILE, index=False)
        st.success("✅ Volee salvata!")
        st.session_state.colpi = []
