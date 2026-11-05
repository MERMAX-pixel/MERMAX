import streamlit as st
import sqlite3
import pandas as pd
from database import inicializar_bd

inicializar_bd()

st.set_page_config(page_title="Portal de Vendedores", layout="wide")
st.title("📦 Panel de Control Ejecutivo y Métricas del Vendedor")

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
        st.markdown("### ➕ Publicar Nuevo Lote de Mermas")
        prod = st.text_input("Nombre del Producto:")
        cat = st.selectbox("Categoría:", ["Frutas y Verduras", "Lácteos", "Panadería", "Carnes y Embutidos", "Otros"])
        cant = st.number_input("Cantidad total (kg):", min_value=1.0, value=100.0)
        base = st.number_input("Precio Base por unidad ($):", min_value=0.5, value=5.0)
        tiempo = st.text_input("Vigencia / Urgencia:", value="2 horas restantes (Urgente)")
        
        if st.form_submit_button("Publicar en el Mercado"):
            conn = sqlite3.connect("mermax.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO lotes (producto, categoria, cantidad_kg, kilos_vendidos, precio_base, tiempo_limite, vendedor)
                VALUES (?, ?, ?, 0, ?, ?, ?)
            """, (prod, cat, cant, base, tiempo, vendedor))
            conn.commit()
            conn.close()
            st.success("¡Lote publicado correctamente en la plataforma!")

    st.markdown("---")
    
    # ==========================================
    # DASHBOARD EJECUTIVO Y GRÁFICAS ESTILO EXCEL
    # ==========================================
    st.subheader("📊 Dashboard de Rendimiento e Impacto (Estilo Ejecutivo)")
    conn = sqlite3.connect("mermax.db")
    cursor = conn.cursor()
    cursor.execute("SELECT producto, categoria, cantidad_kg, kilos_vendidos, precio_base FROM lotes WHERE vendedor = ?", (vendedor,))
    datos_grafica = cursor.fetchall()
    
    if datos_grafica:
        df_lotes = pd.DataFrame(datos_grafica, columns=["Producto", "Categoría", "Cantidad Total (kg)", "Kilos Vendidos (kg)", "Precio Base"])
        df_lotes["Kilos Faltantes (kg)"] = df_lotes["Cantidad Total (kg)"] - df_lotes["Kilos Vendidos (kg)"]
        df_lotes["Ingresos Estimados ($)"] = df_lotes["Kilos Vendidos (kg)"] * df_lotes["Precio Base"]
        
        # Gráfica de barras de unidades / kilos comercializados
        st.markdown("#### 📊 Unidades y Kilos Comercializados por Producto")
        df_kilos = df_lotes.set_index("Producto")[["Kilos Vendidos (kg)", "Kilos Faltantes (kg)"]]
        st.bar_chart(df_kilos)
        
        # Gráfica de líneas de tendencia de ingresos
        st.markdown("#### 📈 Tendencia de Ingresos por Lote")
        df_ingresos = df_lotes.set_index("Producto"]["Ingresos Estimados ($)"]
        st.line_chart(df_ingresos)
        
        total_kilos_cat = df_lotes["Cantidad Total (kg)"].sum()
        total_vendidos = df_lotes["Kilos Vendidos (kg)"].sum()
        ganancia_estimada = df_lotes["Ingresos Estimados ($)"].sum()
        perdida_evitada = (df_lotes["Cantidad Total (kg)"] * df_lotes["Precio Base"]).sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Ingresos Totales", f"${ganancia_estimada:,.2f} USD")
        col2.metric("🛡️ Pérdidas Evitadas", f"${perdida_evitada:,.2f} USD")
        col3.metric("📦 Avance de Venta", f"{(total_vendidos/total_kilos_cat)*100:.1f}% completado" if total_kilos_cat > 0 else "0%")
    else:
        st.info("Publica lotes de productos para visualizar las gráficas ejecutivas del dashboard.")
        
    st.markdown("---")
    st.subheader("📈 Historial de Pujas y Porciones Solicitadas")
    
    cursor.execute("SELECT id, producto, cantidad_kg, precio_base FROM lotes WHERE vendedor = ?", (vendedor,))
    mis_lotes = cursor.fetchall()
    
    if mis_lotes:
        for ml in mis_lotes:
            st.markdown(f"#### 📦 Lote #{ml[0]}: {ml[1]} ({ml[2]} kg) - Base: ${ml[3]} USD/kg")
            query_pujas = f"SELECT comprador, oferta, kilos_solicitados FROM pujas WHERE lote_id = {ml[0]} ORDER BY oferta DESC"
            df_pujas = pd.read_sql(query_pujas, conn)
            
            if not df_pujas.empty:
                df_pujas.index = range(1, len(df_pujas) + 1)
                df_pujas.columns = ["Comprador / Empresa", "Oferta ($/kg)", "Kilos Solicitados"]
                st.dataframe(df_pujas, use_container_width=True)
            else:
                st.info("Aún no hay pujas registradas en este lote.")
            st.markdown("---")
    else:
        st.info("No tienes lotes publicados todavía.")

    st.subheader("📥 Buzón de Mensajes y Enviar Respuesta al Comprador")
    cursor.execute("SELECT id, remitente, lote, mensaje, logistica, imagen, respuesta FROM mensajes WHERE vendedor = ?", (vendedor,))
    mensajes_recibidos = cursor.fetchall()
    
    if mensajes_recibidos:
        for m in mensajes_recibidos:
            msg_id, remitente, lote_nom, texto_msj, logis, img, resp_actual = m
            img_info = f" | 🖼️ Imagen: {img}" if img else ""
            
            st.markdown(f"**De:** {remitente} | **Lote:** *{lote_nom}*{img_info}")
            st.info(f"💬 *\"{texto_msj}\"*\n\n🚚 *Logística seleccionada:* {logis}")
            
            if resp_actual:
                st.success(f"✅ **Tu respuesta enviada:** {resp_actual}")
            else:
                with st.form(key=f"form_resp_{msg_id}"):
                    texto_respuesta = st.text_area("Escribe una respuesta para este comprador:")
                    enviar_resp = st.form_submit_button("Enviar Respuesta")
                    if enviar_resp:
                        cursor.execute("UPDATE mensajes SET respuesta = ? WHERE id = ?", (texto_respuesta, msg_id))
                        conn.commit()
                        st.success("📩 ¡Respuesta enviada con éxito al comprador!")
                        st.rerun()
            st.markdown("---")
    else:
        st.info("📭 No hay mensajes pendientes de compradores.")
        
    conn.close()
else:
    st.warning("Por favor, inicia sesión o regístrate en el menú lateral para gestionar tus productos.")
