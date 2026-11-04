import streamlit as st
import pandas as pd

st.set_page_config(page_title="Plataforma de Presubasta de Mermas", layout="wide")

st.title("🌱 Plataforma Integral de Presubasta de Mermas (FoodTech)")
st.markdown("Optimiza el rescate de alimentos, previene pérdidas y conecta a compradores con vendedores de forma eficiente.")

# Base de datos simulada en sesión
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

if rol == "Invitado (Solo lectura)":
    st.subheader("👁️ Vista Pública de Lotes Activos")
    for l in st.session_state.lotes:
        st.write(f"**[Lote #{l['id']}] {l['producto']}** ({l['categoria']}) | Cantidad: {l['cantidad_kg']} kg | Vendedor: {l['vendedor']}")
        st.caption(f"⏰ {l['tiempo_limite']}")

elif rol == "Comprador":
    st.subheader("🛒 Panel de Comprador y Presubasta")
    nombre_comprador = st.text_input("Ingresa el nombre de tu empresa:")
    
    if nombre_comprador:
        if nombre_comprador not in st.session_state.usuarios_db:
            st.session_state.usuarios_db[nombre_comprador] = {"historial": []}
            
        accion = st.radio("¿Qué deseas hacer?", ["Pujar en un Lote", "Ver mi Historial de Compras"])
        
        if accion == "Pujar en un Lote":
            st.markdown("---")
            for l in st.session_state.lotes:
                st.write(f"**Lote ID {l['id']}: {l['producto']}** | Cantidad: {l['cantidad_kg']} kg | Precio Base: ${l['precio_base']}")
                st.write("🏆 *Top 3 pujas actuales:*")
                for i, p in enumerate(l['mejores_ofertas'], 1):
                    st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;{i}. {p['comprador']} - ${p['oferta']} USD")
            
            lote_id = st.selectbox("Selecciona el ID del Lote:", [l['id'] for l in st.session_state.lotes])
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
                    st.warning("🎉 ¡Estás en el TOP 3! Tienes un canal directo disponible.")
                    desea_chat = st.checkbox("¿Deseas enviar un mensaje directo al vendedor?")
                    if desea_chat:
                        msg = st.text_input("Mensaje directo:")
                        logistica = st.selectbox("Logística de envío:", ["Cadena de frío (Protección ecológica)", "Temperatura ambiente"])
                        if st.button("Enviar mensaje"):
                            st.success(f"Mensaje enviado con logística de tipo: {logistica}")
                
                # Guardar en historial
                st.session_state.usuarios_db[nombre_comprador]["historial"].append(f"{lote_sel['producto']} ({lote_sel['cantidad_kg']}kg) - ${nueva_oferta}/kg")

        elif accion == "Ver mi Historial de Compras":
            st.markdown(f"### 📜 Historial de: {nombre_comprador}")
            hist = st.session_state.usuarios_db[nombre_comprador]["historial"]
            if hist:
                for h in hist:
                    st.write(f"• {h}")
            else:
                st.info("Aún no tienes compras o pujas registradas.")

elif rol == "Vendedor":
    st.subheader("📦 Panel de Gestión para Vendedores")
    st.write("Aquí puedes supervisar los lotes publicados y los reportes de rendimiento.")
    
    total_recaudado = sum(l["mejores_ofertas"][0]["oferta"] * l["cantidad_kg"] for l in st.session_state.lotes)
    volumen_total = sum(l["cantidad_kg"] for l in st.session_state.lotes)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Volumen Total Rescatado", f"{volumen_total} kg")
    col2.metric("Recaudación Estimada", f"${total_recaudado:,.2f} USD")
    col3.metric("CO₂ Evitado", f"{volumen_total * 2.5:,.1f} kg")