import sqlite3

def inicializar_bd():
    conn = sqlite3.connect("mermax.db")
    cursor = conn.cursor()
    
    # Tabla de Usuarios
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
            kilos_vendidos REAL DEFAULT 0,
            precio_base REAL,
            tiempo_limite TEXT,
            vendedor TEXT
        )
    """)
    
    # Tabla de Pujas (incluye los kilos que el comprador desea adquirir de forma parcial)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pujas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lote_id INTEGER,
            comprador TEXT,
            oferta REAL,
            kilos_solicitados REAL,
            FOREIGN KEY(lote_id) REFERENCES lotes(id)
        )
    """)
    
    # Tabla de Mensajes y Negociación bidireccional
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
