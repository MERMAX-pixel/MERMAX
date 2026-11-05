import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from database import inicializar_bd

inicializar_bd()

st.set_page_config(page_title="Portal de Vendedores", layout="wide")
st.title("📦 Panel Ejecutivo y Gráficas de Tendencia Temporal")

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
    # GRÁFICA DE TENDENCIA DE INGRESOS POR DÍA / TIEMPO
    # ==========================================================
    st.subheader("📊 Dashboard Financiero y Tendencia Temporal")
    conn = sqlite3.connect("mermax.db")
    
    # Consultar lotes con sus pujas y fechas para graficar evolución por días/meses
    query_tendencia = f"""
        SELECT l.fecha, (p.kilos_solicitados * p.oferta) AS ingreso 
        FROM pujas p 
        JOIN lotes l ON p.lote_id = l.id 
        WHERE l.vendedor = '{vendedor}'
    """
    df_tendencia = pd.read_sql(query_tendencia, conn)
    
    if not df_tendencia.empty and "fecha" in df_tendencia.columns:
        # Agrupar ingresos por fecha (días/meses) para ver la tendencia temporal real
        df_agrupado = df_tendencia.groupby("fecha")["ingreso"].sum().reset_index()
        df_agrupado.columns = ["Fecha", "Ingresos Totales ($)"]
        df_agrupado = df_agrupado.sort_values("Fecha")
        
        st.markdown("#### 📈 Tendencia de Ingresos a lo largo del tiempo (Días / Meses)")
        st.line_chart(df_agrupado.set_index("Fecha"))
    else:
        st.info("Aún no hay suficientes transacciones para graficar la tendencia temporal.")
        
    # Métricas generales
    cursor = conn.cursor()
    cursor.execute("SELECT cantidad_kg, kilos_vendidos, precio_base FROM lotes WHERE vendedor = ?", (vendedor,))
    lotes_resumen = cursor.fetchall()
    if lotes_resumen:
        df_res = pd.DataFrame(lotes_resumen, columns=["Total", "Vendidos", "Base"])
        ingresos_totales = (df_res["Vendidos"] * df_res["Base"]).sum()
        perdidas_evitadas = (df_res["Total"] * df_res["Base"]).sum()
        
        col1, col2 = st.columns(2)
        col1.metric("💰 Ingresos Totales Generados", f"${ingresos_totales:,.2f} USD")
        col2.metric("🛡️ Pérdidas Totales Evitadas", f"${perdidas_evitadas:,.2f} USD")
        
    st.markdown("---")
    st.subheader("📥 Buzón de Chat Personal Ilimitado con Compradores")
    cursor.execute("SELECT id, remitente, lote, mensaje, logistica, imagen, respuesta, fecha FROM mensajes WHERE vendedor = ? ORDER BY fecha DESC", (vendedor,))
    mensajes_recibidos = cursor.fetchall()
    
    if mensajes_recibidos:
        for m in mensajes_recibidos:
            msg_id, remitente, lote_nom, texto_msj, logis, img, resp_actual, fecha_m = m
            img_info = f" | 🖼️ Imagen: {img}" if img else ""
            
            st.markdown(f"📅 *{fecha_m}* | **Comprador:** {remitente} | **Lote:** *{lote_nom}*{img_info}")
            st.info(f"💬 *\"{texto_msj}\"*\n\n🚚 *Logística:* {logis}")
            
            if resp_actual:
                st.success(f"✅ **Tu respuesta:** {resp_actual}")
            else:
                with st.form(key=f"form_resp_vendedor_{msg_id}"):
                    texto_respuesta = st.text_area("Responder al comprador:", key=f"txt_resp_{msg_id}")
                    enviar_resp = st.form_submit_button("Enviar Respuesta al Chat")
                    if enviar_resp and texto_respuesta:
                        cursor.execute("UPDATE mensajes SET respuesta = ? WHERE id = ?", (texto_respuesta, msg_id))
                        conn.commit()
                        st.success("📩 ¡Respuesta enviada con éxito al chat!")
                        st.rerun()
            st.markdown("---")
    else:
        st.info("📭 No hay mensajes en el buzón.")
        
    conn.close()
else:
    st.warning("Por favor, inicia sesión o regístrate en el menú lateral.")
