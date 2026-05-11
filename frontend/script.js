// ============================================================
// ESTADO GLOBAL DE LA UI
// Guardan qué botón de selección está activo en cada momento.
// Se actualizan con setSexo() y setObj() al hacer clic.
// ============================================================
let sexo    = 'H';              // 'H' = Hombre | 'M' = Mujer
let objetivo = 'perder_grasa'; // 'perder_grasa' | 'ganar_musculo'


// ============================================================
// CONSTANTES DE RENDERIZADO
// Definidas aquí arriba para que sean fáciles de modificar
// sin tener que buscarlas dentro de las funciones.
// ============================================================

// Orden exacto en que se muestran los días en la tabla semanal
const DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];

// Iconos para cada momento del día; usamos un objeto para poder
// recorrerlo con Object.entries() y obtener clave + valor juntos
const ICONOS = {
    desayuno : '☕',
    comida   : '🍽',
    cena     : '🌙'
};


// ============================================================
// FUNCIONES DE ESTADO DE LA UI (botones de selección)
// ============================================================

// Cambia el sexo seleccionado y resalta visualmente el botón correcto.
// La clase CSS 'active' es la que cambia el estilo del botón.
function setSexo(val) {
    sexo = val;
    document.getElementById('btn-h').classList.toggle('active', val === 'H');
    document.getElementById('btn-m').classList.toggle('active', val === 'M');
}

// Cambia el objetivo seleccionado y resalta visualmente el botón correcto.
function setObj(val) {
    objetivo = val;
    document.getElementById('btn-perder').classList.toggle('active', val === 'perder_grasa');
    document.getElementById('btn-ganar').classList.toggle('active', val === 'ganar_musculo');
}


// ============================================================
// FUNCIÓN PRINCIPAL: recoge el formulario y llama al backend
// ============================================================
async function generarPlan() {

    // --- Leer campos del formulario ---
    // El operador || actúa como valor por defecto si el campo está vacío
    const nombre = document.getElementById('nombre').value.trim() || 'Usuario';
    const edad   = parseInt(document.getElementById('edad').value)    || 25;
    const peso   = parseFloat(document.getElementById('peso').value)  || 70;
    const talla  = parseFloat(document.getElementById('talla').value) || 175;

    // Convertimos los checkboxes marcados en un array de strings.
    // querySelectorAll devuelve una NodeList; el spread [...] la convierte
    // en Array para poder usar .map().
    const condiciones = [...document.querySelectorAll('.check-item input:checked')]
                            .map(c => c.value);

    // --- Bloquear botón durante la petición ---
    // Evita que el usuario haga clic varias veces mientras espera respuesta
    const btn = document.getElementById('btn');
    btn.disabled   = true;
    btn.textContent = 'Analizando tu perfil...';
    document.getElementById('result').innerHTML =
        '<p class="loading">Consultando al Sistema Experto...</p>';

    // --- Construir el objeto que se enviará al backend ---
    // Debe coincidir exactamente con el modelo Pydantic de FastAPI
    const datosUsuario = {
        nombre   : nombre,
        edad     : edad,
        peso     : peso,
        talla    : talla,
        sexo     : sexo,      // valor de la variable global
        objetivo : objetivo,  // valor de la variable global
        salud    : condiciones
    };

    try {
        // Petición POST a la API de FastAPI (Uvicorn corre en el puerto 8000)
        const res = await fetch('http://127.0.0.1:8000/generar-plan', {
            method  : 'POST',
            headers : { 'Content-Type': 'application/json' },
            body    : JSON.stringify(datosUsuario)
        });

        // Si el servidor devuelve un código de error (4xx / 5xx),
        // leemos el detalle y lanzamos un Error para que lo capture el catch
        if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.detail || 'Error en el servidor');
        }

        // FastAPI devuelve: { "plan": { ... }, "status": "success" }
        const data = await res.json();

        // Pintamos el plan en pantalla pasando los datos del motor experto
        renderPlan(data.plan, condiciones);

    } catch (e) {
        // Captura errores de red (servidor apagado) o errores lanzados arriba
        console.error('Error detallado:', e);
        document.getElementById('result').innerHTML = `
            <div class="error">
                <p><strong>Error de conexión:</strong> No se pudo contactar con el Sistema Experto.</p>
                <small>Asegúrate de que el servidor (Uvicorn) esté corriendo en el puerto 8000.</small>
            </div>`;
    } finally {
        // El bloque finally se ejecuta siempre, haya error o no.
        // Restauramos el botón para que el usuario pueda volver a intentarlo.
        btn.disabled    = false;
        btn.textContent = 'Generar mi plan personalizado';
    }
}


