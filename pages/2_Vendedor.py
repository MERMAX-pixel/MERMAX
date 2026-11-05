import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from database import inicializar_bd

inicializar_bd()

st.set_page_config(page_title="Portal de Vendedores", layout="wide")
st.title("📦 Panel de Vendedor - Control, Gráficas y Chat")

st.sidebar.header("🔐 Acceso Vendedor")
modo_v = st.sidebar.radio("Acción:", ["Iniciar Sesión", "Registrarse"], key="auth_v")
user_v = st.sidebar.text_input("Empresa Vendedora:", key="uv")
pwd_v = st.sidebar.text_input("Contraseña:", type="password", key="pv")

if st.sidebar.button("Iniciar Sesión / Acceder", key="btn_auth_v"):
    conn = sqlite3.connect("mermax.db")
    cursor = conn.cursor()
    if modo_v == "Registrarse":
        try:
            cursor.execute("INSERT INTO usuarios (nombre, rol, password) VALUES (?, ?, ?)", (user_v, "vendedor", pwd_v))
            conn.commit()
            st.sidebar.success("¡Cuenta de vendedor creada con éxito!")
        except sqlite3.IntegrityError:
            st.sidebar.error("El usuario ya existe.")
    else:
        cursor.execute("SELECT * FROM usuarios WHERE nombre = ? AND password = ? AND rol = 'vendedor'", (user_v, pwd_v))
        if cursor.fetchone():
            st.session_state.vendedor_activo = user_v
            st.sidebar.success(f"Bienvenido, {user_v}")
        else:
            st.sidebar.error("Credenciales inválidas.")
    conn.close()

if "vendedor_activo" in st.session_state and st.session_state.vendedor_activo:
    vendedor = st.session_state.vendedor_activo
    st.success(f"Sesión activa como Vendedor: **{vendedor}**")
    
    with st.form("form_lote"):
        st.markdown("### ➕ Publicar Nuevo Lote de Mermas")
        prod = st.text_input("Nombre del Producto:")
        cat = st.selectbox("Categoría:", ["Frutas y Verduras", "Lácteos", "Panadería", "Carnes y Embutidos", "Otros"])
        cant = st.number_input("Cantidad total (kg):", min_value=1.0, value=100.0)
        base = st.number_input("Precio Base por unidad ($):", min_value=0.5, value=5.0)
        tiempo = st.text_input("Vigencia / Urgencia:", value="2 horas restantes")
        
        if st.form_submit_button("Publicar en el Mercado"):
            conn = sqlite3.connect("mermax.db")
            cursor = conn.cursor()
            fecha_pub = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT INTO lotes (producto, categoria, cantidad_kg, kilos_vendidos, precio_base, tiempo_limite, vendedor, fecha)
                VALUES (?, ?, ?, 0, ?, ?, ?, ?)
            """, (prod, cat, cant, base, tiempo, vendedor, fecha_pub))
            conn.commit()
            conn.close()
            st.success("¡Lote publicado correctamente!")

    st.markdown("---")
    
    # ==========================================================
    # GRÁFICA DE BARRAS: KILOS VENDIDOS VS KILOS FALTANTES
    # ==========================================================
    st.subheader("📊 Gráfica de Control: Kilos Vendidos vs. Kilos Faltantes")
    conn = sqlite3.connect("mermax.db")
    cursor = conn.cursor()
    cursor.execute("SELECT producto, cantidad_kg, kilos_vendidos FROM lotes WHERE vendedor = ?", (vendedor,))
    lotes_grafica = cursor.fetchall()
    
    if lotes_grafica:
        df_lotes = pd.DataFrame(lotes_grafica, columns=["Producto", "Cantidad Total (kg)", "Kilos Vendidos (kg)"])
        df_lotes["Kilos Faltantes (kg)"] = df_lotes["Cantidad Total (kg)"] - df_lotes["Kilos Vendidos (kg)"]
        
        # Gráfica de barras solicitada
        st.bar_chart(df_lotes.set_index("Producto")[["Kilos Vendidos (kg)", "Kilos Faltantes (kg)"]])
    else:
        st.info("Publica lotes para visualizar la gráfica de barras de inventario.")

    st.markdown("---")
    st.subheader("📈 Historial del Top 3 de Pujas por Lote")
    cursor.execute("SELECT id, producto, cantidad_kg, precio_base FROM lotes WHERE vendedor = ?", (vendedor,))
    mis_lotes = cursor.fetchall()
    
    if mis_lotes:
        for ml in mis_lotes:
            st.markdown(f"#### 📦 Lote #{ml[0]}: {ml[1]} ({ml[2]} kg) - Base: ${ml[3]} USD/kg")
            query_pujas = f"SELECT comprador, oferta, kilos_solicitados, fecha FROM pujas WHERE lote_id = {ml[0]} ORDER BY oferta DESC LIMIT 3"
            df_pujas = pd.read_sql(query_pujas, conn)
            
            if not df_pujas.empty:
                df_pujas.index = range(1, len(df_pujas) + 1)
                df_pujas.columns = ["Comprador", "Oferta ($/kg)", "Kilos Solicitados", "Fecha"]
                st.dataframe(df_pujas, use_container_width=True)
            else:
                st.info("Aún no hay pujas en este lote.")
            st.markdown("---")
    else:
        st.info("No tienes lotes publicados.")

    st.subheader("📥 Buzón de Chat y Mensajes Directos con Compradores")
    cursor.execute("SELECT id, remitente, lote, mensaje, logistica, imagen, respuesta, fecha FROM mensajes WHERE vendedor = ? ORDER BY fecha DESC", (vendedor,))
    mensajes_recibidos = cursor.fetchall()
    
    if mensajes_recibidos:
        for m in mensajes_recibidos:
            msg_id, remitente, lote_nom, texto_msj, logis, img, resp_actual, fecha_m = m
            
            st.markdown(f"📅 *{fecha_m}* | **Comprador:** {remitente} | **Lote:** *{lote_nom}*")
            st.info(f"💬 *\"{texto_msj}\"*\n\n🚚 *Logística:* {logis}")
            if img:
                st.warning(f"🖼️ **Imagen adjunta por el comprador:** {img}")
            
            if resp_actual:
                st.success(f"✅ **Tu respuesta:** {resp_actual}")
            else:
                with st.form(key=f"form_resp_vendedor_{msg_id}"):
                    texto_respuesta = st.text_area("Escribe una respuesta para este comprador:")
                    enviar_resp = st.form_submit_button("Enviar Respuesta")
                    if enviar_resp and texto_respuesta:
                        cursor.execute("UPDATE mensajes SET respuesta = ? WHERE id = ?", (texto_respuesta, msg_id))
                        conn.commit()
                        st.success("📩 ¡Respuesta enviada al chat!")
                        st.rerun()
            st.markdown("---")
    else:
        st.info("📭 No hay mensajes en el buzón.")
        
    conn.close()
else:
    st.warning("Por favor, inicia sesión o regístrate en el menú lateral.")
