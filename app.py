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
            ]
        }
    ]

# Base de datos de perfiles, contraseñas, historiales y buzón de mensajes
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
            "password": "123",
            "historial": [],
            "mensajes_enviados": []
        }
    }

if "mensajes_vendedor" not in st.session_state:
    st.session_state.mensajes_vendedor = [
        {"vendedor": "Agro Alimentos S.A.", "remitente": "Supermercado Express", "lote": "Tomate fresco", "mensaje": "Interesado en cadena de frío para entrega.", "logistica": "Cadena de frío (Protección ecológica)", "imagen": None}
    ]

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
# 2. VISTA DE COMPRADOR (CON CONTRASEÑA)
# ==========================================
elif rol == "Comprador":
    st.subheader("🛒 Panel de Comprador y Presubasta")
    
    modo_auth = st.radio("¿Tienes una cuenta o deseas registrarte?", ["Iniciar Sesión", "Registrar Nueva Cuenta"])
    nombre_comprador = st.text_input("🔑 Nombre de tu empresa compradora:")
    password_comprador = st.text_input("🔒 Contraseña personal:", type="password")
    
    acceso_concedido = False

    if nombre_comprador and password_comprador:
        if modo_auth == "Iniciar Sesión":
            if nombre_comprador in st.session_state.usuarios_db:
                if st.session_state.usuarios_db[nombre_comprador]["password"] == password_comprador:
                    acceso_concedido = True
                    st.success(f"👋 ¡Bienvenido de nuevo, {nombre_comprador}!")
                else:
                    st.error("❌ Contraseña incorrecta.")
            else:
                st.warning("⚠️ La cuenta no existe. Selecciona 'Registrar Nueva Cuenta' para crear una.")
        
        elif modo_auth == "Registrar Nueva Cuenta":
            if nombre_comprador in st.session_state.usuarios_db:
                st.error("❌ Este nombre de usuario ya está registrado. Inicia sesión.")
            else:
                st.session_state.usuarios_db[nombre_comprador] = {
                    "rol": "comprador",
                    "password": password_comprador,
                    "historial": [],
                    "mensajes_enviados": []
                }
                acceso_concedido = True
                st.success(f"✨ ¡Cuenta creada e iniciada con éxito para {nombre_comprador}!")

    if acceso_concedido:
        accion = st.radio("¿Qué deseas hacer?", ["Pujar en un Lote", "Ver mi Historial y Mensajes"])
        
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
            
            lote_id = st.selectbox("Selecciona el ID del Lote por el que deseas ofertar:", [l['id'] for l in st.session_state.lotes])
            nueva_oferta = st.number_input("Tu oferta por unidad ($):", min_value=1.0, value=7.0)
            
            if st.button("Enviar Oferta"):
                lote_sel = next(l for l in st.session_state.lotes if l['id'] == lote_id)
                lote_sel["mejores_ofertas"].append({"comprador": nombre_comprador, "oferta": nueva_oferta})
                lote_sel["mejores_ofertas"] = sorted(lote_sel["mejores_ofertas"], key=lambda x: x["oferta"], reverse=True)[:3]
                
                st.success(f"✅ ¡Oferta de ${nueva_oferta} registrada con éxito!")
                
                # Verificar Top 3
                en_top3 = any(p["comprador"] == nombre_comprador for p in lote_sel["mejores_ofertas"])
                if en_top3:
                    st.balloons()
                    st.warning("🎉 **¡Felicidades! Estás en el TOP 3.**")
                    
                    # Opción Sí/No para el mensaje al vendedor
                    desea_mensaje = st.radio("¿Deseas enviar un mensaje directo al vendedor?", ["No", "Sí"])
                    
                    if desea_mensaje == "Sí":
                        msg = st.text_area("Escribe tu mensaje deseado:")
                        logistica = st.selectbox("Logística de envío:", ["Cadena de frío (Protección ecológica)", "Temperatura ambiente"])
                        imagen_subida = st.file_uploader("Adjuntar una imagen opcional (comprobante, referencia, etc.):", type=["png", "jpg", "jpeg"])
                        
                        if st.button("Enviar mensaje al vendedor"):
                            # Guardar mensaje en el buzón global del vendedor y del usuario
                            mensaje_obj = {
                                "vendedor": lote_sel["vendedor"], 
                                "remitente": nombre_comprador, 
                                "lote": lote_sel["producto"], 
                                "mensaje": msg, 
                                "logistica": logistica,
                                "imagen": imagen_subida.name if imagen_subida else None
                            }
                            st.session_state.mensajes_vendedor.append(mensaje_obj)
                            st.session_state.usuarios_db[nombre_comprador]["mensajes_enviados"].append(f"Para {lote_sel['vendedor']} ({lote_sel['producto']}): {msg}")
                            st.success("📩 ¡Mensaje y archivo enviados con éxito y guardados en tu historial!")
                    else:
                        st.info("Has seleccionado no enviar mensaje. Puedes continuar navegando.")
                
                # Guardar en historial del comprador
                registro_historial = f"{lote_sel['producto']} ({lote_sel['cantidad_kg']}kg) - Oferta: ${nueva_oferta}/kg"
                if registro_historial not in st.session_state.usuarios_db[nombre_comprador]["historial"]:
                    st.session_state.usuarios_db[nombre_comprador]["historial"].append(registro_historial)

        elif accion == "Ver mi Historial y Mensajes":
            st.markdown(f"### 📜 Historial de Compras y Pujas de: {nombre_comprador}")
            hist = st.session_state.usuarios_db[nombre_comprador]["historial"]
            if hist:
                for h in hist:
                    st.write(f"• {h}")
            else:
                st.info("Aún no tienes compras o pujas registradas.")
            
            st.markdown("### 💬 Mis Mensajes Enviados al Vendedor")
            mensajes_usr = st.session_state.usuarios_db[nombre_comprador]["mensajes_enviados"]
            if mensajes_usr:
                for mu in mensajes_usr:
                    st.write(f"📤 {mu}")
            else:
                st.info("No has enviado mensajes directos todavía.")

