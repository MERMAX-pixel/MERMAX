import streamlit as st
import pandas as pd

# Configuración de la página web
st.set_page_config(page_title="Plataforma de Presubasta de Mermas", layout="wide")

st.title("🌱 Plataforma Integral de Presubasta de Mermas (FoodTech)")
st.markdown("Optimiza el rescate de alimentos, previene pérdidas y conecta dinámicamente a compradores con vendedores.")

# 1. Base de datos global persistente en la sesión
if "lotes" not in st.session_state:
    st.session_state.lotes = [
        {
            "id": 1, 
            "producto": "Tomate fresco", 
            "categoria": "Frutas y Verduras", 
            "cantidad_kg": 150, 
            "precio_base": 5.00, 
            "tiempo_limite": "2 horas restantes (¡Cierre inminente!)",
            "vendedor": "Agro Alimentos S.A.",
            "mejores_ofertas": [
                {"comprador": "Supermercado Express", "oferta": 7.50},
                {"comprador": "Frutería Local", "oferta": 6.80}
            ],
            "historial_pujas": [
                {"comprador": "Frutería Local", "oferta": 6.80},
                {"comprador": "Supermercado Express", "oferta": 7.50}
            ]
        }
    ]

if "usuarios_db" not in st.session_state:
    st.session_state.usuarios_db = {
        "Supermercado Express": {
            "rol": "comprador",
            "password": "123",
            "historial": ["Tomate fresco (150kg) - $7.50/kg"],
            "mensajes_enviados": []
        },
        "Agro Alimentos S.A.": {
            "rol": "vendedor",
            "password": "123"
        }
    }

if "mensajes_vendedor" not in st.session_state:
    st.session_state.mensajes_vendedor = [
        {
            "id_msg": 1,
            "vendedor": "Agro Alimentos S.A.", 
            "remitente": "Supermercado Express", 
            "lote": "Tomate fresco", 
            "mensaje": "Interesado en cadena de frío para entrega.", 
            "logistica": "Cadena de frío (Protección ecológica)", 
            "imagen": None,
            "respuesta": "Entendido, coordinaremos la cadena de frío."
        }
    ]

# Estado para controlar la última oferta realizada y mantener estable la interfaz del mensaje
if "ultima_oferta_activa" not in st.session_state:
    st.session_state.ultima_oferta_activa = None

# Menú lateral para selección de perfiles y autenticación
st.sidebar.header("🔐 Portal de Acceso y Autenticación")
rol = st.sidebar.selectbox("Selecciona tu rol:", ["Invitado (Solo lectura)", "Comprador", "Vendedor"])

# ==========================================
# 1. VISTA DE INVITADO
# ==========================================
if rol == "Invitado (Solo lectura)":
    st.subheader("👁️ Vista Pública de Lotes Activos")
    for l in st.session_state.lotes:
        st.write(f"**[Lote #{l['id']}] {l['producto']}** ({l['categoria']}) | Cantidad: {l['cantidad_kg']} kg | Vendedor: {l['vendedor']}")
        st.caption(f"⏰ {l['tiempo_limite']}")
        st.write("🏆 *Top 3 pujas actuales:*")
        if l['mejores_ofertas']:
            for i, p in enumerate(l['mejores_ofertas'], 1):
                st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;{i}. {p['comprador']} - ${p['oferta']} USD")
        else:
            st.write("&nbsp;&nbsp;&nbsp;&nbsp;Aún sin ofertas registradas.")
        st.markdown("---")

