import streamlit as st
import sqlite3
from database import inicializar_bd

inicializar_bd()

st.set_page_config(page_title="Portal de Compradores", layout="wide")
st.title("🛒 Panel de Comprador - Presubasta y Pujas")

# Autenticación de Comprador en barra lateral
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
    
    accion = st.radio("¿Qué deseas hacer?", ["Pujar en un Lote (Porción personalizada)", "Mi Historial y Buzón de Mensajes"])
    
    conn = sqlite3.connect("mermax.db")
    cursor = conn.cursor()
    
    if accion == "Pujar en un Lote (Porción personalizada)":
        cursor.execute("SELECT id, producto, categoria, cantidad_kg, kilos_vendidos, precio_base, vendedor FROM lotes")
        lotes = cursor.fetchall()
        
        st.markdown("### 📦 Lotes Disponibles en el Mercado")
        lote_opciones = {f"Lote #{l[0]} - {l[1]} ({l[2]}) | Stock total: {l[3]} kg | Base: ${l[5]}": l[0] for l in lotes}
        
        if lote_opciones:
            lote_elegido_str = st.selectbox("Selecciona un lote:", list(lote_opciones.keys()))
            lote_id = lote_opciones[lote_elegido_str]
            
            cursor.execute("SELECT producto, vendedor, cantidad_kg, kilos_vendidos FROM lotes WHERE id = ?", (lote_id,))
            info_lote = cursor.fetchone()
            stock_disponible = info_lote[2] - info_lote[3]
            
            st.info(f"ℹ️ **Stock disponible para rescate:** {stock_disponible} kg (de un total de {info_lote[2]} kg)")
            
            # Selección de porción particular de kilos
            kilos_deseados = st.number_input("¿Cuántos kilos deseas comprar/subastar de este lote?:", min_value=1.0, max_value=float(max(1.0, stock_disponible)), value=min(50.0, stock_disponible))
            nueva_oferta = st.number_input("Tu oferta por unidad ($/kg):", min_value=1.0, value=7.0)
            
            if st.button("Enviar Puja y Porción"):
                cursor.execute("INSERT INTO pujas (lote_id, comprador, oferta, kilos_solicitados) VALUES (?, ?, ?, ?)", (lote_id, comprador, nueva_oferta, kilos_deseados))
                
                # Actualizar kilos vendidos en el lote
                cursor.execute("UPDATE lotes SET kilos_vendidos = MIN(cantidad_kg, kilos_vendidos + ?) WHERE id = ?", (kilos_deseados, lote_id))
                conn.commit()
                st.success(f"¡Puja de ${nueva_oferta} por {kilos_deseados} kg registrada con éxito!")
                
                cursor.execute("SELECT comprador FROM pujas WHERE lote_id = ? ORDER BY oferta DESC LIMIT 3", (lote_id,))
                top3_actual = [row[0] for row in cursor.fetchall()]
                
                if comprador in top3_actual:
                    st.balloons()
                    st.warning("🎉 **¡Felicidades! Estás en el TOP 3 de este lote.**")
                    st.session_state.ultima_oferta_comprador = {
                        "lote_id": lote_id,
                        "producto": info_lote[0],
                        "vendedor": info_lote[1]
                    }
                else:
                    st.info("Tu oferta se registró correctamente.")
            
            if "ultima_oferta_comprador" in st.session_state:
                uo = st.session_state.ultima_oferta_comprador
                st.markdown("---")
                desea_mensaje = st.radio("¿Deseas enviar un mensaje directo al vendedor sobre tu porción?", ["No", "Sí"], key="radio_msg_comp")
                
                if desea_mensaje == "Sí":
                    with st.form("form_mensaje_comprador"):
                        msg = st.text_area("Escribe tu mensaje o requerimiento logístico:")
                        logistica = st.selectbox("Logística de envío:", ["Cadena de frío (Protección ecológica)", "Temperatura ambiente"])
                        imagen_subida = st.file_uploader("Adjuntar una imagen opcional:", type=["png", "jpg", "jpeg"])
                        
                        btn_enviar_chat = st.form_submit_button("Enviar Mensaje al Vendedor")
                        if btn_enviar_chat:
                            cursor.execute("""
                                INSERT INTO mensajes (vendedor, remitente, lote, mensaje, logistica, imagen, respuesta)
                                VALUES (?, ?, ?, ?, ?, ?, NULL)
                            """, (uo["vendedor"], comprador, uo["producto"], msg, logistica, imagen_subida.name if imagen_subida else None))
                            conn.commit()
                            st.success("📩 ¡Mensaje enviado con éxito al vendedor!")
        else:
            st.info("No hay lotes disponibles para pujar.")
            
    elif accion == "Mi Historial y Buzón de Mensajes":
        st.markdown(f"### 📜 Historial de Pujas y Porciones de: {comprador}")
        cursor.execute("SELECT l.producto, p.oferta, p.kilos_solicitados FROM pujas p JOIN lotes l ON p.lote_id = l.id WHERE p.comprador = ?", (comprador,))
        mis_pujas = cursor.fetchall()
        if mis_pujas:
            for p in mis_pujas:
                st.write(f"• Lote: **{p[0]}** — Porción solicitada: **{p[2]} kg** — Oferta: **${p[1]} USD/kg**")
        else:
            st.info("Aún no tienes pujas registradas.")
            
        st.markdown("---")
        st.markdown("### 💬 Buzón de Mensajes y Respuestas del Vendedor")
        cursor.execute("SELECT id, lote, mensaje, respuesta, vendedor, logistica FROM mensajes WHERE remitente = ?", (comprador,))
        mensajes_mios = cursor.fetchall()
        if mensajes_mios:
            for m in mensajes_mios:
                st.write(f"📤 **Para el vendedor ({m[4]}) sobre el lote '{m[1]}':**")
                st.info(f"💬 *\"{m[2]}\"*\n\n🚚 *Logística:* {m[5]}")
                
                if m[3]:
                    st.success(f"📥 **Respuesta oficial del Vendedor:** {m[3]}")
                else:
                    st.warning("⏳ Esperando respuesta del vendedor...")
                st.markdown("---")
        else:
            st.info("📭 No has enviado mensajes directos todavía.")
            
    conn.close()
else:
    st.warning("Por favor, inicia sesión o regístrate en el menú lateral para acceder a tu panel.")
