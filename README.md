# RaDuqQui Petrol - Sistema de Venta Controlada de Carburantes

## 1. Narrativa General del Sistema

RaDuqQui Petrol es una plataforma web centralizada para la gestión de inventario y venta controlada de carburantes (Gasolina y Diésel) en una estación de servicio. El sistema optimiza el control de existencias en los tanques de almacenamiento y mitiga la especulación o el sobreabastecimiento mediante un algoritmo de cupos dinámicos basado en el historial de compra de cada cliente.

## 2. Arquitectura de Módulos e Interfaces

### A. Módulo de Configuración de la Empresa
- Registra y modifica datos institucionales.
- Campos: nombre de la estación, NIT/identificación tributaria, dirección, ciudad, teléfono.
- Control crítico: alertas de stock mínimo y factor de holgura para cálculo de promedio semanal.

### B. Módulo de Gestión de Tanques de Depósito
- Representa la infraestructura física de los tanques.
- Campos: identificador, tipo de carburante, capacidad máxima y stock mínimo de seguridad.
- Dinámica: el sistema calcula el stock actual sumando ingresos y restando salidas.

### C. Módulo de Registro y Gestión de Clientes
- Controla el padrón de usuarios habilitados para compra.
- Campos: cédula/NIT, nombre completo/razón social, placa del vehículo, tipo de cliente, estado.
- Si el cliente no existe, se guarda automáticamente.

### D. Módulo de Transacciones: Ingresos y Salidas

#### Registro de Ingresos (Abastecimiento de Tanques)
- El operador registra tanque de destino, litros ingresados, factura/remisión y fecha/hora.
- Incrementa automáticamente el inventario del tanque.

#### Registro de Salidas (Venta Controlada)
- Flujo operativo:
  1. Identificación por placa o documento.
  2. Cálculo de cupo con historial de compras.
  3. Validación:
     - Si la cantidad solicitada es menor o igual al promedio más holgura, autoriza.
     - Si supera, bloquea y sugiere el límite permitido.
  4. Despacho: genera el registro de salida y descuenta stock del tanque.

## 3. Regla de Negocio: Algoritmo de Venta Controlada

El promedio semanal se calcula como:

```
P_s = Total de litros comprados en los últimos X días / Número de semanas evaluadas
```

- Se recomienda evaluar las últimas 4 semanas (28 días).
- Si el cliente es nuevo y no tiene historial, se aplica un cupo base inicial desde la configuración de la empresa.

## 4. Flujo de Usuario Ideal

1. Vehículo llega a la bomba.
2. Operador inicia sesión en la aplicación web.
3. Selecciona "Nueva Venta", ingresa placa y tipo de carburante.
4. El sistema muestra estado del cliente y límite de compra permitido.
5. Operador digita la cantidad solicitada.
6. Si excede el límite, el botón "Procesar" se deshabilita y se alerta.
7. Si está dentro del límite, se procesa la venta, actualiza el tanque y emite comprobante.

## Arquitectura propuesta

- Frontend: aplicación web ligera (tablet/terminal local).
- Backend: API REST en Python con Flask.
- Base de datos: SQLite para almacenamiento local y rápido.
- Tablas principales: `empresa`, `tanque`, `cliente`, `ingreso`, `venta`.

## Archivos incluidos

- `schema.sql`: definición del modelo de datos.
- `app.py`: ejemplo de backend con lógica de cupo y transacciones.
- `requirements.txt`: dependencias.
- `static/index.html`, `static/main.js`, `static/styles.css`: interfaz web básica.
- `seed_data.py`: script para cargar datos de ejemplo.

## Ejecutar la aplicación

1. Instalar dependencias:

```bash
pip install -r requirements.txt
```

2. Iniciar la aplicación:

```bash
python app.py
```

3. Abrir en el navegador:

```text
http://localhost:5000/
```

4. (Opcional) Cargar datos de ejemplo:

```bash
python seed_data.py
```

La interfaz web permite configurar la empresa, registrar tanques y clientes, consultar el límite de compra por cliente y procesar ventas controladas.
