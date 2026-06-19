import sqlite3
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, g

DATABASE = 'database.db'

app = Flask(__name__, static_folder='static', static_url_path='')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys = ON')
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        with open('schema.sql', 'r', encoding='utf-8') as f:
            db.executescript(f.read())
        db.commit()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = [dict(row) for row in cur.fetchall()]
    cur.close()
    return (rv[0] if rv else None) if one else rv


def execute_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    return cur.lastrowid


@app.route('/configuracion/empresa', methods=['POST'])
def crear_empresa():
    data = request.json
    required = ['nombre', 'nit', 'direccion', 'ciudad', 'stock_minimo_alerta', 'factor_holgura', 'cupo_base_inicial']
    if not all(field in data for field in required):
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    try:
        empresa_id = execute_db(
            'INSERT INTO empresa (nombre, nit, direccion, ciudad, telefono, stock_minimo_alerta, factor_holgura, cupo_base_inicial) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (data['nombre'], data['nit'], data['direccion'], data['ciudad'], data.get('telefono'), data['stock_minimo_alerta'], data['factor_holgura'], data['cupo_base_inicial'])
        )
        return jsonify({'empresa_id': empresa_id}), 201
    except sqlite3.IntegrityError as exc:
        return jsonify({'error': str(exc)}), 400


@app.route('/tanques', methods=['POST'])
def crear_tanque():
    data = request.json
    required = ['codigo', 'tipo_carburante', 'capacidad_maxima', 'stock_minimo_seguridad']
    if not all(field in data for field in required):
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    tanque_id = execute_db(
        'INSERT INTO tanque (codigo, tipo_carburante, capacidad_maxima, stock_minimo_seguridad, stock_actual) VALUES (?, ?, ?, ?, ?)',
        (data['codigo'], data['tipo_carburante'], data['capacidad_maxima'], data['stock_minimo_seguridad'], 0)
    )
    return jsonify({'tanque_id': tanque_id}), 201


@app.route('/clientes', methods=['POST'])
def crear_cliente():
    data = request.json
    required = ['documento', 'nombre', 'placa', 'tipo_cliente', 'estado']
    if not all(field in data for field in required):
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    try:
        cliente_id = execute_db(
            'INSERT INTO cliente (documento, nombre, placa, tipo_cliente, estado) VALUES (?, ?, ?, ?, ?)',
            (data['documento'], data['nombre'], data['placa'], data['tipo_cliente'], data['estado'])
        )
        return jsonify({'cliente_id': cliente_id}), 201
    except sqlite3.IntegrityError as exc:
        return jsonify({'error': str(exc)}), 400


@app.route('/ingresos', methods=['POST'])
def registrar_ingreso():
    data = request.json
    required = ['tanque_id', 'litros', 'factura']
    if not all(field in data for field in required):
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    execute_db(
        'INSERT INTO ingreso (tanque_id, litros, factura, fecha_hora) VALUES (?, ?, ?, ?)',
        (data['tanque_id'], data['litros'], data['factura'], data.get('fecha_hora', datetime.utcnow().isoformat()))
    )
    execute_db('UPDATE tanque SET stock_actual = stock_actual + ? WHERE id = ?', (data['litros'], data['tanque_id']))
    return jsonify({'message': 'Ingreso registrado'}), 201


def calcular_promedio_semanal(cliente_id, dias=28):
    fecha_inicio = datetime.utcnow() - timedelta(days=dias)
    ventas = query_db(
        'SELECT sum(litros) AS total_litros FROM venta WHERE cliente_id = ? AND fecha_hora >= ?',
        (cliente_id, fecha_inicio.isoformat()),
        one=True
    )
    total_litros = ventas['total_litros'] or 0
    semanas = dias / 7
    return total_litros / semanas