# ==========================================
# 3. VISTA DE VENDEDOR (CON CONTRASEÑA)
# ==========================================
elif rol == "Vendedor":
    st.subheader("📦 Panel de Control y Gestión del Vendedor")
    
    modo_auth_v = st.radio("¿Tienes una cuenta o deseas registrarte?", ["Iniciar Sesión", "Registrar Nueva Cuenta"])
    nombre_vendedor = st.text_input("🔑 Nombre de tu empresa vendedora:")
    password_vendedor = st.text_input("🔒 Contraseña personal:", type="password")
    
    acceso_vendedor_concedido = False

    if nombre_vendedor and password_vendedor:
        if modo_auth_v == "Iniciar Sesión":
            if nombre_vendedor in st.session_state.usuarios_db:
                if st.session_state.usuarios_db[nombre_vendedor]["password"] == password_vendedor:
                    acceso_vendedor_concedido = True
                    st.success(f"👋 ¡Bienvenido de nuevo, {nombre_vendedor}!")
                else:
                    st.error("❌ Contraseña incorrecta.")
            else:
                st.warning("⚠️ La cuenta de vendedor no existe. Selecciona 'Registrar Nueva Cuenta'.")
        
        elif modo_auth_v == "Registrar Nueva Cuenta":
            if nombre_vendedor in st.session_state.usuarios_db:
                st.error("❌ Este nombre ya está registrado. Inicia sesión.")
            else:
                st.session_state.usuarios_db[nombre_vendedor] = {
                    "rol": "vendedor",
                    "password": password_vendedor,
                    "historial": [],
                    "mensajes_enviados": []
                }
                acceso_vendedor_concedido = True
                st.success(f"✨ ¡Cuenta de vendedor creada con éxito para {nombre_vendedor}!")

    if acceso_vendedor_concedido:
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
                        "mejores_ofertas": []
                    }
                    st.session_state.lotes.append(nuevo_lote)
                    st.success(f"✅ ¡Lote #{nuevo_id} ('{nombre_producto}') publicado y visible para los compradores con éxito!")

        st.markdown("---")
        st.subheader("📥 Buzón de Mensajes Directos Recibidos")
        # Filtrar mensajes dirigidos a este vendedor
        mensajes_mi_empresa = [m for m in st.session_state.mensajes_vendedor if m["vendedor"] == nombre_vendedor]
        
        if mensajes_mi_empresa:
            for idx, m in enumerate(mensajes_mi_empresa, 1):
                img_info = f" | 🖼️ Imagen adjunta: {m['imagen']}" if m["imagen"] else ""
                st.info(f"**Mensaje #{idx}** | De: **{m['remitente']}** | Lote: *{m['lote']}*{img_info}\n\n💬 *\"{m['mensaje']}\"*\n\n🚚 *Logística preferida:* {m['logistica']}")
        else:
            st.info("📭 Aún no tienes mensajes directos de compradores del Top 3.")

        st.markdown("---")
        st.subheader("📊 Métricas Financieras y de Impacto Global")
        
        # Filtrar lotes de este vendedor
        mis_lotes = [l for l in st.session_state.lotes if l["vendedor"] == nombre_vendedor]
        volumen_total = sum(l["cantidad_kg"] for l in mis_lotes)
        total_recaudado = sum(
            (l["mejores_ofertas"][0]["oferta"] if l["mejores_ofertas"] else l["precio_base"]) * l["cantidad_kg"] 
            for l in mis_lotes
        )
        
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Mis Lotes Activos", len(mis_lotes))
        m_col2.metric("Volumen Total en Gestión", f"{volumen_total:,.1f} kg")
        m_col3.metric("Recaudación Estimada", f"${total_recaudado:,.2f} USD")