import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Portal de Vendedores", layout="wide")
st.title("📦 Panel de Control de Vendedores")

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
    
    # Formulario para publicar nuevo lote
    with st.form("form_lote"):
        st.markdown("### ➕ Publicar Nuevo Lote")
        prod = st.text_input("Nombre del Producto:")
        cat = st.selectbox("Categoría:", ["Frutas y Verduras", "Lácteos", "Panadería", "Carnes y Embutidos", "Otros"])
        cant = st.number_input("Cantidad (kg):", min_value=1.0, value=100.0)
        base = st.number_input("Precio Base ($):", min_value=0.5, value=5.0)
        tiempo = st.text_input("Vigencia / Urgencia:", value="2 horas restantes (Urgente)")
        
        if st.form_submit_button("Publicar en el Mercado"):
            conn = sqlite3.connect("mermax.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO lotes (producto, categoria, cantidad_kg, precio_base, tiempo_limite, vendedor)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (prod, cat, cant, base, tiempo, vendedor))
            conn.commit()
            conn.close()
            st.success("¡Lote publicado correctamente!")

    st.markdown("---")
    st.subheader("📈 Historial de Pujas en tus Lotes")
    conn = sqlite3.connect("mermax.db")
    
    # Obtener lotes de este vendedor
    cursor = conn.cursor()
    cursor.execute("SELECT id, producto, cantidad_kg, precio_base FROM lotes WHERE vendedor = ?", (vendedor,))
    mis_lotes = cursor.fetchall()
    
    if mis_lotes:
        for ml in mis_lotes:
            st.markdown(f"#### 📦 Lote #{ml[0]}: {ml[1]} ({ml[2]} kg) - Base: ${ml[3]} USD")
            query_pujas = f"SELECT comprador, oferta FROM pujas WHERE lote_id = {ml[0]} ORDER BY oferta DESC"
            df_pujas = pd.read_sql(query_pujas, conn)
            
            if not df_pujas.empty:
                df_pujas.index = range(1, len(df_pujas) + 1)
                df_pujas.columns = ["Comprador / Empresa", "Oferta por Unidad ($)"]
                st.dataframe(df_pujas, use_container_width=True)
            else:
                st.info("Aún no hay pujas registradas en este lote.")
            st.markdown("---")
    else:
        st.info("No tienes lotes publicados todavía.")

    st.subheader("📥 Buzón de Mensajes Directos y Respuestas")
    cursor.execute("SELECT id, remitente, lote, mensaje, logistica, imagen, respuesta FROM mensajes WHERE vendedor = ?", (vendedor,))
    mensajes_recibidos = cursor.fetchall()
    
    if mensajes_recibidos:
        for m in mensajes_recibidos:
            msg_id, remitente, lote_nom, texto_msj, logis, img, resp_actual = m
            img_info = f" | 🖼️ Imagen: {img}" if img else ""
            
            st.markdown(f"**De:** {remitente} | **Lote:** *{lote_nom}*{img_info}")
            st.info(f"💬 *\"{texto_msj}\"*\n\n🚚 *Logística:* {logis}")
            
            if resp_actual:
                st.success(f"✅ **Tu respuesta enviada:** {resp_actual}")
            else:
                with st.form(key=f"form_resp_{msg_id}"):
                    texto_respuesta = st.text_area("Escribe una respuesta para este comprador:")
                    enviar_resp = st.form_submit_button("Enviar Respuesta")
                    if enviar_resp:
                        cursor.execute("UPDATE mensajes SET respuesta = ? WHERE id = ?", (texto_respuesta, msg_id))
                        conn.commit()
                        st.success("📩 ¡Respuesta enviada con éxito!")
                        st.rerun()
            st.markdown("---")
    else:
        st.info("📭 No tienes mensajes directos de compradores.")
        
    conn.close()
else:
    st.warning("Por favor, inicia sesión o regístrate en el menú lateral para gestionar tus productos.")
