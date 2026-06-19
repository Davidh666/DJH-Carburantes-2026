const empresaForm = document.getElementById('empresa-form');
const tanqueForm = document.getElementById('tanque-form');
const clienteForm = document.getElementById('cliente-form');
const ventaForm = document.getElementById('venta-form');
const verificarForm = document.getElementById('venta-verificar-form');
const limiteInfo = document.getElementById('limite-info');
const ventaResult = document.getElementById('venta-result');
const selectTanque = document.getElementById('select-tanque');

async function fetchTanques() {
  const response = await fetch('/tanques');
  if (!response.ok) return [];
  return response.json();
}

async function cargarTanques() {
  const tanques = await fetchTanques();
  selectTanque.innerHTML = '<option value="">Seleccione un tanque</option>';
  tanques.forEach(tanque => {
    const option = document.createElement('option');
    option.value = tanque.id;
    option.textContent = `${tanque.codigo} (${tanque.tipo_carburante}) - stock ${tanque.stock_actual}L`;
    selectTanque.appendChild(option);
  });
}

async function postJson(url, data) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return res.json().then(body => ({ status: res.status, body }));
}

function showMessage(element, message) {
  element.textContent = message;
}

empresaForm.addEventListener('submit', async event => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(empresaForm).entries());
  data.stock_minimo_alerta = Number(data.stock_minimo_alerta);
  data.factor_holgura = Number(data.factor_holgura);
  data.cupo_base_inicial = Number(data.cupo_base_inicial);

  const result = await postJson('/configuracion/empresa', data);
  if (result.status === 201) {
    showMessage(limiteInfo, 'Empresa registrada correctamente.');
  } else {
    showMessage(limiteInfo, 'Error: ' + result.body.error);
  }
});

tanqueForm.addEventListener('submit', async event => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(tanqueForm).entries());
  data.capacidad_maxima = Number(data.capacidad_maxima);
  data.stock_minimo_seguridad = Number(data.stock_minimo_seguridad);

  const result = await postJson('/tanques', data);
  if (result.status === 201) {
    showMessage(limiteInfo, 'Tanque registrado correctamente.');
    await cargarTanques();
  } else {
    showMessage(limiteInfo, 'Error: ' + result.body.error);
  }
});

clienteForm.addEventListener('submit', async event => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(clienteForm).entries());
  const result = await postJson('/clientes', data);
  if (result.status === 201) {
    showMessage(limiteInfo, 'Cliente registrado correctamente.');
  } else {
    showMessage(limiteInfo, 'Error: ' + result.body.error);
  }
});

verificarForm.addEventListener('submit', async event => {
  event.preventDefault();
  const documento = document.getElementById('buscar-documento').value.trim();
  const placa = document.getElementById('buscar-placa').value.trim();
  if (!documento && !placa) {
    showMessage(limiteInfo, 'Ingrese documento o placa para verificar el límite.');
    return;
  }
  const params = new URLSearchParams({ documento, placa });
  const response = await fetch('/ventas/limite?' + params.toString());
  const data = await response.json();

  if (response.ok) {
    showMessage(limiteInfo, `Estado: ${data.estado}. Límite permitido: ${data.limite.toFixed(2)} L. Promedio semanal: ${data.promedio_semanal.toFixed(2)} L.`);
  } else {
    showMessage(limiteInfo, 'Error: ' + data.error);
  }
});

ventaForm.addEventListener('submit', async event => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(ventaForm).entries());
  data.litros = Number(data.litros);
  data.tanque_id = Number(data.tanque_id);

  const result = await postJson('/ventas', data);
  if (result.status === 201) {
    showMessage(ventaResult, `Venta autorizada. Litros: ${result.body.litros}. Total: ${result.body.total}.`);
    await cargarTanques();
  } else {
    showMessage(ventaResult, 'Error: ' + (result.body.error || result.body.mensaje));
  }
});

window.addEventListener('load', () => {
  cargarTanques();
});
