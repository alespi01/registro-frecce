import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import os
from streamlit_plotly_events import plotly_events

# === Config ===
st.set_page_config(layout="centered", page_title="Registro Frecce")
st.title("🎯 Registro Frecce - Allenamento")

STORICO_FILE = "storico_frecce.csv"
if not os.path.exists(STORICO_FILE):
    df_vuoto = pd.DataFrame(columns=["datetime", "session_id", "volee", "freccia", "x", "y", "punteggio", "distanza"])
    df_vuoto.to_csv(STORICO_FILE, index=False)

distanza = st.selectbox("📏 Seleziona la distanza", ["18", "20", "25", "30", "40", "50", "60", "70"])
frecce_per_volee = st.selectbox("🏹 Numero di frecce per volee", [3, 6])
session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# === Build target with scoring rings ===
step = 0.2
x_vals = np.arange(-10, 10, step)
y_vals = np.arange(-10, 10, step)
xx, yy = np.meshgrid(x_vals, y_vals)
r = np.sqrt(xx**2 + yy**2)

def punteggio_da_raggio(r):
    for i in range(10, 0, -1):
        if r <= i:
            return i
    return 0

# Apply score for each square
punteggi = np.vectorize(punteggio_da_raggio)(r)

# Build dataframe
df = pd.DataFrame({
    'x': xx.ravel(),
    'y': yy.ravel(),
    'score': punteggi.ravel()
})

# === Plot ===
# === Plot === (updated with discrete colors)
color_map = {
    10: "gold",
    9: "gold",
    8: "red",
    7: "red",
    6: "blue",
    5: "blue",
    4: "black",
    3: "black",
    2: "white",
    1: "white",
    0: "gray"
}

df["color"] = df["score"].map(color_map)

fig = px.scatter(
    df, x="x", y="y",
    color="color",
    color_discrete_map=color_map,
    opacity=0.6
)

fig.update_traces(marker=dict(size=3))
fig.update_layout(
    width=600,
    height=600,
    showlegend=False,
    dragmode="pan",
    clickmode="event+select",
    xaxis=dict(range=[-10.5, 10.5], zeroline=False),
    yaxis=dict(range=[-10.5, 10.5], scaleanchor="x", zeroline=False),
    margin=dict(t=20, r=20, b=20, l=20),
)


st.subheader("🖐️ Clicca sul bersaglio per registrare la freccia")

if "colpi" not in st.session_state:
    st.session_state.colpi = []

# === Display plot & get click ===
selected_points = plotly_events(fig, click_event=True, key="canvas")

if selected_points and len(st.session_state.colpi) < frecce_per_volee:
    point = selected_points[0]
    x, y = point['x'], point['y']
    score = punteggio_da_raggio((x**2 + y**2)**0.5)
    st.session_state.colpi.append((x, y, score))
    st.success(f"📍 Freccia registrata a ({x:.1f}, {y:.1f}) - Punti: {score}")
elif selected_points and len(st.session_state.colpi) >= frecce_per_volee:
    st.warning("Hai già registrato tutte le frecce per questa volee.")

# === Show current arrows ===
if st.session_state.colpi:
    st.subheader("📌 Frecce registrate finora")
    for i, (x, y, score) in enumerate(st.session_state.colpi, 1):
        st.markdown(f"- Freccia {i}: ({x:.1f}, {y:.1f}) → {score} punti")

# === Save to CSV ===
if st.button("💾 Salva volee"):
    if not st.session_state.colpi:
        st.error("Nessuna freccia registrata.")
    else:
        df_nuovo = pd.DataFrame([{
            "datetime": datetime.now().isoformat(),
            "session_id": session_id,
            "volee": 1,
            "freccia": i + 1,
            "x": x,
            "y": y,
            "punteggio": score,
            "distanza": distanza
        } for i, (x, y, score) in enumerate(st.session_state.colpi)])
        
        df_storico = pd.read_csv(STORICO_FILE)
        df_finale = pd.concat([df_storico, df_nuovo], ignore_index=True)
        df_finale.to_csv(STORICO_FILE, index=False)
        st.success("✅ Volee salvata!")
        st.session_state.colpi = []