// ============================================================
// FUNCIONES DE RENDERIZADO
// Cada función crea una pieza del resultado final usando
// las plantillas <template> del HTML en vez de strings de HTML.
// ============================================================

// Clona una <template> del HTML por su id y devuelve el elemento raíz.
// cloneNode(true) copia el nodo Y todos sus hijos (deep clone).
// .content es la propiedad especial del elemento <template>;
// .firstElementChild es el primer hijo real (ignora nodos de texto vacíos).
function clonarTemplate(id) {
    return document.getElementById(id).content.cloneNode(true).firstElementChild;
}

// ─── Tarjeta de calorías ────────────────────────────────────
function crearCardCalorias(calorias) {
    const card = clonarTemplate('tpl-plan-card');
    card.querySelector('.card-title').textContent = 'Calorías diarias calculadas';
    // innerHTML aquí es seguro porque los datos vienen del backend,
    // no de inputs libres del usuario
    card.querySelector('.card-body').innerHTML =
        `<span class="kcal-num">${calorias || '--'}</span>
         <span class="kcal-unit">kcal / día</span>`;
    return card;
}

// ─── Fila de una comida (desayuno / comida / cena) ──────────
// Usamos textContent (no innerHTML) para los datos del usuario:
// evita inyección de HTML accidental si el backend devuelve caracteres especiales
function crearMealRow(icono, nombre, comida) {
    const row = clonarTemplate('tpl-meal-row');
    row.querySelector('.meal-icon').textContent = icono;
    row.querySelector('.meal-name').textContent = nombre;
    row.querySelector('.meal-food').textContent = comida || '—';
    return row;
}

// ─── Bloque de un día completo (p.ej. "Lunes") ──────────────
// Recibe el nombre del día y el objeto con desayuno/comida/cena
function crearDayBlock(dia, datos) {
    const block = clonarTemplate('tpl-day-block');
    block.querySelector('.day-name').textContent = dia;

    const mealsContainer = block.querySelector('.meals');

    // Recorremos ICONOS para generar una fila por cada momento del día.
    // Object.entries() devuelve pares [clave, valor], p.ej. ['desayuno', '☕']
    for (const [momento, icono] of Object.entries(ICONOS)) {
        // Capitalizamos la primera letra para mostrarla en pantalla
        const label = momento.charAt(0).toUpperCase() + momento.slice(1);
        mealsContainer.appendChild(
            crearMealRow(icono, label, datos[momento])
        );
    }
    return block;
}

// ─── Tarjeta completa de dieta semanal ──────────────────────
// Itera sobre DIAS (en orden) y añade un bloque por cada día
function crearCardDieta(dietaSemanal) {
    const card = clonarTemplate('tpl-plan-card');
    card.querySelector('.card-title').textContent = 'Dieta semanal sugerida';
    const body = card.querySelector('.card-body');

    for (const dia of DIAS) {
        const datos = dietaSemanal?.[dia]; // ?. evita error si dietaSemanal es null
        if (!datos) continue;             // si ese día no tiene datos, lo saltamos
        body.appendChild(crearDayBlock(dia, datos));
    }
    return card;
}

// ─── Tarjeta de plan de ejercicio ───────────────────────────
function crearCardEjercicio(ejercicio) {
    const card = clonarTemplate('tpl-plan-card');
    card.querySelector('.card-title').textContent = 'Plan de Ejercicio';

    const p = document.createElement('p');
    p.textContent = ejercicio || 'Caminata diaria y entrenamiento de fuerza moderado.';
    card.querySelector('.card-body').appendChild(p);
    return card;
}

// ─── Tarjeta de avisos de salud (solo si hay condiciones) ───
function crearCardAvisos(aviso) {
    const card = clonarTemplate('tpl-plan-card');
    card.querySelector('.card-title').textContent = 'Avisos de Salud';

    const div = document.createElement('div');
    div.className   = 'alert-box';
    div.textContent = aviso || 'Sigue las recomendaciones médicas para tu condición.';
    card.querySelector('.card-body').appendChild(div);
    return card;
}


// ============================================================
// ORQUESTADOR DE RENDERIZADO
// Limpia el área de resultados y monta todas las tarjetas
// en el orden correcto usando las funciones anteriores.
// ============================================================
function renderPlan(plan, condiciones) {
    const result = document.getElementById('result');
    result.innerHTML = ''; // limpiamos el contenido anterior

    result.appendChild(crearCardCalorias(plan.calorias));
    result.appendChild(crearCardDieta(plan.dieta_semanal));
    result.appendChild(crearCardEjercicio(plan.ejercicio));

    // La tarjeta de avisos solo se añade si el usuario marcó alguna condición
    if (condiciones.length > 0) {
        result.appendChild(crearCardAvisos(plan.aviso));
    }
}