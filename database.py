import sqlite3
from datetime import datetime

def inicializar_bd():
    conn = sqlite3.connect("mermax.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            nombre TEXT PRIMARY KEY,
            rol TEXT,
            password TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto TEXT,
            categoria TEXT,
            cantidad_kg REAL,
            kilos_vendidos REAL DEFAULT 0,
            precio_base REAL,
            tiempo_limite TEXT,
            vendedor TEXT,
            fecha TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pujas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lote_id INTEGER,
            comprador TEXT,
            oferta REAL,
            kilos_solicitados REAL,
            fecha TEXT,
            FOREIGN KEY(lote_id) REFERENCES lotes(id)
        )
    """)
    
    # Historial de chat ilimitado y estructurado
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendedor TEXT,
            remitente TEXT,
            lote TEXT,
            mensaje TEXT,
            logistica TEXT,
            imagen TEXT,
            respuesta TEXT,
            fecha TEXT
        )
    """)
    
    conn.commit()
    conn.close()