# ==========================================
# 2. VISTA DE COMPRADOR
# ==========================================
elif rol == "Comprador":
    st.subheader("🛒 Panel de Comprador y Presubasta")
    
    modo_auth = st.radio("¿Tienes una cuenta o deseas registrarte?", ["Iniciar Sesión", "Registrar Nueva Cuenta"], key="auth_comp_radio")
    nombre_comprador_input = st.text_input("🔑 Nombre de tu empresa compradora:", key="input_user_comp")
    password_comprador_input = st.text_input("🔒 Contraseña personal:", type="password", key="input_pass_comp")
    
    btn_login = st.button("Iniciar Sesión / Acceder", key="btn_login_comp")
    
    if "comprador_logueado" not in st.session_state:
        st.session_state.comprador_logueado = None

    if btn_login:
        if modo_auth == "Iniciar Sesión":
            if nombre_comprador_input in st.session_state.usuarios_db:
                if st.session_state.usuarios_db[nombre_comprador_input]["password"] == password_comprador_input:
                    st.session_state.comprador_logueado = nombre_comprador_input
                    st.success(f"👋 ¡Bienvenido de nuevo, {nombre_comprador_input}!")
                else:
                    st.error("❌ Contraseña incorrecta.")
            else:
                st.warning("⚠️ La cuenta no existe. Selecciona 'Registrar Nueva Cuenta'.")
        
        elif modo_auth == "Registrar Nueva Cuenta":
            if nombre_comprador_input in st.session_state.usuarios_db:
                st.error("❌ Este nombre de usuario ya está registrado. Inicia sesión.")
            else:
                st.session_state.usuarios_db[nombre_comprador_input] = {
                    "rol": "comprador",
                    "password": password_comprador_input,
                    "historial": [],
                    "mensajes_enviados": []
                }
                st.session_state.comprador_logueado = nombre_comprador_input
                st.success(f"✨ ¡Cuenta creada e iniciada con éxito para {nombre_comprador_input}!")

    if st.session_state.comprador_logueado:
        nombre_comprador = st.session_state.comprador_logueado
        st.info(f"Sesión activa como: **{nombre_comprador}**")
        
        accion = st.radio("¿Qué deseas hacer?", ["Pujar en un Lote", "Ver mi Historial y Mensajes"], key="accion_comp")
        
        if accion == "Pujar en un Lote":
            st.markdown("---")
            st.markdown("### 📦 Lotes disponibles para presubasta")
            for l in st.session_state.lotes:
                st.write(f"**Lote ID {l['id']}: {l['producto']}** ({l['categoria']}) | Cantidad: {l['cantidad_kg']} kg | Vendedor: {l['vendedor']} | Base: ${l['precio_base']}")
                st.write("🏆 *Top 3 pujas actuales:*")
                if l['mejores_ofertas']:
                    for i, p in enumerate(l['mejores_ofertas'], 1):
                        st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;{i}. {p['comprador']} - ${p['oferta']} USD")
                else:
                    st.write("&nbsp;&nbsp;&nbsp;&nbsp;Sé el primero en ofertar por este lote.")
                st.markdown("---")
            
            lote_id = st.selectbox("Selecciona el ID del Lote por el que deseas ofertar:", [l['id'] for l in st.session_state.lotes], key="sel_lote_id")
            nueva_oferta = st.number_input("Tu oferta por unidad ($):", min_value=1.0, value=7.0, key="num_oferta_val")
            
            if st.button("Enviar Oferta", key="btn_enviar_oferta"):
                lote_sel = next(l for l in st.session_state.lotes if l['id'] == lote_id)
                
                # Actualizar Top 3
                lote_sel["mejores_ofertas"].append({"comprador": nombre_comprador, "oferta": nueva_oferta})
                lote_sel["mejores_ofertas"] = sorted(lote_sel["mejores_ofertas"], key=lambda x: x["oferta"], reverse=True)[:3]
                
                # Registrar en el historial cronológico de pujas del lote (para que el vendedor lo vea)
                lote_sel["historial_pujas"].append({"comprador": nombre_comprador, "oferta": nueva_oferta})
                
                # Guardar en sesión para mantener la interfaz del mensaje activa sin reiniciarse
                en_top3 = any(p["comprador"] == nombre_comprador for p in lote_sel["mejores_ofertas"])
                st.session_state.ultima_oferta_activa = {
                    "lote_id": lote_sel['id'],
                    "producto": lote_sel['producto'],
                    "vendedor": lote_sel['vendedor'],
                    "oferta": nueva_oferta,
                    "en_top3": en_top3
                }
                
                # Guardar en historial personal del comprador
                registro_historial = f"{lote_sel['producto']} ({lote_sel['cantidad_kg']}kg) - Oferta: ${nueva_oferta}/kg"
                if registro_historial not in st.session_state.usuarios_db[nombre_comprador]["historial"]:
                    st.session_state.usuarios_db[nombre_comprador]["historial"].append(registro_historial)

            # Mostrar cuadro de interacción de mensaje de forma persistente si hay oferta activa
            if st.session_state.ultima_oferta_activa:
                uo = st.session_state.ultima_oferta_activa
                st.success(f"✅ ¡Oferta de ${uo['oferta']} registrada con éxito para '{uo['producto']}'!")
                
                if uo["en_top3"]:
                    st.balloons()
                    st.warning("🎉 **¡Felicidades! Estás en el TOP 3 de este lote.**")
                    
                    desea_mensaje = st.radio("¿Deseas enviar un mensaje directo al vendedor?", ["No", "Sí"], key="radio_desea_msg")
                    
                    if desea_mensaje == "Sí":
                        st.markdown("#### 💬 Redactar Mensaje al Vendedor")
                        with st.form(key="form_envio_msg_vendedor"):
                            msg = st.text_area("Escribe tu mensaje deseado:")
                            logistica = st.selectbox("Logística de envío:", ["Cadena de frío (Protección ecológica)", "Temperatura ambiente"])
                            imagen_subida = st.file_uploader("Adjuntar una imagen opcional:", type=["png", "jpg", "jpeg"])
                            
                            btn_enviar_msg_final = st.form_submit_button("Enviar Mensaje al Vendedor")
                            if btn_enviar_msg_final:
                                nuevo_id_msg = len(st.session_state.mensajes_vendedor) + 1
                                mensaje_obj = {
                                    "id_msg": nuevo_id_msg,
                                    "vendedor": uo["vendedor"], 
                                    "remitente": nombre_comprador, 
                                    "lote": uo["producto"], 
                                    "mensaje": msg, 
                                    "logistica": logistica,
                                    "imagen": imagen_subida.name if imagen_subida else None,
                                    "respuesta": None
                                }
                                st.session_state.mensajes_vendedor.append(mensaje_obj)
                                st.session_state.usuarios_db[nombre_comprador]["mensajes_enviados"].append(f"Para {uo['vendedor']} ({uo['producto']}): {msg}")
                                st.success("📩 ¡Mensaje enviado con éxito al vendedor!")
                    else:
                        st.info("Has seleccionado no enviar mensaje.")

        elif accion == "Ver mi Historial y Mensajes":
            st.markdown(f"### 📜 Historial de Compras y Pujas de: {nombre_comprador}")
            hist = st.session_state.usuarios_db[nombre_comprador]["historial"]
            if hist:
                for h in hist:
                    st.write(f"• {h}")
            else:
                st.info("Aún no tienes compras o pujas registradas.")
            
            st.markdown("### 💬 Mis Mensajes y Respuestas del Vendedor")
            mensajes_mios = [m for m in st.session_state.mensajes_vendedor if m["remitente"] == nombre_comprador]
            if mensajes_mios:
                for mm in mensajes_mios:
                    st.write(f"📤 **Para {mm['vendedor']} ({mm['lote']}):** {mm['mensaje']}")
                    if mm['respuesta']:
                        st.success(f"📥 **Respuesta del Vendedor:** {mm['respuesta']}")
                    else:
                        st.info("⏳ Esperando respuesta del vendedor...")
                    st.markdown("---")
            else:
                st.info("No has enviado mensajes directos todavía.")

