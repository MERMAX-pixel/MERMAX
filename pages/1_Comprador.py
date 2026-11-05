import streamlit as st
import sqlite3
from datetime import datetime
from database import inicializar_bd

inicializar_bd()

st.set_page_config(page_title="Portal de Compradores", layout="wide")
st.title("🛒 Panel de Comprador - Presubasta y Chat")

st.sidebar.header("🔐 Acceso Comprador")
modo = st.sidebar.radio("Acción:", ["Iniciar Sesión", "Registrarse"], key="auth_c")
user = st.sidebar.text_input("Empresa Compradora:", key="uc")
pwd = st.sidebar.text_input("Contraseña:", type="password", key="pc")

if st.sidebar.button("Iniciar Sesión / Acceder", key="btn_auth_c"):
    conn = sqlite3.connect("mermax.db")
    cursor = conn.cursor()
    if modo == "Registrarse":
        try:
            cursor.execute("INSERT INTO usuarios (nombre, rol, password) VALUES (?, ?, ?)", (user, "comprador", pwd))
            conn.commit()
            st.sidebar.success("¡Cuenta creada con éxito! Ya puedes iniciar sesión.")
        except sqlite3.IntegrityError:
            st.sidebar.error("El usuario ya existe.")
    else:
        cursor.execute("SELECT * FROM usuarios WHERE nombre = ? AND password = ? AND rol = 'comprador'", (user, pwd))
        if cursor.fetchone():
            st.session_state.comprador_activo = user
            st.sidebar.success(f"Bienvenido, {user}")
        else:
            st.sidebar.error("Credenciales inválidas.")
    conn.close()

