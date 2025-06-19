import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile

st.set_page_config(page_title="Choque Rotacional", layout="wide")
st.title("\U0001F4A5 Simulación de Choque Rotacional entre Discos")

# --- ENTRADAS DEL USUARIO ---
st.sidebar.header("\U0001F4CC Parámetros del sistema")

mA = st.sidebar.slider("Masa disco A (kg)", 0.1, 10.0, 2.0, 0.1)
rA = st.sidebar.slider("Radio disco A (m)", 0.01, 1.0, 0.20, 0.01)
wA = st.sidebar.slider("Vel. angular disco A (rad/s)", 0.0, 500.0, 50.0, 1.0)

mB = st.sidebar.slider("Masa disco B (kg)", 0.1, 10.0, 0.4, 0.1)
rB = st.sidebar.slider("Radio disco B (m)", 0.01, 1.0, 0.10, 0.01)
wB = st.sidebar.slider("Vel. angular disco B (rad/s)", 0.0, 500.0, 200.0, 1.0)

# --- CÁLCULOS FÍSICOS ---
IA = 0.5 * mA * rA*rA
IB = 0.5 * mB * rB*rB
w_final = (IA * wA + IB * wB) / (IA + IB)
K1 = 0.5 * IA * wA*wA + 0.5 * IB * wB*wB
K2 = 0.5 * (IA + IB) * w_final*w_final
perdida = K1 - K2
perdida_pct = (perdida / K1) * 100 if K1 != 0 else 0

st.markdown("""
Esta app tiene como proposito demostrar el principio de conservación angular mediante el analisis de dos discos de embrague
""")

st.markdown("""
En la cual se puede ingresar la masa, radio de ambos discos y su velocidad angular inicial 
""")

st.title("Visualización de un Cilindro")

st.image("https://i.postimg.cc/3rjB0Nzr/embrague.png", 
         caption="Embrague - Momento Angular", 
         use_container_width=True)

# --- MOSTRAR RESULTADOS ---
st.subheader("\U0001F4CA Resultados")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Momentos de inercia:**")
    st.latex(f"I_A = \\frac{{1}}{{2}} m_A r_A^2 = {IA:.3f}\\ \text{{kgm²}}")
    st.latex(f"I_B = \\frac{{1}}{{2}} m_B r_B^2 = {IB:.3f}\\ \text{{kgm²}}")
    st.markdown("**Velocidad angular final común:**")
    st.latex(f"\\omega = \\frac{{I_A \\omega_A + I_B \\omega_B}}{{I_A + I_B}} = {w_final:.2f}\\ \text{{rad/s}}")

with col2:
    st.markdown("**Energía cinética antes del choque:**")
    st.latex(f"K_1 = \\frac{{1}}{{2}} I_A \\omega_A^2 + \\frac{{1}}{{2}} I_B \\omega_B^2 = {K1:.1f}\\ \text{{J}}")
    st.markdown("**Energía cinética después del choque:**")
    st.latex(f"K_2 = \\frac{{1}}{{2}} (I_A + I_B) \\omega^2 = {K2:.1f}\\ \text{{J}}")
    st.markdown("**Pérdida de energía cinética:**")
    st.latex(f"\\Delta K = K_1 - K_2 = {perdida:.1f}\\ \text{{J}}\\ ({perdida_pct:.1f}\\%)")

# --- ANIMACIÓN CON VELOCIDADES ANGULARES ---
fig, axs = plt.subplots(2, 2, figsize=(10, 6), gridspec_kw={'height_ratios': [2, 1]})
ax, ax_energy, ax_w = axs[0][0], axs[0][1], axs[1][0]
axs[1][1].axis('off')

ax.set_aspect('equal')
ax.set_xlim(-2, 2)
ax.set_ylim(-1.5, 1.5)
ax.axis('off')

ax_energy.set_xlim(0, 1)
ax_energy.set_ylim(0, K1 * 1.1)
ax_energy.set_xticks([])
bar1 = ax_energy.bar(0.2, K1, width=0.2, color='green', label="K Total")[0]
bar2 = ax_energy.bar(0.6, K2, width=0.2, color='red', label="K Final")[0]
ax_energy.legend()

ax_w.set_xlim(0, 5)
ax_w.set_ylim(0, max(wA, wB, w_final) * 1.2)
ax_w.set_xlabel("Tiempo (s)")
ax_w.set_ylabel("Velocidad angular (rad/s)")
line_wA, = ax_w.plot([], [], 'r-', label='ωA')
line_wB, = ax_w.plot([], [], 'k-', label='ωB')
ax_w.legend()

theta = np.linspace(0, 2 * np.pi, 100)
lineA, = ax.plot([], [], 'brown')
lineB, = ax.plot([], [], 'peru')
ptrA, = ax.plot([], [], 'r', lw=2)
ptrB, = ax.plot([], [], 'k', lw=2)
txt = ax.text(0, 1.4, "", fontsize=14, ha="center")

