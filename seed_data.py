import sqlite3
from datetime import datetime

DATABASE = 'database.db'

with sqlite3.connect(DATABASE) as conn:
    conn.execute('PRAGMA foreign_keys = ON')
    with open('schema.sql', 'r', encoding='utf-8') as f:
        conn.executescript(f.read())

    conn.execute(
        'INSERT INTO empresa (nombre, nit, direccion, ciudad, telefono, stock_minimo_alerta, factor_holgura, cupo_base_inicial) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        ('RaDuqQui Petrol', '123456789', 'Calle Central 100', 'Ciudad', '+57 300 0000000', 120, 0.10, 120)
    )

    conn.execute(
        'INSERT INTO tanque (codigo, tipo_carburante, capacidad_maxima, stock_minimo_seguridad, stock_actual) VALUES (?, ?, ?, ?, ?)',
        ('T-01', 'Gasolina', 15000, 1000, 10000)
    )
    conn.execute(
        'INSERT INTO tanque (codigo, tipo_carburante, capacidad_maxima, stock_minimo_seguridad, stock_actual) VALUES (?, ?, ?, ?, ?)',
        ('T-02', 'Diésel', 12000, 1000, 8000)
    )

    conn.execute(
        'INSERT INTO cliente (documento, nombre, placa, tipo_cliente, estado, creado_en) VALUES (?, ?, ?, ?, ?, ?)',
        ('11223344', 'Cliente Ejemplo', 'ABC123', 'Particular', 'Activo', datetime.utcnow().isoformat())
    )

    conn.commit()

print('Datos de ejemplo cargados en', DATABASE)
