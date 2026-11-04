import streamlit as st
import sqlite3

st.set_page_config(page_title="Portal de Compradores", layout="wide")
st.title("🛒 Panel de Comprador - Presubasta y Pujas")

# Sistema de Autenticación de Comprador
st.sidebar.header("🔐 Acceso Comprador")
modo = st.sidebar.radio("Acción:", ["Iniciar Sesión", "Registrarse"], key="auth_c")
user = st.sidebar.text_input("Empresa Compradora:", key="uc")
pwd = st.sidebar.text_input("Contraseña:", type="password", key="pc")

if st.sidebar.button("Entrar / Registrarse", key="btn_auth_c"):
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
    st.success(f"Sesión activa: **{comprador}**")
    
    conn = sqlite3.connect("mermax.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, producto, categoria, cantidad_kg, precio_base, vendedor FROM lotes")
    lotes = cursor.fetchall()
    
    st.markdown("### 📦 Lotes Disponibles para Pujar")
    lote_opciones = {f"Lote #{l[0]} - {l[1]} ($ {l[4]} base)": l[0] for l in lotes}
    
    if lote_opciones:
        lote_elegido_str = st.selectbox("Selecciona un lote:", list(lote_opciones.keys()))
        lote_id = lote_opciones[lote_elegido_str]
        
        nueva_oferta = st.number_input("Tu oferta por unidad ($):", min_value=1.0, value=7.0)
        if st.button("Enviar Puja"):
            cursor.execute("INSERT INTO pujas (lote_id, comprador, oferta) VALUES (?, ?, ?)", (lote_id, comprador, nueva_oferta))
            conn.commit()
            st.success("¡Puja registrada con éxito en la base de datos!")
    else:
        st.info("No hay lotes disponibles para pujar en este momento.")
    conn.close()
else:
    st.warning("Por favor, inicia sesión o regístrate en el menú lateral para realizar pujas.")