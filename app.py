import streamlit as st
import pandas as pd

# Configuración de la página web
st.set_page_config(page_title="Plataforma de Presubasta de Mermas", layout="wide")

st.title("🌱 Plataforma Integral de Presubasta de Mermas (FoodTech)")
st.markdown("Optimiza el rescate de alimentos, previene pérdidas y conecta dinámicamente a compradores con vendedores.")

# 1. Base de datos persistente en la sesión de Streamlit para el Top 3 y lotes
if "lotes_mercado" not in st.session_state:
    st.session_state.lotes_mercado = [
        {
            "id": 1, 
            "producto": "Tomate fresco", 
            "categoria": "Frutas y Verduras", 
            "cantidad_kg": 150, 
            "precio_base": 5.00, 
            "mejores_ofertas": [
                {"comprador": "Comercializadora Norte", "oferta": 7.50},
                {"comprador": "Supermercado Express", "oferta": 7.00},
                {"comprador": "Frutería Local", "oferta": 6.80}
            ]
        },
        {
            "id": 2, 
            "producto": "Yogurt natural (Cercano a caducar)", 
            "categoria": "Lácteos", 
            "cantidad_kg": 80, 
            "precio_base": 12.00, 
            "mejores_ofertas": [
                {"comprador": "Lácteos del Sur", "oferta": 15.00},
                {"comprador": "Distribuidora Central", "oferta": 14.50},
                {"comprador": "Mercado Fresco", "oferta": 14.00}
            ]
        },
        {
            "id": 3, 
            "producto": "Pan artesanal del día", 
            "categoria": "Panadería", 
            "cantidad_kg": 50, 
            "precio_base": 3.00, 
            "mejores_ofertas": [
                {"comprador": "Panificadora Central", "oferta": 4.20},
                {"comprador": "Cafetería Aroma", "oferta": 3.90},
                {"comprador": "Bistró Local", "oferta": 3.60}
            ]
        }
    ]

# Menú lateral para cambiar de rol y probar la interacción real
st.sidebar.header("🔐 Selección de Rol")
rol = st.sidebar.selectbox("¿Cómo deseas ingresar?", ["Comprador", "Vendedor", "Invitado"])

if rol == "Invitado":
    st.subheader("👁️ Vista Pública de Lotes Activos")
    for l in st.session_state.lotes_mercado:
        st.write(f"**[Lote #{l['id']}] {l['producto']}** ({l['categoria']}) | Cantidad: {l['cantidad_kg']} kg | Precio Base: ${l['precio_base']} USD")
        st.write("🏆 *Top 3 pujas actuales:*")
        for i, p in enumerate(l['mejores_ofertas'], 1):
            st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;{i}. {p['comprador']} - **${p['oferta']} USD**")
        st.markdown("---")

elif rol == "Comprador":
    st.subheader("🛒 Panel de Puja Interactiva para Compradores")
    nombre_comprador = st.text_input("Ingresa el nombre de tu empresa o comprador:")
    
    # Mostrar estado actual de los lotes y su Top 3
    st.markdown("### 📦 Lotes disponibles y Podio actual")
    for l in st.session_state.lotes_mercado:
        st.markdown(f"**Lote ID {l['id']}: {l['producto']}** ({l['categoria']}) | Cantidad: {l['cantidad_kg']} kg | Base: ${l['precio_base']}")
        podio_str = " | ".join([f"{i+1}. {p['comprador']} (${p['oferta']})" for i, p in enumerate(l['mejores_ofertas'])])
        st.caption(f"🏆 Podio Top 3: {podio_str}")

    st.markdown("---")
    lote_id = st.selectbox("Selecciona el ID del Lote por el que deseas ofertar:", [l['id'] for l in st.session_state.lotes_mercado])
    nueva_oferta = st.number_input("Ingresa el valor de tu oferta por unidad ($ USD):", min_value=1.0, value=7.0)

    if st.button("Registrar Oferta"):
        if not nombre_comprador.strip():
            st.warning("⚠️ Por favor ingresa el nombre de tu empresa antes de ofertar.")
        else:
            # Encontrar el lote seleccionado
            lote_encontrado = next(l for l in st.session_state.lotes_mercado if l['id'] == lote_id)
            
            # Añadir y ordenar las ofertas de mayor a menor, tomando solo el Top 3
            lote_encontrado["mejores_ofertas"].append({"comprador": nombre_comprador, "oferta": nueva_oferta})
            lote_encontrado["mejores_ofertas"] = sorted(
                lote_encontrado["mejores_ofertas"], 
                key=lambda x: x["oferta"], 
                reverse=True
            )[:3]
            
            st.success(f"✅ ¡Oferta de ${nueva_oferta} registrada con éxito para '{lote_encontrado['producto']}'!")
            
            # Verificar si el usuario ingresó al Top 3
            en_top3 = any(p["comprador"] == nombre_comprador for p in lote_encontrado["mejores_ofertas"])
            if en_top3:
                st.balloons()
                st.warning(f"🎉 **¡Felicidades, {nombre_comprador}!** Estás en el **TOP 3** de este lote.")
                st.info("💬 **[MENSAJE DIRECTO ACTIVADO]:** Canal privado abierto con el Vendedor.")
                mensaje_chat = st.text_input("Escribe tu mensaje directo al vendedor (ej. logística o volúmenes):")
                if st.button("Enviar Mensaje al Vendedor"):
                    st.success(f"📩 Mensaje enviado al vendedor de **{lote_encontrado['producto']}** con éxito.")
            else:
                st.info("ℹ️ Tu oferta se registró, pero estás fuera del Top 3 actual. ¡Intenta con una puja mayor!")

elif rol == "Vendedor":
    st.subheader("📦 Panel de Control del Vendedor")
    st.markdown("Supervisa en tiempo real el comportamiento de los lotes y las ofertas líderes de los compradores.")
    
    for l in st.session_state.lotes_mercado:
        with st.container():
            st.markdown(f"### Lote #{l['id']}: {l['producto']}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Cantidad", f"{l['cantidad_kg']} kg")
            col2.metric("Precio Base", f"${l['precio_base']} USD")
            
            mejor_oferta = l['mejores_ofertas'][0]['oferta'] if l['mejores_ofertas'] else l['precio_base']
            col3.metric("Oferta Líder Actual", f"${mejor_oferta} USD")
            
            st.write("🏆 **Top 3 Postores actuales:**")
            for i, p in enumerate(l['mejores_ofertas'], 1):
                st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;{i}. **{p['comprador']}** con **${p['oferta']} USD**")
            st.markdown("---")
            
    # Estadísticas globales para el vendedor
    st.subheader("📊 Métricas Financieras y de Impacto Global")
    volumen_total = sum(l["cantidad_kg"] for l in st.session_state.lotes_mercado)
    recaudacion_total = sum(l["mejores_ofertas"][0]["oferta"] * l["cantidad_kg"] for l in st.session_state.lotes_mercado if l["mejores_ofertas"])
    
    m_col1, m_col2 = st.columns(2)
    m_col1.metric("Volumen Total en Gestión", f"{volumen_total} kg")
    m_col2.metric("Recaudación Estimada (Ofertas Líderes)", f"${recaudacion_total:,.2f} USD")