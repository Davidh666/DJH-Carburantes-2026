# DOCUMENTACIÓN TÉCNICA - RaDuqQui Petrol

## 1. Modelo de Datos - Diagrama ER

```
┌─────────────────┐
│    EMPRESA      │
├─────────────────┤
│ id (PK)         │
│ nombre          │
│ nit             │
│ direccion       │
│ ciudad          │
│ telefono        │
│ stock_minimo_alerta
│ factor_holgura  │
│ cupo_base_inicial
└─────────────────┘
        │
        │ (Configuración global para)
        ▼
┌─────────────────┐
│    TANQUE       │
├─────────────────┤
│ id (PK)         │
│ codigo          │──┐
│ tipo_carburante  │ 1
│ capacidad_maxima│ │
│ stock_minimo    │ │
│ stock_actual    │ │
│ created_at      │ │
└─────────────────┘ │
        │           │ (N)
        │ (N)       │ Abastece
   Tiene            │
        │           │
        ▼           │
    INGRESO◄────────┘
 ┌─────────────────┐
 │ id (PK)         │
 │ tanque_id (FK)  │
 │ litros          │
 │ factura         │
 │ fecha_hora      │
 └─────────────────┘


┌─────────────────┐
│    CLIENTE      │
├─────────────────┤
│ id (PK)         │
│ documento       │
│ nombre          │
│ placa           │
│ tipo_cliente    │
│ estado          │
│ creado_en       │
└─────────────────┘
        │
        │ (N)
   Realiza
        │
        ▼
    VENTA
 ┌─────────────────┐
 │ id (PK)         │
 │ cliente_id (FK) │
 │ tanque_id (FK)  │
 │ litros          │
 │ tipo_carburante │
 │ fecha_hora      │
 │ precio_unitario │
 │ total           │
 └─────────────────┘
```

## 2. Descripción de Tablas

### EMPRESA
- **id**: Identificador único (autoincremento).
- **nombre**: Nombre de la estación (ej: "RaDuqQui Petrol").
- **nit**: Número de identificación tributaria.
- **direccion**: Dirección física.
- **ciudad**: Ciudad de ubicación.
- **telefono**: Teléfono de contacto.
- **stock_minimo_alerta**: Cantidad mínima de litros para alertar (ej: 1000).
- **factor_holgura**: Margen permitido sobre el promedio semanal (ej: 0.10 = 10%).
- **cupo_base_inicial**: Cupo inicial para clientes sin historial (ej: 120 litros).

### TANQUE
- **id**: Identificador único.
- **codigo**: Código del tanque (ej: "T-01").
- **tipo_carburante**: "Gasolina" o "Diésel".
- **capacidad_maxima**: Capacidad total en litros.
- **stock_minimo_seguridad**: Nivel mínimo recomendado.
- **stock_actual**: Stock en tiempo real = (SUM(ingresos) - SUM(ventas)).
- **created_at**: Fecha de creación.

### CLIENTE
- **id**: Identificador único.
- **documento**: Cédula/NIT (único).
- **nombre**: Nombre completo o razón social.
- **placa**: Placa del vehículo (único).
- **tipo_cliente**: "Particular", "Transporte Público" o "Empresa".
- **estado**: "Activo" o "Suspendido".
- **creado_en**: Fecha de registro.

### INGRESO
- **id**: Identificador único.
- **tanque_id**: Referencia al tanque.
- **litros**: Cantidad ingresada.
- **factura**: Número de factura/remisión del proveedor.
- **fecha_hora**: Timestamp del ingreso (default: CURRENT_TIMESTAMP).

Efecto: `UPDATE tanque SET stock_actual = stock_actual + litros`.

### VENTA
- **id**: Identificador único.
- **cliente_id**: Referencia al cliente.
- **tanque_id**: Referencia al tanque.
- **litros**: Cantidad vendida.
- **tipo_carburante**: "Gasolina" o "Diésel".
- **fecha_hora**: Timestamp (default: CURRENT_TIMESTAMP).
- **precio_unitario**: Precio por litro.
- **total**: litros * precio_unitario.

Efecto: `UPDATE tanque SET stock_actual = stock_actual - litros`.

## 3. Flujo de Lógica - Cálculo de Cupo

### Promedio Semanal Básico:

```
P_s = SUM(litros de ventas en últimos 28 días) / 4 semanas
```

### Límite Permitido:

```
límite = P_s * (1 + factor_holgura)
```

### Caso de Cliente Nuevo (sin historial):

```
P_s = 0
límite = cupo_base_inicial (de empresa)
```

### Autorización de Venta:

- Si `litros_solicitados <= límite` → **Autorizado**.
- Si `litros_solicitados > límite` → **Bloqueado** (se puede procesar solo con `límite`).

## 4. APIs REST Disponibles

### 1. Crear Empresa
**POST** `/configuracion/empresa`

