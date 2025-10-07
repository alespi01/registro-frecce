import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from datetime import datetime
import numpy as np
import os

# === Config ===
st.set_page_config(layout="centered", page_title="Registro Frecce")
st.title("🎯 Registro Frecce - Grid Target")

# === File dati ===
STORICO_FILE = "storico_frecce.csv"
if not os.path.exists(STORICO_FILE):
    df_vuoto = pd.DataFrame(columns=["datetime", "session_id", "volee", "freccia", "x", "y", "punteggio", "distanza"])
    df_vuoto.to_csv(STORICO_FILE, index=False)

# === Inizializza sessione ===
session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
if "colpi" not in st.session_state:
    st.session_state.colpi = []

# === Selezione distanza ===
distanza = st.selectbox("📏 Seleziona la distanza (metri)", ["18", "20", "25", "30", "40", "50", "60", "70"])
frecce_per_volee = st.selectbox("🏹 Numero di frecce per volee", [3, 6])

# === Funzione punteggio ===
def calcola_punteggio(x, y):
    d = (x**2 + y**2)**0.5
    for raggio, punti in zip(range(10, 0, -1), range(1, 11)):
        if d <= raggio:
            return punti
    return 0

# === Genera griglia ===
grid_size = 0.2
x_vals = np.arange(-10, 10 + grid_size, grid_size)
y_vals = np.arange(-10, 10 + grid_size, grid_size)
grid_x, grid_y = np.meshgrid(x_vals, y_vals)
flat_x = grid_x.flatten()
flat_y = grid_y.flatten()
scores = [calcola_punteggio(x, y) for x, y in zip(flat_x, flat_y)]

# === Visualizza bersaglio a griglia ===
fig = go.Figure()

fig.add_trace(go.Scattergl(
    x=flat_x,
    y=flat_y,
    mode='markers',
    marker=dict(
        color=scores,
        colorscale='Jet',
        size=8,
        colorbar=dict(title='Punti'),
        line=dict(width=0)
    ),
    hovertemplate="x: %{x:.2f}<br>y: %{y:.2f}<br>Punti: %{marker.color}<extra></extra>"
))

# Mostra le frecce già aggiunte
for i, (x, y) in enumerate(st.session_state.colpi):
    fig.add_trace(go.Scatter(
        x=[x], y=[y],
        mode='markers+text',
        marker=dict(color='limegreen', size=12, symbol='x'),
        text=[str(i + 1)],
        textposition="top center",
        showlegend=False
    ))

fig.update_layout(
    height=600,
    width=600,
    margin=dict(l=10, r=10, t=10, b=10),
    title="🖐️ Clicca sul bersaglio per selezionare una freccia",
    clickmode='event+select',
    xaxis=dict(scaleanchor="y", range=[-10, 10]),
    yaxis=dict(range=[-10, 10])
)

# === Mostra bersaglio ===
click = st.plotly_chart(fig, use_container_width=True)

# === Usa callback di selezione (solo su Streamlit local o desktop) ===
st.markdown("ℹ️ Clicca sul grafico per selezionare la posizione. (Streamlit Cloud non supporta clic diretti nativamente).")
x_sel = st.number_input("📍 X", -10.0, 10.0, 0.0, step=grid_size)
y_sel = st.number_input("📍 Y", -10.0, 10.0, 0.0, step=grid_size)
punteggio_sel = calcola_punteggio(x_sel, y_sel)
st.write(f"🎯 **Punteggio stimato**: {punteggio_sel}")

# === Aggiungi freccia ===
if st.button("➕ Aggiungi Freccia"):
    if len(st.session_state.colpi) < frecce_per_volee:
        st.session_state.colpi.append((x_sel, y_sel))
        st.success(f"✅ Freccia aggiunta: ({x_sel}, {y_sel}) - Punti: {punteggio_sel}")
    else:
        st.warning("Hai già registrato tutte le frecce per questa volee.")

# === Salva volee ===
if st.button("💾 Salva volee"):
    if not st.session_state.colpi:
        st.error("❌ Nessuna freccia registrata.")
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