@app.route('/ventas', methods=['POST'])
def registrar_venta():
    data = request.json
    required = ['documento', 'placa', 'tipo_carburante', 'litros', 'tanque_id']
    if not all(field in data for field in required):
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    cliente = query_db('SELECT * FROM cliente WHERE documento = ? OR placa = ?', (data['documento'], data['placa']), one=True)
    if cliente is None:
        cliente_id = execute_db(
            'INSERT INTO cliente (documento, nombre, placa, tipo_cliente, estado) VALUES (?, ?, ?, ?, ?)',
            (data['documento'], data.get('nombre', 'CLIENTE NUEVO'), data['placa'], data.get('tipo_cliente', 'Particular'), 'Activo')
        )
        cliente = query_db('SELECT * FROM cliente WHERE id = ?', (cliente_id,), one=True)
    else:
        cliente_id = cliente['id']

    empresa = query_db('SELECT * FROM empresa ORDER BY id DESC LIMIT 1', one=True)
    if empresa is None:
        return jsonify({'error': 'No existe configuración de empresa'}), 400

    promedio = calcular_promedio_semanal(cliente_id)
    limite = promedio * (1 + empresa['factor_holgura'])
    if cliente['estado'] != 'Activo':
        return jsonify({'error': 'Cliente suspendido'}), 403

    if promedio == 0:
        limite = empresa['cupo_base_inicial']

    if data['litros'] > limite:
        return jsonify({
            'estado': 'bloqueado',
            'mensaje': 'La cantidad excede el límite semanal',
            'limite': limite,
            'promedio_semanal': promedio
        }), 400

    tanque = query_db('SELECT * FROM tanque WHERE id = ?', (data['tanque_id'],), one=True)
    if tanque is None or tanque['stock_actual'] < data['litros']:
        return jsonify({'error': 'Tanque inválido o stock insuficiente'}), 400

    total = data['litros'] * data.get('precio_unitario', 0)

    execute_db(
        'INSERT INTO venta (cliente_id, tanque_id, litros, tipo_carburante, fecha_hora, precio_unitario, total) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (cliente_id, data['tanque_id'], data['litros'], data['tipo_carburante'], data.get('fecha_hora', datetime.utcnow().isoformat()), data.get('precio_unitario', 0), total)
    )
    execute_db('UPDATE tanque SET stock_actual = stock_actual - ? WHERE id = ?', (data['litros'], data['tanque_id']))
    return jsonify({'estado': 'autorizado', 'litros': data['litros'], 'limite': limite, 'total': total}), 201


@app.route('/ventas/limite', methods=['GET'])
def obtener_limite():
    documento = request.args.get('documento')
    placa = request.args.get('placa')
    if not documento and not placa:
        return jsonify({'error': 'Documento o placa requerido'}), 400

    cliente = query_db('SELECT * FROM cliente WHERE documento = ? OR placa = ?', (documento, placa), one=True)
    if cliente is None:
        empresa = query_db('SELECT * FROM empresa ORDER BY id DESC LIMIT 1', one=True)
        if empresa is None:
            return jsonify({'error': 'No existe configuración de empresa'}), 400
        return jsonify({'estado': 'Habilitado', 'limite': empresa['cupo_base_inicial'], 'promedio_semanal': 0})

    promedio = calcular_promedio_semanal(cliente['id'])
    empresa = query_db('SELECT * FROM empresa ORDER BY id DESC LIMIT 1', one=True)
    limite = promedio * (1 + empresa['factor_holgura']) if promedio > 0 else empresa['cupo_base_inicial']
    return jsonify({'estado': cliente['estado'], 'limite': limite, 'promedio_semanal': promedio})


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/empresa', methods=['GET'])
def obtener_empresa():
    empresa = query_db('SELECT * FROM empresa ORDER BY id DESC LIMIT 1', one=True)
    if empresa is None:
        return jsonify({'error': 'No existe configuración de empresa'}), 400
    return jsonify(empresa)


@app.route('/tanques', methods=['GET'])
def listar_tanques():
    tanques = query_db('SELECT * FROM tanque ORDER BY codigo')
    return jsonify(tanques)


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
