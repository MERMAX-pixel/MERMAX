import streamlit as st
import sqlite3
from datetime import datetime
from database import inicializar_bd

inicializar_bd()

st.set_page_config(page_title="Portal de Compradores", layout="wide")
st.title("🛒 Panel de Comprador - Presubasta, Pujas y Chat")

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
    
    accion = st.radio("¿Qué deseas hacer?", ["Pujar en un Lote y Ver Top 3", "Mi Historial y Chat Ilimitado con Vendedores"])
    
    conn = sqlite3.connect("mermax.db")
    cursor = conn.cursor()
    
    if accion == "Pujar en un Lote y Ver Top 3":
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
            
            # Mostrar la tabla del Top 3 de ofertas debajo del producto
            cursor.execute("SELECT comprador, oferta, kilos_solicitados, fecha FROM pujas WHERE lote_id = ? ORDER BY oferta DESC LIMIT 3", (lote_id,))
            top3 = cursor.fetchall()
            st.markdown("#### 🏆 Top 3 Pujas Actuales para este Lote")
            if top3:
                for idx, t in enumerate(top3, 1):
                    st.write(f"**{idx}.** Empresa: `{t[0]}` | Oferta: **${t[1]} USD/kg** | Cantidad: {t[2]} kg *(Fecha: {t[3]})*")
            else:
                st.write("Aún no hay ofertas registradas en este lote. ¡Sé el primero!")
            
            st.markdown("---")
            
            # Validación segura corregida para evitar StreamlitValueBelowMinError
            max_val = float(max(1.0, stock_disponible))
            val_inicial = float(min(50.0, max_val)) if max_val >= 1.0 else 1.0
            
            kilos_deseados = st.number_input(
                "¿Cuántos kilos deseas comprar de este lote?:", 
                min_value=1.0, 
                max_value=max_val, 
                value=val_inicial
            )
            nueva_oferta = st.number_input("Tu oferta por unidad ($/kg):", min_value=1.0, value=7.0)
            
            if st.button("Enviar Puja"):
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
                cursor.execute("INSERT INTO pujas (lote_id, comprador, oferta, kilos_solicitados, fecha) VALUES (?, ?, ?, ?, ?)", 
                               (lote_id, comprador, nueva_oferta, kilos_deseados, fecha_actual))
                cursor.execute("UPDATE lotes SET kilos_vendidos = MIN(cantidad_kg, kilos_vendidos + ?) WHERE id = ?", (kilos_deseados, lote_id))
                conn.commit()
                st.success("¡Puja registrada con éxito!")
                st.session_state.puja_realizada = {
                    "vendedor": info_lote[1],
                    "producto": info_lote[0]
                }
                st.rerun()
            
            if "puja_realizada" in st.session_state:
                st.markdown("---")
                st.success("✅ Tu oferta ha sido procesada correctamente.")
                desea_enviar = st.radio("¿Deseas enviar un mensaje o imagen directa al vendedor sobre esta puja?", ["No", "Sí"], key="radio_opcion_msg")
                
                if desea_enviar == "Sí":
                    with st.form("form_chat_comprador_activo"):
                        pr = st.session_state.puja_realizada
                        msg_texto = st.text_area("Escribe tu mensaje o requerimiento:")
                        logistica_opc = st.selectbox("Logística:", ["Cadena de frío", "Temperatura ambiente"])
                        img_adjunta = st.file_uploader("Adjuntar imagen:", type=["png", "jpg", "jpeg"])
                        
                        btn_enviar_msj = st.form_submit_button("Enviar Mensaje al Vendedor")
                        if btn_enviar_msj:
                            fecha_m = datetime.now().strftime("%Y-%m-%d %H:%M")
                            cursor.execute("""
                                INSERT INTO mensajes (vendedor, remitente, lote, mensaje, logistica, imagen, respuesta, fecha)
                                VALUES (?, ?, ?, ?, ?, ?, NULL, ?)
                            """, (pr["vendedor"], comprador, pr["producto"], msg_texto, logistica_opc, img_adjunta.name if img_adjunta else None, fecha_m))
                            conn.commit()
                            st.success("📩 ¡Mensaje enviado con éxito al vendedor!")
                            del st.session_state.puja_realizada
                            st.rerun()
        else:
            st.info("No hay lotes activos en este momento.")
            
    elif accion == "Mi Historial y Chat Ilimitado con Vendedores":
        st.markdown(f"### 💬 Historial de Chat y Mensajes (Comprador: {comprador})")
        cursor.execute("SELECT id, lote, mensaje, respuesta, vendedor, logistica, imagen, fecha FROM mensajes WHERE remitente = ? ORDER BY fecha DESC", (comprador,))
        historial = cursor.fetchall()
        
        if historial:
            for h in historial:
                st.markdown(f"📅 *{h[7]}* | **Vendedor:** {h[4]} | **Lote:** {h[1]}")
                st.info(f"🧑‍💻 **Tú:** {h[2]}\n\n🚚 *Logística:* {h[5]}")
                if h[6]:
                    st.warning(f"🖼️ **Imagen adjunta:** {h[6]}")
                if h[3]:
                    st.success(f"📦 **Respuesta del Vendedor:** {h[3]}")
                else:
                    st.warning("⏳ Esperando respuesta...")
                st.markdown("---")
        else:
            st.info("📭 No tienes mensajes en tu chat personal.")
            
    conn.close()
else:
    st.warning("Por favor, inicia sesión o regístrate en el menú lateral.")
