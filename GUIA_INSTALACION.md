# Guía de Instalación y Ejecución - RaDuqQui Petrol

## Opción 1: Instalación Manual de Python (Recomendado)

### Paso 1: Descargar Python 3.10 o superior
1. Ve a https://www.python.org/downloads/windows/
2. Descarga **Python 3.10.x** o superior (exe instalador).
3. **IMPORTANTE**: Al instalar, marca la casilla **"Add Python to PATH"**.
4. Completa la instalación.

### Paso 2: Verificar Instalación
Abre PowerShell y ejecuta:
```powershell
python --version
```

Si responde algo como `Python 3.10.11`, está correcto. Si no reconoce el comando, repite el Paso 1 asegurándote de marcar "Add Python to PATH".

### Paso 3: Instalar Dependencias
```powershell
cd "c:\examen de software"
pip install -r requirements.txt
```

### Paso 4: Cargar Datos de Ejemplo (Opcional)
```powershell
python seed_data.py
```

### Paso 5: Ejecutar la Aplicación
```powershell
python app.py
```

Deberías ver:
```
 * Running on http://0.0.0.0:5000
 * Press CTRL+C to quit
```

### Paso 6: Abrir en el Navegador
Abre `http://localhost:5000/` en tu navegador web.

---

## Opción 2: Usando Anaconda (Alternativa)

Si tienes Anaconda instalada:

```powershell
conda create -n raduqui python=3.10
conda activate raduqui
cd "c:\examen de software"
pip install -r requirements.txt
python app.py
```

---

## Troubleshooting

### Error: "python: El término 'python' no se reconoce"

**Solución:**
1. Reinstala Python desde https://www.python.org/downloads/windows/
2. **Marca la casilla "Add Python to PATH"** al instalar.
3. Reinicia PowerShell después de instalar.

### Error: "No module named 'flask'"

**Solución:**
```powershell
pip install -r requirements.txt
```

### Puerto 5000 ya está en uso

**Solución:**
Edita `app.py` y cambia la última línea:
```python
app.run(host='0.0.0.0', port=8000, debug=True)  # cambiar puerto a 8000
```

Luego accede a `http://localhost:8000/`

### La base de datos ya existe y quiero reiniciarla

**Solución:**
```powershell
Remove-Item database.db -Force
python seed_data.py
python app.py
```

---

## Estructura del Proyecto

```
c:\examen de software\
├── app.py                       # Backend Flask principal
├── schema.sql                   # Definición de tablas
├── seed_data.py                 # Script de datos de ejemplo
├── requirements.txt             # Dependencias Python
├── database.db                  # Base de datos SQLite (se crea automático)
├── static/
│   ├── index.html              # Interfaz web
│   ├── main.js                 # Lógica frontend
│   ├── styles.css              # Estilos CSS
├── README.md                    # Información general
└── DOCUMENTACION_TECNICA.md     # Esta documentación
```

---

## Uso de la Interfaz Web

### 1. Configuración de la Empresa
- Completa los datos de la estación de servicio.
- Marca los parámetros críticos (cupo base, holgura, stock mínimo).
- Haz clic en "Guardar empresa".

### 2. Registro de Tanques
- Ingresa código del tanque (ej: T-01).
- Selecciona tipo de carburante (Gasolina o Diésel).
- Ingresa capacidad máxima.
- Haz clic en "Registrar tanque".

### 3. Registro de Clientes (Opcional)
- Puedes registrar clientes previamente, o se crean automáticamente en la primera compra.
- Completa documento, nombre, placa, tipo y estado.
- Haz clic en "Registrar cliente".

### 4. Venta Controlada
- **Verificar límite**: Ingresa documento o placa y haz clic en "Ver límite".
- **Procesar venta**: Completa los datos de la venta y haz clic en "Procesar venta".
- Si la cantidad excede el límite, verás un mensaje de advertencia.

---

## Pruebas Recomendadas

### Prueba 1: Crear empresa
1. Rellena la sección "Configuración de la Empresa".
2. Espera a ver el mensaje de éxito.

### Prueba 2: Crear tanques
1. Crea un tanque con código `T-01`, tipo `Gasolina`, capacidad `15000`, stock mínimo `1000`.
2. Crea otro tanque con código `T-02`, tipo `Diésel`, capacidad `12000`, stock mínimo `1000`.

### Prueba 3: Registrar ingreso (desde la terminal o API)
```bash
curl -X POST http://localhost:5000/ingresos -H "Content-Type: application/json" -d "{\"tanque_id\": 1, \"litros\": 5000, \"factura\": \"FAC-001\"}"
```

### Prueba 4: Procesar venta
1. Ingresa documento: `11223344`.
2. Ingresa placa: `ABC123`.
3. Selecciona carburante: `Gasolina`.
4. Ingresa litros: `100`.
5. Selecciona tanque: `T-01`.
6. Haz clic en "Procesar venta".

---

## Comandos Útiles

```powershell
# Ir al directorio del proyecto
cd "c:\examen de software"

# Instalar dependencias
pip install -r requirements.txt

# Cargar datos de ejemplo
python seed_data.py

# Iniciar servidor
python app.py

# Acceder a la interfaz
# Abre http://localhost:5000/ en tu navegador

# Detener servidor
# Presiona Ctrl+C en PowerShell
```

---

## Notas Importantes

- La base de datos es **SQLite** (almacenamiento local).
- Todas las transacciones se guardan automáticamente.
- El cálculo del promedio semanal se realiza en tiempo real.
- Si un cliente es nuevo y sin historial, se le asigna el `cupo_base_inicial`.
- Las alertas de stock mínimo se pueden consultar en los tanques.

¡El proyecto está listo para usar!
