import streamlit as st
import sqlite3
from database import inicializar_bd

# Inicializar base de datos
inicializar_bd()

st.set_page_config(page_title="Plataforma Mermax - Inicio", layout="wide")

st.title("Plataforma Integral de Presubasta de Mermas (FoodTech)")
st.markdown("Optimiza el rescate de alimentos, previene pérdidas y conecta dinámicamente a compradores con vendedores.")

st.info("Utiliza el menú lateral izquierdo para navegar entre el **Panel de Comprador** y el **Panel de Vendedor**.")

st.markdown("---")
st.subheader(" Vista Pública de Lotes Activos y Filtros por Categoría")

conn = sqlite3.connect("mermax.db")
cursor = conn.cursor()

# Filtro interactivo por categorías
cat_seleccionada = st.selectbox("Filtrar por categoría:", ["Todas", "Frutas y Verduras", "Lácteos", "Panadería", "Carnes y Embutidos", "Otros"])

if cat_seleccionada == "Todas":
    cursor.execute("SELECT id, producto, categoria, cantidad_kg, precio_base, tiempo_limite, vendedor FROM lotes")
else:
    cursor.execute("SELECT id, producto, categoria, cantidad_kg, precio_base, tiempo_limite, vendedor FROM lotes WHERE categoria = ?", (cat_seleccionada,))

lotes_db = cursor.fetchall()

if lotes_db:
    for l in lotes_db:
        st.write(f"**[Lote #{l[0]}] {l[1]}** ({l[2]}) | Cantidad: {l[3]} kg | Precio Base: ${l[4]} USD | Vendedor: {l[6]}")
        st.caption(f"⏰ Urgencia / Vigencia: {l[5]}")
        
        # Mostrar el Top 3 actual de cada lote en la vista pública
        cursor.execute("SELECT comprador, oferta FROM pujas WHERE lote_id = ? ORDER BY oferta DESC LIMIT 3", (l[0],))
        top3 = cursor.fetchall()
        if top3:
            st.write("🏆 *Top 3 pujas actuales:*")
            for i, p in enumerate(top3, 1):
                st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;{i}. {p[0]} - **${p[1]} USD**")
        else:
            st.write("🏆 *Top 3 pujas actuales:* Aún sin ofertas registradas.")
        st.markdown("---")
else:
    st.info("No hay lotes activos en esta categoría.")

conn.close()
