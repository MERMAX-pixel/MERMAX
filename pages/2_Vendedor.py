import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Portal de Vendedores", layout="wide")
st.title("📦 Panel de Control de Vendedores")

st.sidebar.header("🔐 Acceso Vendedor")
modo_v = st.sidebar.radio("Acción:", ["Iniciar Sesión", "Registrarse"], key="auth_v")
user_v = st.sidebar.text_input("Empresa Vendedora:", key="uv")
pwd_v = st.sidebar.text_input("Contraseña:", type="password", key="pv")

if st.sidebar.button("Entrar / Registrarse", key="btn_auth_v"):
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
        st.markdown("### ➕ Publicar Nuevo Lote")
        prod = st.text_input("Nombre del Producto:")
        cat = st.selectbox("Categoría:", ["Frutas y Verduras", "Lácteos", "Panadería", "Otros"])
        cant = st.number_input("Cantidad (kg):", min_value=1.0, value=100.0)
        base = st.number_input("Precio Base ($):", min_value=0.5, value=5.0)
        tiempo = st.text_input("Vigencia:", value="2 horas restantes")
        
        if st.form_submit_button("Publicar en el Mercado"):
            conn = sqlite3.connect("mermax.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO lotes (producto, categoria, cantidad_kg, precio_base, tiempo_limite, vendedor) VALUES (?, ?, ?, ?, ?, ?)",
                           (prod, cat, cant, base, tiempo, vendedor))
            conn.commit()
            conn.close()
            st.success("¡Lote publicado correctamente!")

    st.markdown("---")
    st.subheader("📈 Historial de Pujas en tus Lotes")
    conn = sqlite3.connect("mermax.db")
    query = f"SELECT l.id, l.producto, p.comprador, p.oferta FROM lotes l JOIN pujas p ON l.id = p.lote_id WHERE l.vendedor = '{vendedor}'"
    df_pujas = pd.read_sql(query, conn)
    conn.close()
    
    if not df_pujas.empty:
        st.dataframe(df_pujas, use_container_width=True)
    else:
        st.info("Aún no hay pujas en tus lotes.")
else:
    st.warning("Por favor, inicia sesión o regístrate en el menú lateral para gestionar tus productos.")
