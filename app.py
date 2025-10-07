import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

st.set_page_config(layout="centered")
st.title("🎯 Registro Frecce - Interattivo")

# === Config ===
STORICO_FILE = "storico_frecce.csv"
session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# === Init file ===
if not os.path.exists(STORICO_FILE):
    pd.DataFrame(columns=["datetime", "session_id", "volee", "freccia", "x", "y", "punteggio", "distanza"])\
      .to_csv(STORICO_FILE, index=False)

# === UI Input ===
distanza = st.selectbox("📏 Seleziona la distanza", ["18", "20", "25", "30", "40", "50", "60", "70"])
frecce_per_volee = st.selectbox("🏹 Numero di frecce per volee", [3, 6])

if "colpi" not in st.session_state:
    st.session_state.colpi = []

# === Funzione punteggio ===
def calcola_punteggio(x, y):
    d = np.sqrt(x**2 + y**2)
    for raggio, punti in zip(range(10, 0, -1), range(1, 11)):
        if d <= raggio:
            return punti
    return 0

# === Bersaglio con cerchi ===
fig = go.Figure()

colori = ['#FFFF00', '#FF0000', '#0000FF', '#000000', '#FFFFFF']  # Giallo, rosso, blu, nero, bianco
r = 10
for colore in colori:
    for _ in range(2):
        fig.add_shape(
            type="circle",
            x0=-r, y0=-r, x1=r, y1=r,
            line_color="black",
            fillcolor=colore,
            layer="below"
        )
        r -= 1

# === Aggiungi i colpi precedenti ===
for i, (x, y) in enumerate(st.session_state.colpi):
    fig.add_trace(go.Scatter(x=[x], y=[y], mode='markers+text',
                             marker=dict(size=10, color='lime'),
                             text=[str(i+1)], textposition="top center"))

# === Layout ===
fig.update_layout(
    width=600, height=600,
    xaxis=dict(range=[-10, 10], zeroline=False),
    yaxis=dict(range=[-10, 10], zeroline=False),
    dragmode='drawopenpath',
    margin=dict(l=0, r=0, t=0, b=0),
    plot_bgcolor='white'
)

# === Plotly chart ===
click = st.plotly_chart(fig, use_container_width=True)

# === Slider X/Y ===
x = st.slider("X", -10.0, 10.0, value=0.0, step=0.1, key="x_slider")
y = st.slider("Y", -10.0, 10.0, value=0.0, step=0.1, key="y_slider")

if st.button("➕ Aggiungi Freccia"):
    if len(st.session_state.colpi) < frecce_per_volee:
        st.session_state.colpi.append((x, y))
        st.rerun()
    else:
        st.warning("Hai già registrato tutte le frecce per questa volee.")

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