Request:
```json
{
  "nombre": "RaDuqQui Petrol",
  "nit": "123456789",
  "direccion": "Calle Central 100",
  "ciudad": "Ciudad",
  "telefono": "+57 300 0000000",
  "stock_minimo_alerta": 120,
  "factor_holgura": 0.10,
  "cupo_base_inicial": 120
}
```

Response (201):
```json
{"empresa_id": 1}
```

### 2. Crear Tanque
**POST** `/tanques`

Request:
```json
{
  "codigo": "T-01",
  "tipo_carburante": "Gasolina",
  "capacidad_maxima": 15000,
  "stock_minimo_seguridad": 1000
}
```

Response (201):
```json
{"tanque_id": 1}
```

### 3. Listar Tanques
**GET** `/tanques`

Response (200):
```json
[
  {
    "id": 1,
    "codigo": "T-01",
    "tipo_carburante": "Gasolina",
    "capacidad_maxima": 15000,
    "stock_minimo_seguridad": 1000,
    "stock_actual": 10000,
    "created_at": "2026-06-19T12:00:00"
  }
]
```

### 4. Crear Cliente
**POST** `/clientes`

Request:
```json
{
  "documento": "11223344",
  "nombre": "Cliente Ejemplo",
  "placa": "ABC123",
  "tipo_cliente": "Particular",
  "estado": "Activo"
}
```

Response (201):
```json
{"cliente_id": 1}
```

### 5. Registrar Ingreso
**POST** `/ingresos`

Request:
```json
{
  "tanque_id": 1,
  "litros": 5000,
  "factura": "FAC-001",
  "fecha_hora": "2026-06-19T10:30:00"
}
```

Response (201):
```json
{"message": "Ingreso registrado"}
```

### 6. Consultar Límite de Compra
**GET** `/ventas/limite?documento=11223344&placa=ABC123`

Response (200):
```json
{
  "estado": "Activo",
  "limite": 132.0,
  "promedio_semanal": 120.0
}
```

### 7. Procesar Venta Controlada
**POST** `/ventas`

Request:
```json
{
  "documento": "11223344",
  "placa": "ABC123",
  "tipo_carburante": "Gasolina",
  "litros": 100,
  "tanque_id": 1,
  "precio_unitario": 8500.00
}
```

Response (201 - Autorizado):
```json
{
  "estado": "autorizado",
  "litros": 100,
  "limite": 132.0,
  "total": 850000.00
}
```

Response (400 - Bloqueado):
```json
{
  "estado": "bloqueado",
  "mensaje": "La cantidad excede el límite semanal",
  "limite": 132.0,
  "promedio_semanal": 120.0
}
```

## 5. Interfaz Web

La interfaz web en `static/index.html` incluye 4 secciones:

1. **Configuración de Empresa**: Registra parámetros globales.
2. **Registro de Tanques**: Crea tanques de depósito.
3. **Registro de Clientes**: Registra usuarios habilitados.
4. **Venta Controlada**: Consulta límites y procesa ventas.

## 6. Instalación y Ejecución

### Requisitos:
- Python 3.8+
- pip

### Pasos:

1. **Clonar/descargar el proyecto**:
   ```bash
   cd c:\examen de software
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Inicializar base de datos**:
   ```bash
   python seed_data.py
   ```

4. **Iniciar servidor**:
   ```bash
   python app.py
   ```

5. **Acceder a la interfaz**:
   ```
   http://localhost:5000/
   ```

## 7. Validaciones Implementadas

### En Venta:
- ✅ Verificar cliente (crear si no existe).
- ✅ Calcular promedio semanal (últimos 28 días).
- ✅ Comparar con límite permitido.
- ✅ Bloquear si supera límite.
- ✅ Descontar stock del tanque.
- ✅ Registrar transacción.

### En Ingreso:
- ✅ Validar tanque existe.
- ✅ Incrementar stock actual.
- ✅ Registrar factura.

### En Cliente:
- ✅ Verificar estado (Activo/Suspendido).
- ✅ Guardar automáticamente si no existe.

## 8. Ejemplo de Caso de Uso Completo

### Escenario A: Cliente nuevo intenta comprar 150L

1. Ingresa placa: `ABC123`.
2. Sistema busca cliente → No existe → **Crea cliente con cupo base = 120L**.
3. Promedio semanal = 0 → Límite = 120L.
4. Usuario solicita 150L > 120L → **Transacción bloqueada**.
5. Mensaje: "La cantidad excede el límite semanal. Límite: 120L".

### Escenario B: Cliente con historial compra dentro del límite

1. Ingresa placa: `ABC123`.
2. Sistema calcula promedio de últimas 4 semanas = 100L.
3. Límite = 100 * (1 + 0.10) = 110L.
4. Usuario solicita 90L < 110L → **Transacción autorizada**.
5. Stock se descuenta, se registra venta.
6. Nuevo promedio la próxima semana incluirá estos 90L.
