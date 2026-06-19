PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS empresa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    nit TEXT NOT NULL UNIQUE,
    direccion TEXT NOT NULL,
    ciudad TEXT NOT NULL,
    telefono TEXT,
    stock_minimo_alerta INTEGER NOT NULL DEFAULT 100,
    factor_holgura REAL NOT NULL DEFAULT 0.10,
    cupo_base_inicial INTEGER NOT NULL DEFAULT 100
);

CREATE TABLE IF NOT EXISTS tanque (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    tipo_carburante TEXT NOT NULL CHECK(tipo_carburante IN ('Gasolina', 'Diésel')),
    capacidad_maxima INTEGER NOT NULL,
    stock_minimo_seguridad INTEGER NOT NULL,
    stock_actual INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cliente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    documento TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    placa TEXT NOT NULL UNIQUE,
    tipo_cliente TEXT NOT NULL CHECK(tipo_cliente IN ('Particular', 'Transporte Público', 'Empresa')),
    estado TEXT NOT NULL CHECK(estado IN ('Activo', 'Suspendido')),
    creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ingreso (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanque_id INTEGER NOT NULL,
    litros INTEGER NOT NULL,
    factura TEXT NOT NULL,
    fecha_hora TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(tanque_id) REFERENCES tanque(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS venta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    tanque_id INTEGER NOT NULL,
    litros INTEGER NOT NULL,
    tipo_carburante TEXT NOT NULL CHECK(tipo_carburante IN ('Gasolina', 'Diésel')),
    fecha_hora TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    precio_unitario REAL,
    total REAL,
    FOREIGN KEY(cliente_id) REFERENCES cliente(id) ON DELETE RESTRICT,
    FOREIGN KEY(tanque_id) REFERENCES tanque(id) ON DELETE RESTRICT
);
