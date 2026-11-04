import streamlit as st
import pandas as pd

# Configuración de la página web
st.set_page_config(page_title="Plataforma de Presubasta de Mermas", layout="wide")

st.title("🌱 Plataforma Integral de Presubasta de Mermas (FoodTech)")
st.markdown("Optimiza el rescate de alimentos, previene pérdidas y conecta dinámicamente a compradores con vendedores.")

# 1. Base de datos simulada en la sesión para que los datos persistan mientras usas la app
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
                {"comprador": "Frutería Local", "oferta": 6.80},
                {"comprador": "Comercializadora Norte", "oferta": 6.50}
            ]
        },
        {
            "id": 2, 
            "producto": "Yogurt natural (Cercano a caducar)", 
            "categoria": "Lácteos", 
            "cantidad_kg": 80, 
            "precio_base": 12.00, 
            "tiempo_limite": "45 minutos restantes (¡Urgente!)",
            "vendedor": "Lácteos del Sur",
            "mejores_ofertas": [
                {"comprador": "Distribuidora Central", "oferta": 15.00},
                {"comprador": "Mercado Fresco", "oferta": 14.50}
            ]
        }
    ]

if "usuarios_db" not in st.session_state:
    st.session_state.usuarios_db = {
        "Supermercado Express": {"historial": ["Tomate fresco (150kg) - $7.50/kg"]}
    }

# Menú lateral para selección de perfiles
st.sidebar.header("🔐 Portal de Acceso")
rol = st.sidebar.selectbox("Selecciona tu rol:", ["Invitado (Solo lectura)", "Comprador", "Vendedor"])

# ==========================================
# VISTA DE INVITADO
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
# VISTA DE COMPRADOR
# ==========================================
elif rol == "Comprador":
    st.subheader("🛒 Panel de Comprador y Presubasta")
    nombre_comprador = st.text_input("Ingresa el nombre de tu empresa compradora:")
    
    if nombre_comprador:
        if nombre_comprador not in st.session_state.usuarios_db:
            st.session_state.usuarios_db[nombre_comprador] = {"historial": []}
            
        accion = st.radio("¿Qué deseas hacer?", ["Pujar en un Lote", "Ver mi Historial de Compras"])
        
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
                
                st.success(f"¡Oferta de ${nueva_oferta} registrada con éxito!")
                
                # Incentivo por volumen
                if lote_sel["cantidad_kg"] >= 100:
                    st.info("🎁 [Incentivo por volumen]: Al superar los 100 kg, obtienes 5% de descuento en gestión.")
                
                # Verificar Top 3
                en_top3 = any(p["comprador"] == nombre_comprador for p in lote_sel["mejores_ofertas"])
                if en_top3:
                    st.balloons()
                    st.warning("🎉 ¡Estás en el TOP 3! Tienes un canal directo disponible con el vendedor.")
                    desea_chat = st.checkbox("¿Deseas enviar un mensaje directo al vendedor (opcional)?")
                    if desea_chat:
                        msg = st.text_input("Mensaje directo:")
                        logistica = st.selectbox("Logística de envío:", ["Cadena de frío (Protección ecológica)", "Temperatura ambiente"])
                        if st.button("Enviar mensaje"):
                            st.success(f"Mensaje enviado con logística de tipo: {logistica}")
                
                # Guardar en historial del comprador
                st.session_state.usuarios_db[nombre_comprador]["historial"].append(f"{lote_sel['producto']} ({lote_sel['cantidad_kg']}kg) - ${nueva_oferta}/kg")

        elif accion == "Ver mi Historial de Compras":
            st.markdown(f"### 📜 Historial de: {nombre_comprador}")
            hist = st.session_state.usuarios_db[nombre_comprador]["historial"]
            if hist:
                for h in hist:
                    st.write(f"• {h}")
            else:
                st.info("Aún no tienes compras o pujas registradas.")

# ==========================================
# VISTA DE VENDEDOR (NUEVA OPCIÓN DE REGISTRO)
# ==========================================
elif rol == "Vendedor":
    st.subheader("📦 Panel de Gestión y Publicación para Vendedores")
    st.write("Aquí puedes registrar nuevos productos o lotes de mermas anticipadas para que los compradores puedan ofertar.")
    
    with st.form("form_nuevo_lote"):
        st.markdown("### ➕ Publicar Nuevo Lote / Producto")
        nombre_vendedor = st.text_input("Nombre de tu empresa o finca:", value="Agro Alimentos S.A.")
        nombre_producto = st.text_input("Nombre del producto (ej. Fresas maduras, Leche en stock):")
        categoria_prod = st.selectbox("Categoría:", ["Frutas y Verduras", "Lácteos", "Panadería", "Carnes y Embutidos", "Otros"])
        cantidad_kg = st.number_input("Cantidad total (kg o unidades):", min_value=1.0, value=100.0)
        precio_base = st.number_input("Precio base de rescate por unidad ($):", min_value=0.5, value=4.0)
        tiempo_limite = st.text_input("Tiempo límite o vigencia:", value="3 horas restantes (Urgente)")
        
        btn_publicar = st.form_submit_button("Publicar Lote en la Plataforma")
        
        if btn_publicar:
            if nombre_producto.strip() == "":
                st.warning("⚠️ Por favor ingresa el nombre del producto.")
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
                    "mejores_ofertas": [] # Inicia sin ofertas hasta que los compradores pujen
                }
                st.session_state.lotes.append(nuevo_lote)
                st.success(f"✅ ¡Lote #{nuevo_id} ('{nombre_producto}') publicado con éxito! Ya está visible para los compradores.")

    st.markdown("---")
    st.subheader("📊 Reportes y Métricas Financieras en Tiempo Real")
    
    # Cálculos globales actualizados con los lotes reales
    total_recaudado = sum(
        (l["mejores_ofertas"][0]["oferta"] if l["mejores_ofertas"] else l["precio_base"]) * l["cantidad_kg"] 
        for l in st.session_state.lotes
    )
    volumen_total = sum(l["cantidad_kg"] for l in st.session_state.lotes)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Volumen Total Rescatado", f"{volumen_total:,.1f} kg")
    col2.metric("Recaudación Estimada", f"${total_recaudado:,.2f} USD")
    col3.metric("CO₂ Evitado", f"{volumen_total * 2.5:,.1f} kg")
    
    st.markdown("### 📋 Lotes Actuales Publicados por Vendedores")
    for l in st.session_state.lotes:
        st.write(f"**[Lote #{l['id']}] {l['producto']}** | Cantidad: {l['cantidad_kg']} kg | Base: ${l['precio_base']} | Vendedor: {l['vendedor']}")
        if l['mejores_ofertas']:
            st.caption(f"🏆 Oferta líder actual: ${l['mejores_ofertas'][0]['oferta']} por {l['mejores_ofertas'][0]['comprador']}")
        else:
            st.caption("⏳ Esperando primera oferta de los compradores...")