# ==========================================
# 3. VISTA DE VENDEDOR
# ==========================================
elif rol == "Vendedor":
    st.subheader("📦 Panel de Control y Gestión del Vendedor")
    
    modo_auth_v = st.radio("¿Tienes una cuenta o deseas registrarte?", ["Iniciar Sesión", "Registrar Nueva Cuenta"], key="auth_vend_radio")
    nombre_vendedor_input = st.text_input("🔑 Nombre de tu empresa vendedora:", key="input_user_vend")
    password_vendedor_input = st.text_input("🔒 Contraseña personal:", type="password", key="input_pass_vend")
    
    btn_login_v = st.button("Iniciar Sesión / Acceder (Vendedor)", key="btn_login_vend")
    
    if "vendedor_logueado" not in st.session_state:
        st.session_state.vendedor_logueado = None

    if btn_login_v:
        if modo_auth_v == "Iniciar Sesión":
            if nombre_vendedor_input in st.session_state.usuarios_db:
                if st.session_state.usuarios_db[nombre_vendedor_input]["password"] == password_vendedor_input:
                    st.session_state.vendedor_logueado = nombre_vendedor_input
                    st.success(f"👋 ¡Bienvenido de nuevo, {nombre_vendedor_input}!")
                else:
                    st.error("❌ Contraseña incorrecta.")
            else:
                st.warning("⚠️ La cuenta de vendedor no existe. Selecciona 'Registrar Nueva Cuenta'.")
        
        elif modo_auth_v == "Registrar Nueva Cuenta":
            if nombre_vendedor_input in st.session_state.usuarios_db:
                st.error("❌ Este nombre ya está registrado. Inicia sesión.")
            else:
                st.session_state.usuarios_db[nombre_vendedor_input] = {
                    "rol": "vendedor",
                    "password": password_vendedor_input
                }
                st.session_state.vendedor_logueado = nombre_vendedor_input
                st.success(f"✨ ¡Cuenta de vendedor creada con éxito para {nombre_vendedor_input}!")

    if st.session_state.vendedor_logueado:
        nombre_vendedor = st.session_state.vendedor_logueado
        st.info(f"Sesión activa como Vendedor: **{nombre_vendedor}**")
        
        # Formulario para publicar nuevo lote
        with st.form("form_nuevo_lote"):
            st.markdown("### ➕ Publicar Nuevo Lote de Mermas")
            nombre_producto = st.text_input("Nombre del producto (ej. Fresas maduras, Lácteos próximos a vencer):")
            categoria_prod = st.selectbox("Categoría:", ["Frutas y Verduras", "Lácteos", "Panadería", "Carnes y Embutidos", "Otros"])
            cantidad_kg = st.number_input("Cantidad total (kg):", min_value=1.0, value=100.0)
            precio_base = st.number_input("Precio base de rescate por unidad ($):", min_value=0.5, value=4.0)
            tiempo_limite = st.text_input("Tiempo límite o vigencia:", value="3 horas restantes (Urgente)")
            
            btn_publicar = st.form_submit_button("Publicar Lote")
            
            if btn_publicar:
                if nombre_producto.strip() == "":
                    st.warning("⚠️ Ingresa el nombre del producto.")
                else:
                    nuevo_id = len(st.session_state.lotes) + 1
                    nuevo_lote = {
                        "id": nuevo_id,
                        "producto": nombre_producto,
                        "categoria": categoria_prod,
                        "cantidad_kg": cantidad_kg,
                        "precio_base": precio_base,
                        "tiempo_limite": tiempo_limite,
                        "vendedor": nombre_vendedor,
                        "mejores_ofertas": [],
                        "historial_pujas": []
                    }
                    st.session_state.lotes.append(nuevo_lote)
                    st.success(f"✅ ¡Lote #{nuevo_id} ('{nombre_producto}') publicado con éxito!")

        st.markdown("---")
        st.subheader("📈 Historial de Pujas por Producto")
        mis_lotes = [l for l in st.session_state.lotes if l["vendedor"] == nombre_vendedor]
        
        if mis_lotes:
            for l in mis_lotes:
                st.markdown(f"#### 📦 Lote #{l['id']}: {l['producto']} ({l['cantidad_kg']} kg) - Base: ${l['precio_base']}")
                if l['historial_pujas']:
                    st.write("📜 **Historial cronológico de cómo va subiendo la puja:**")
                    df_historial = pd.DataFrame(l['historial_pujas'])
                    df_historial.index = range(1, len(df_historial) + 1)
                    df_historial.columns = ["Comprador / Empresa", "Oferta por Unidad ($)"]
                    st.dataframe(df_historial, use_container_width=True)
                else:
                    st.info("Aún no se han registrado pujas en este lote.")
                st.markdown("---")
        else:
            st.info("No tienes lotes publicados todavía.")

        st.subheader("📥 Buzón de Mensajes Directos y Respuestas")
        mensajes_mi_empresa = [m for m in st.session_state.mensajes_vendedor if m["vendedor"] == nombre_vendedor]
        
        if mensajes_mi_empresa:
            for m in mensajes_mi_empresa:
                img_info = f" | 🖼️ Imagen adjunta: {m['imagen']}" if m["imagen"] else ""
                st.markdown(f"**De:** {m['remitente']} | **Lote:** *{m['lote']}*{img_info}")
                st.info(f"💬 *\"{m['mensaje']}\"*\n\n🚚 *Logística preferida:* {m['logistica']}")
                
                if m['respuesta']:
                    st.success(f"✅ **Tu respuesta enviada:** {m['respuesta']}")
                else:
                    with st.form(key=f"form_resp_{m['id_msg']}"):
                        texto_respuesta = st.text_area("Escribe una respuesta para este comprador:")
                        enviar_resp = st.form_submit_button("Enviar Respuesta")
                        if enviar_resp:
                            m['respuesta'] = texto_respuesta
                            st.success("📩 ¡Respuesta enviada al comprador con éxito!")
                            st.rerun()
                st.markdown("---")
        else:
            st.info("📭 Aún no tienes mensajes directos de compradores.")

        st.markdown("---")
        st.subheader("📊 Métricas Financieras y de Impacto Global")
        
        volumen_total = sum(l["cantidad_kg"] for l in mis_lotes)
        total_recaudado = sum(
            (l["mejores_ofertas"][0]["oferta"] if l["mejores_ofertas"] else l["precio_base"]) * l["cantidad_kg"] 
            for l in mis_lotes
        )
        
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Mis Lotes Activos", len(mis_lotes))
        m_col2.metric("Volumen Total en Gestión", f"{volumen_total:,.1f} kg")
        m_col3.metric("Recaudación Estimada", f"${total_recaudado:,.2f} USD")