xA_init = -1.0
xB_init = 1.0
x_join = 0.0
t_hist, wA_hist, wB_hist = [], [], []

def init():
    lineA.set_data([], [])
    lineB.set_data([], [])
    ptrA.set_data([], [])
    ptrB.set_data([], [])
    line_wA.set_data([], [])
    line_wB.set_data([], [])
    txt.set_text("")
    return lineA, lineB, ptrA, ptrB, txt, bar1, bar2, line_wA, line_wB

def animate(i):
    t = i / 20
    t_hist.append(t)

    if t < 3:
        p = t / 3
        xA = xA_init + (x_join - xA_init) * p
        xB = xB_init + (x_join - xB_init) * p
        thetaA = wA * t
        thetaB = wB * t
        current_K = 0.5 * IA * wA**2 + 0.5 * IB * wB**2
        wA_hist.append(wA)
        wB_hist.append(wB)
        txt.set_text("ANTES DEL CHOQUE")
    else:
        xA = xB = x_join
        thetaA = thetaB = w_final * (t - 3)
        current_K = 0.5 * (IA + IB) * w_final**2
        wA_hist.append(w_final)
        wB_hist.append(w_final)
        txt.set_text("DESPUÉS DEL CHOQUE")

    xA_circ = rA * np.cos(theta + thetaA) + xA
    yA_circ = rA * np.sin(theta + thetaA)
    xB_circ = rB * np.cos(theta + thetaB) + xB
    yB_circ = rB * np.sin(theta + thetaB)
    lineA.set_data(xA_circ, yA_circ)
    lineB.set_data(xB_circ, yB_circ)
    ptrA.set_data([xA, xA + rA * np.cos(thetaA)], [0, rA * np.sin(thetaA)])
    ptrB.set_data([xB, xB + rB * np.cos(thetaB)], [0, rB * np.sin(thetaB)])

    bar1.set_height(current_K)
    bar2.set_height(K2)

    line_wA.set_data(t_hist, wA_hist)
    line_wB.set_data(t_hist, wB_hist)

    return lineA, lineB, ptrA, ptrB, txt, bar1, bar2, line_wA, line_wB

ani = animation.FuncAnimation(fig, animate, init_func=init, frames=100, interval=100, blit=True)

st.markdown("### \U0001F39E️ Animación del choque rotacional + velocidades angulares")
with tempfile.NamedTemporaryFile(delete=False, suffix=".gif") as f:
    ani.save(f.name, writer=PillowWriter(fps=20))
    st.image(f.name)

# --- GENERACIÓN DEL PDF ---
def generar_pdf():
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica", 12)
    y = 750

    def write(text):
        nonlocal y
        c.drawString(50, y, text)
        y -= 20

    write("Simulación de Choque Rotacional entre Discos")
    write("-" * 60)
    write("Parámetros ingresados:")
    write(f"Masa disco A: {mA} kg, Radio: {rA} m, Velocidad angular: {wA} rad/s")
    write(f"Masa disco B: {mB} kg, Radio: {rB} m, Velocidad angular: {wB} rad/s")
    write("")
    write("Momentos de inercia:")
    write(f"I_A = 0.5 * {mA} * {rA}² = {IA:.3f} kg·m²")
    write(f"I_B = 0.5 * {mB} * {rB}² = {IB:.3f} kg·m²")
    write("")
    write(f"Velocidad angular final: ω = {w_final:.2f} rad/s")
    write("")
    write("Energía cinética:")
    write(f"K1 (inicial): {K1:.1f} J")
    write(f"K2 (final): {K2:.1f} J")
    write(f"Pérdida de energía: {perdida:.1f} J ({perdida_pct:.1f}%)")
    write("-" * 60)
    write("Conservación del momento angular aplicada:")
    write("ω = (IA*ωA + IB*ωB) / (IA + IB)")
    write("Energías cinéticas calculadas como K = 0.5 * I * ω²")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

st.markdown("### \U0001F4C4 Exportar informe en PDF")
if st.button("Generar PDF del ejercicio"):
    pdf = generar_pdf()
    st.download_button("Descargar PDF", data=pdf, file_name="choque_rotacional.pdf", mime="application/pdf")

st.markdown("""
Para comprobar que esta aplicacíon calcule correctamente cada variable se tomo el Ejemplo 10.13 de el Libro 
Física Universitaria
YOUNG • FREEDMAN
Volumen 1
Sears Zemansky

""")

st.markdown("[Haz clic aquí para ir a Google](https://blog.espol.edu.ec/srpinarg/files/2014/05/Fisica-Universitaria-Sears-Zemansky-12ava-Edicion-Vol1.pdf)")