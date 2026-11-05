import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
from database import inicializar_bd

inicializar_bd()

st.set_page_config(page_title="Portal de Vendedores", layout="wide")
st.title("📦 Panel Ejecutivo y Dashboard de Ingresos (Reporte Estilo Excel)")

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
    # DASHBOARD EJECUTIVO: GRÁFICA APILADA, PASTEL Y LÍNEAS
    # ==========================================================
    st.subheader("📊 Dashboard de Rendimiento y Reporte Financiero")
    conn = sqlite3.connect("mermax.db")
    
    cursor = conn.cursor()
    cursor.execute("SELECT producto, categoria, cantidad_kg, kilos_vendidos, precio_base FROM lotes WHERE vendedor = ?", (vendedor,))
    lotes_grafica = cursor.fetchall()
    
    if lotes_grafica:
        df_lotes = pd.DataFrame(lotes_grafica, columns=["Producto", "Categoría", "Cantidad Total (kg)", "Kilos Vendidos (kg)", "Precio Base"])
        df_lotes["Kilos Faltantes (kg)"] = df_lotes["Cantidad Total (kg)"] - df_lotes["Kilos Vendidos (kg)"]
        df_lotes["Ingresos ($)"] = df_lotes["Kilos Vendidos (kg)"] * df_lotes["Precio Base"]
        
        # Fila 1: Gráfica de Barras Superpuestas (Apiladas) y Gráfica de Pastel
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown("#### 📊 Inventario: Vendido vs. Faltante (Superpuesto)")
            # Preparamos el DataFrame en formato largo para Plotly con barras apiladas
            df_melted = df_lotes.melt(id_vars=["Producto"], value_vars=["Kilos Vendidos (kg)", "Kilos Faltantes (kg)"], 
                                      var_name="Estado", value_name="Kilos")
            fig_bar = px.bar(df_melted, x="Producto", y="Kilos", color="Estado", barmode="stack",
                             color_discrete_map={"Kilos Vendidos (kg)": "#2b5c8f", "Kilos Faltantes (kg)": "#d9822b"})
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col_g2:
            st.markdown("#### 🥧 Distribución de Ingresos por Categoría")
            df_cat = df_lotes.groupby("Categoría")["Ingresos ($)"].sum().reset_index()
            if not df_cat.empty and df_cat["Ingresos ($)"].sum() > 0:
                fig_pie = px.pie(df_cat, names="Categoría", values="Ingresos ($)", hole=0.3)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Aún no hay ingresos suficientes para mostrar la distribución en pastel.")

        st.markdown("---")
        
        # Fila 2: Gráfica de Tendencia Temporal (Ingresos generados por fecha con puntos y líneas)
        query_tendencia = f"""
            SELECT l.fecha, (p.kilos_solicitados * p.oferta) AS ingreso 
            FROM pujas p 
            JOIN lotes l ON p.lote_id = l.id 
            WHERE l.vendedor = '{vendedor}'
        """
        df_tendencia = pd.read_sql(query_tendencia, conn)
        
        if not df_tendencia.empty and "fecha" in df_tendencia.columns:
            df_agrupado = df_tendencia.groupby("fecha")["ingreso"].sum().reset_index()
            df_agrupado.columns = ["Fecha", "Ingresos Totales ($)"]
            df_agrupado = df_agrupado.sort_values("Fecha")
            
            st.markdown("#### 📈 Tendencia de Ingresos a lo largo del tiempo (Días / Meses)")
            fig_line = px.line(df_agrupado, x="Fecha", y="Ingresos Totales ($)", markers=True, 
                               line_shape="linear", color_discrete_sequence=["#1f77b4"])
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Registra pujas para visualizar la línea de tendencia temporal de ingresos.")
            
        # Métricas ejecutivas rápidas
        total_kilos_cat = df_lotes["Cantidad Total (kg)"].sum()
        total_vendidos = df_lotes["Kilos Vendidos (kg)"].sum()
        ganancia_estimada = df_lotes["Ingresos ($)"].sum()
        perdida_evitada = (df_lotes["Cantidad Total (kg)"] * df_lotes["Precio Base"]).sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Ingresos Totales", f"${ganancia_estimada:,.2f} USD")
        col2.metric("🛡️ Pérdidas Evitadas", f"${perdida_evitada:,.2f} USD")
        col3.metric("📦 Avance General", f"{(total_vendidos/total_kilos_cat)*100:.1f}%" if total_kilos_cat > 0 else "0%")
    else:
        st.info("Publica lotes de productos para visualizar las gráficas del dashboard ejecutivo.")
        
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
