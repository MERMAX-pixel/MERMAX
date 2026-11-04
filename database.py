import sqlite3

def inicializar_bd():
    conn = sqlite3.connect("mermax.db")
    cursor = conn.cursor()
    
    # Tabla de Usuarios (Compradores y Vendedores)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            nombre TEXT PRIMARY KEY,
            rol TEXT,
            password TEXT
        )
    """)
    
    # Tabla de Lotes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto TEXT,
            categoria TEXT,
            cantidad_kg REAL,
            precio_base REAL,
            tiempo_limite TEXT,
            vendedor TEXT
        )
    """)
    
    # Tabla de Pujas / Ofertas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pujas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lote_id INTEGER,
            comprador TEXT,
            oferta REAL,
            FOREIGN KEY(lote_id) REFERENCES lotes(id)
        )
    """)
    
    # Tabla de Mensajes y Negociación
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendedor TEXT,
            remitente TEXT,
            lote TEXT,
            mensaje TEXT,
            logistica TEXT,
            imagen TEXT,
            respuesta TEXT
        )
    """)
    
    conn.commit()
    conn.close()

# Funciones de apoyo para insertar y consultar datos fácilmente
def registrar_usuario(nombre, rol, password):
    conn = sqlite3.connect("mermax.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (nombre, rol, password) VALUES (?, ?, ?)", (nombre, rol, password))
        conn.commit()
        exito = True
    except sqlite3.IntegrityError:
        exito = False
    conn.close()
    return exito

def verificar_usuario(nombre, password):
    conn = sqlite3.connect("mermax.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE nombre = ? AND password = ?", (nombre, password))
    user = cursor.fetchone()
    conn.close()
    return user