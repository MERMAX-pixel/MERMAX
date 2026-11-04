import streamlit as st
import sqlite3
from database import inicializar_bd, registrar_usuario, verificar_usuario

# Inicializar la base de datos SQLite al arrancar
inicializar_bd()

st.set_page_config(page_title="Plataforma Mermax - Inicio", layout="wide")

st.title("🌱 Plataforma Integral de Presubasta de Mermas (FoodTech)")
st.markdown("Optimiza el rescate de alimentos, previene pérdidas y conecta dinámicamente a compradores con vendedores.")

st.info("ℹ️ Utiliza el menú lateral izquierdo para navegar entre el **Panel de Comprador** y el **Panel de Vendedor** una vez que inicies sesión.")

# Mostrar lotes públicos activos desde SQLite
st.subheader("👁️ Vista Pública de Lotes Activos en el Mercado")
conn = sqlite3.connect("mermax.db")
cursor = conn.cursor()
cursor.execute("SELECT id, producto, categoria, cantidad_kg, precio_base, tiempo_limite, vendedor FROM lotes")
lotes_db = cursor.fetchall()
conn.close()

if lotes_db:
    for l in lotes_db:
        st.write(f"**[Lote #{l[0]}] {l[1]}** ({l[2]}) | Cantidad: {l[3]} kg | Precio Base: ${l[4]} | Vendedor: {l[6]}")
        st.caption(f"⏰ {l[5]}")
        st.markdown("---")
else:
    st.info("Aún no hay lotes registrados en la base de datos.")