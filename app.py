import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# === Impostazioni ===
GRID_SIZE = 1000
SQUARE_SIZE = 1  # Ogni quadrato sarà 1x1 nel sistema logico
CENTER = GRID_SIZE // 2
MAX_SCORE = 10
RING_WIDTH = GRID_SIZE / (2 * MAX_SCORE)

# === Funzione per calcolare il punteggio ===
def calcola_punteggio(x, y):
    dx = x - CENTER
    dy = y - CENTER
    distanza = np.sqrt(dx**2 + dy**2)
    punteggio = MAX_SCORE - int(distanza // RING_WIDTH)
    return max(punteggio, 0)

# === Titolo ===
st.title("🎯 Seleziona il punto sul bersaglio")

# === Crea immagine del bersaglio ===
fig, ax = plt.subplots(figsize=(6, 6))

# Colori per i cerchi concentrici (dal centro verso l'esterno)
colori = ['gold', 'red', 'blue', 'black', 'white']
for i in range(MAX_SCORE):
    r = (MAX_SCORE - i) * RING_WIDTH
    colore = colori[i // 2]  # 2 cerchi per colore
    cerchio = plt.Circle((CENTER, CENTER), r, color=colore, ec='gray')
    ax.add_patch(cerchio)

# Impostazioni assi
ax.set_xlim(0, GRID_SIZE)
ax.set_ylim(0, GRID_SIZE)
ax.set_aspect('equal')
ax.axis('off')

# === Mostra bersaglio e cattura clic ===
click = st.pyplot(fig, clear_figure=False)
st.write("⬇️ Inserisci le coordinate (simulate):")

# Per ora, coordinate manuali simulate
x = st.slider("X", 0, GRID_SIZE-1, CENTER)
y = st.slider("Y", 0, GRID_SIZE-1, CENTER)

if st.button("📍 Registra colpo"):
    punteggio = calcola_punteggio(x, y)
    st.success(f"Freccia registrata a ({x}, {y}) con punteggio: {punteggio}")
