import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from streamlit_drawable_canvas import st_canvas
from datetime import datetime
import os
import io

st.set_page_config(layout="wide", page_title="Registro Frecce")

st.title("🎯 Registro Frecce - Allenamento Mobile")

STORICO_FILE = "storico_frecce.csv"

if not os.path.exists(STORICO_FILE):
    df_vuoto = pd.DataFrame(columns=["datetime","session_id","volee","freccia","x","y","punteggio","distanza"])
    df_vuoto.to_csv(STORICO_FILE, index=False)

# === Input
distanza = st.selectbox("📏 Seleziona la distanza", ["18","30","50","70","90"])
frecce_per_volee = st.selectbox("🏹 Numero di frecce per volee", [3,6])

session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

if "colpi" not in st.session_state:
    st.session_state.colpi = []

# === Funzioni
def calcola_punteggio(x,y):
    d = (x**2+y**2)**0.5
    for raggio,punti in zip(range(10,0,-1),range(1,11)):
        if d<=raggio: return punti
    return 0

def genera_bersaglio():
    fig, ax = plt.subplots(figsize=(6,6))
    colori = ['white','black','blue','red','yellow']
    r=10
    for c in colori:
        for _ in range(2):
            ax.add_patch(patches.Circle((0,0),r,color=c,ec='black'))
            r-=1
    ax.set_xlim(-10,10)
    ax.set_ylim(-10,10)
    ax.set_aspect('equal')
    ax.axis('off')
    buf = io.BytesIO()
    plt.savefig(buf,format="png",bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf

# === Disegna bersaglio come immagine
bersaglio_img = genera_bersaglio()

st.write("👇 Tocca sul bersaglio per aggiungere frecce")

canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=0,
    stroke_color="",
    background_image=bersaglio_img,
    update_streamlit=True,
    height=500,
    width=500,
    drawing_mode="point",
    key="canvas",
)

# Coordinate click
if canvas_result.json_data is not None:
    objects = canvas_result.json_data["objects"]
    if len(objects) > len(st.session_state.colpi):
        last = objects[-1]
        # Normalizza coordinate [-10,10]
        x_norm = (last["left"]/500)*20 -10
        y_norm = (500-last["top"])/500*20 -10
        if len(st.session_state.colpi)<frecce_per_volee:
            st.session_state.colpi.append((x_norm,y_norm))
        else:
            st.warning("Hai già registrato tutte le frecce per questa volee.")

# Mostra frecce registrate
st.write("Frecce registrate:")
st.write(st.session_state.colpi)

# Salva volee
if st.button("💾 Salva volee"):
    if not st.session_state.colpi:
        st.error("Nessuna freccia registrata")
    else:
        df_nuovo=pd.DataFrame([
            {"datetime":datetime.now().isoformat(),
             "session_id":session_id,
             "volee":1,
             "freccia":i+1,
             "x":x,"y":y,
             "punteggio":calcola_punteggio(x,y),
             "distanza":distanza}
            for i,(x,y) in enumerate(st.session_state.colpi)
        ])
        df_storico=pd.read_csv(STORICO_FILE)
        df_finale=pd.concat([df_storico,df_nuovo],ignore_index=True)
        df_finale.to_csv(STORICO_FILE,index=False)
        st.success("✅ Volee salvata!")
        st.session_state.colpi=[]