if "comprador_activo" in st.session_state and st.session_state.comprador_activo:
    comprador = st.session_state.comprador_activo
    st.success(f"Sesión activa como Comprador: **{comprador}**")
    
    accion = st.radio("¿Qué deseas hacer?", ["Pujar en un Lote (Porción personalizada)", "Historial y Chat Personal Ilimitado"])
    
    conn = sqlite3.connect("mermax.db")
    cursor = conn.cursor()
    
    if accion == "Pujar en un Lote (Porción personalizada)":
        cursor.execute("SELECT id, producto, categoria, cantidad_kg, kilos_vendidos, precio_base, vendedor FROM lotes")
        lotes = cursor.fetchall()
        
        st.markdown("### 📦 Lotes Disponibles en el Mercado")
        lote_opciones = {f"Lote #{l[0]} - {l[1]} ({l[2]}) | Stock: {l[3]-l[4]} kg | Base: ${l[5]}": l[0] for l in lotes}
        
        if lote_opciones:
            lote_elegido_str = st.selectbox("Selecciona un lote:", list(lote_opciones.keys()))
            lote_id = lote_opciones[lote_elegido_str]
            
            cursor.execute("SELECT producto, vendedor, cantidad_kg, kilos_vendidos FROM lotes WHERE id = ?", (lote_id,))
            info_lote = cursor.fetchone()
            stock_disponible = info_lote[2] - info_lote[3]
            
            st.info(f"ℹ️ **Stock disponible:** {stock_disponible} kg (Total: {info_lote[2]} kg)")
            
            kilos_deseados = st.number_input("¿Cuántos kilos deseas comprar?:", min_value=1.0, max_value=float(max(1.0, stock_disponible)), value=min(50.0, stock_disponible))
            nueva_oferta = st.number_input("Tu oferta por unidad ($/kg):", min_value=1.0, value=7.0)
            
            if st.button("Enviar Puja y Porción"):
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
                cursor.execute("INSERT INTO pujas (lote_id, comprador, oferta, kilos_solicitados, fecha) VALUES (?, ?, ?, ?, ?)", 
                               (lote_id, comprador, nueva_oferta, kilos_deseados, fecha_actual))
                
                cursor.execute("UPDATE lotes SET kilos_vendidos = MIN(cantidad_kg, kilos_vendidos + ?) WHERE id = ?", (kilos_deseados, lote_id))
                conn.commit()
                st.success(f"¡Puja de ${nueva_oferta} por {kilos_deseados} kg registrada!")
                
                cursor.execute("SELECT comprador FROM pujas WHERE lote_id = ? ORDER BY oferta DESC LIMIT 3", (lote_id,))
                top3_actual = [row[0] for row in cursor.fetchall()]
                
                if comprador in top3_actual:
                    st.balloons()
                    st.warning("🎉 **¡Felicidades! Estás en el TOP 3 de este lote.**")
                    st.session_state.chat_activo_vendedor = info_lote[1]
                    st.session_state.chat_activo_lote = info_lote[0]
                else:
                    st.info("Tu oferta se registró correctamente.")
            
            # Chat directo persistente si está en el Top 3 o desea comunicarse
            st.markdown("---")
            st.markdown("### 💬 Canal de Comunicación Directa con el Vendedor")
            with st.form("form_chat_persistente_comp"):
                vendedor_destino = info_lote[1]
                lote_nombre = info_lote[0]
                msj_texto = st.text_area("Escribe un mensaje o consulta al vendedor:")
                logistica_sel = st.selectbox("Logística de envío:", ["Cadena de frío", "Temperatura ambiente"])
                img_sub = st.file_uploader("Adjuntar imagen (opcional):", type=["png", "jpg", "jpeg"])
                
                enviar_chat = st.form_submit_button("Enviar Mensaje al Chat")
                if enviar_chat and msj_texto:
                    fecha_msg = datetime.now().strftime("%Y-%m-%d %H:%M")
                    cursor.execute("""
                        INSERT INTO mensajes (vendedor, remitente, lote, mensaje, logistica, imagen, respuesta, fecha)
                        VALUES (?, ?, ?, ?, ?, ?, NULL, ?)
                    """, (vendedor_destino, comprador, lote_nombre, msj_texto, logistica_sel, img_sub.name if img_sub else None, fecha_msg))
                    conn.commit()
                    st.success("📩 ¡Mensaje enviado al chat personal!")
                    st.rerun()
                    
        else:
            st.info("No hay lotes disponibles para pujar.")
            
    elif accion == "Historial y Chat Personal Ilimitado":
        st.markdown(f"### 📜 Historial de Pujas de: {comprador}")
        cursor.execute("SELECT l.producto, p.oferta, p.kilos_solicitados, p.fecha FROM pujas p JOIN lotes l ON p.lote_id = l.id WHERE p.comprador = ?", (comprador,))
        mis_pujas = cursor.fetchall()
        if mis_pujas:
            for p in mis_pujas:
                st.write(f"• [{p[3]}] Lote: **{p[0]}** — {p[2]} kg — **${p[1]} USD/kg**")
        else:
            st.info("Aún no tienes pujas.")
            
        st.markdown("---")
        st.markdown("### 💬 Historial de Chat Personal con Vendedores")
        cursor.execute("SELECT id, lote, mensaje, respuesta, vendedor, logistica, fecha FROM mensajes WHERE remitente = ? ORDER BY fecha DESC", (comprador,))
        historial_msgs = cursor.fetchall()
        
        if historial_msgs:
            for m in historial_msgs:
                st.markdown(f"📅 *{m[6]}* | **Vendedor:** {m[4]} | **Lote:** {m[1]}")
                st.info(f"🧑‍💻 **Tú:** {m[2]}\n\n🚚 *Logística:* {m[5]}")
                if m[3]:
                    st.success(f"📦 **Respuesta del Vendedor:** {m[3]}")
                else:
                    st.warning("⏳ Esperando respuesta...")
                st.markdown("---")
        else:
            st.info("📭 No hay mensajes en tu historial.")
            
    conn.close()
else:
    st.warning("Por favor, inicia sesión o regístrate en el menú lateral.")
