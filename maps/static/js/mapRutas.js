/**
 * Funcionalidad de mapas para rutas de entrega
 * Maneja la visualización de rutas de ida y regreso usando Leaflet y OSRM
 */

// Variables globales
var map;
var rutasData;
var distanciaTotal;
var duracionTotal;

/**
 * Inicializa el mapa de Leaflet
 */
function inicializarMapa() {
    map = L.map('map', {
        zoomControl: true
    }).setView([-36.8146, -73.0509], 14);

    // Añadir capa base de OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);
}

/**
 * Función para regresar a la página anterior
 */
function regresarPaginaAnterior() {
    // Primera opción: usar la página anterior del contexto de Django
    const paginaAnterior = window.paginaAnterior;
    
    if (paginaAnterior && paginaAnterior !== '/' && paginaAnterior !== window.location.href) {
        window.location.href = paginaAnterior;
    } else if (document.referrer && document.referrer !== window.location.href) {
        // Segunda opción: usar document.referrer
        window.location.href = document.referrer;
    } else if (window.history.length > 1) {
        // Tercera opción: usar history.back()
        window.history.back();
    } else {
        // Fallback: ir a la página principal
        window.location.href = '/home/';
    }
}

/**
 * Verifica si las coordenadas están en el rango válido para Chile
 * @param {number} lat - Latitud
 * @param {number} lng - Longitud
 * @returns {boolean} - True si está en rango válido
 */
function verificarRangoChile(lat, lng) {
    return lat >= -56 && lat <= -17 && lng >= -109 && lng <= -66;
}

/**
 * Función para mostrar una ruta individual en el mapa
 * @param {Object} data - Datos de la ruta
 * @param {number} index - Índice de la ruta
 * @returns {Object} - Objeto de polilínea de Leaflet
 */
function mostrarRuta(data, index = 0) {
    if (!data || !data.coordenadas || data.coordenadas.length === 0) {
        console.log("No hay datos de ruta para mostrar");
        return;
    }
    
    console.log(`Datos de ${data.nombre} recibidos:`, data);
    console.log("Número de coordenadas:", data.coordenadas.length);
    console.log("Primera coordenada:", data.coordenadas[0]);
    console.log("Última coordenada:", data.coordenadas[data.coordenadas.length - 1]);
    
    // Verificar si las coordenadas están en rango válido para Chile
    const [lat1, lng1] = data.coordenadas[0];
    console.log(`${data.nombre} - Primera coord - Lat: ${lat1}, Lng: ${lng1}`);
    
    if (!verificarRangoChile(lat1, lng1)) {
        console.warn(`⚠️ Coordenadas de ${data.nombre} parecen estar fuera del rango de Chile!`);
        console.warn("Rango válido: Lat [-56, -17], Lng [-109, -66]");
    } else {
        console.log(`✅ Coordenadas de ${data.nombre} en rango válido para Chile`);
    }
    
    // Crear la polilínea principal
    const ruta = L.polyline(data.coordenadas, {
        color: data.color || (index === 0 ? '#3388ff' : '#ff8833'),
        weight: 5,  // Línea visible
        opacity: 0.8
    }).addTo(map);
    
    // Agregar popup con información
    let popupContent = `<b>${data.nombre}</b><br>`;
    if (data.distancia_km) {
        popupContent += `Distancia: ${data.distancia_km} km<br>`;
    }
    if (data.duracion_minutos) {
        popupContent += `Duración: ${data.duracion_minutos} min<br>`;
    }
    popupContent += `Puntos: ${data.coordenadas.length}`;
    
    ruta.bindPopup(popupContent);
    
    return ruta;
}

/**
 * Crea marcadores de inicio y destino
 * @param {Array} coordenadasInicio - Coordenadas del punto de inicio
 * @param {Array} coordenadasDestino - Coordenadas del punto de destino
 */
function crearMarcadores(coordenadasInicio, coordenadasDestino) {
    // Marcador de inicio (verde)
    L.marker(coordenadasInicio, {
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        })
    }).addTo(map).bindPopup("🏠 Inicio");
    
    // Marcador de destino (azul)
    L.marker(coordenadasDestino, {
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        })
    }).addTo(map).bindPopup("📦 Destino");
}

/**
 * Muestra los pasos detallados de una ruta
 * @param {Object} rutaData - Datos de la ruta
 * @param {number} index - Índice de la ruta
 */
function mostrarPasosRuta(rutaData, index) {
    if (rutaData.pasos && rutaData.pasos.length > 0) {
        console.log(`Mostrando pasos de ${rutaData.nombre}:`, rutaData.pasos.length);
        rutaData.pasos.forEach((paso, pasoIndex) => {
            if (paso.coordenadas && paso.coordenadas.length > 0) {
                const colorPaso = `hsl(${((index * 180) + (pasoIndex * 30)) % 360}, 70%, 50%)`;
                L.polyline(paso.coordenadas, {
                    color: colorPaso,
                    weight: 2,
                    opacity: 0.4
                }).addTo(map).bindPopup(`${rutaData.nombre}<br>${paso.nombre || 'Paso ' + (pasoIndex + 1)}<br>${paso.instruccion || ''}`);
            }
        });
    }
}

/**
 * Función para mostrar todas las rutas
 * @param {Array} rutasArray - Array con los datos de todas las rutas
 */
function mostrarRutas(rutasArray) {
    if (!rutasArray || rutasArray.length === 0) {
        console.log("No hay rutas para mostrar");
        return;
    }
    
    const todasLasRutas = [];
    let marcadoresColocados = false;
    
    rutasArray.forEach((rutaData, index) => {
        const ruta = mostrarRuta(rutaData, index);
        if (ruta) {
            todasLasRutas.push(ruta);
            
            // Solo colocar marcadores una vez (usando la primera ruta)
            if (!marcadoresColocados && rutaData.coordenadas.length > 0) {
                const destinoCoordenada = rutaData.coordenadas[rutaData.coordenadas.length - 1];
                crearMarcadores(rutaData.coordenadas[0], destinoCoordenada);
                marcadoresColocados = true;
            }
            
            // Mostrar pasos individuales si están disponibles
            mostrarPasosRuta(rutaData, index);
        }
    });
    
    // Ajustar la vista del mapa para mostrar todas las rutas
    if (todasLasRutas.length > 0) {
        const group = new L.featureGroup(todasLasRutas);
        map.fitBounds(group.getBounds(), { padding: [20, 20] });
    }
}

/**
 * Actualiza la información mostrada en el header
 */
function actualizarInformacionHeader() {
    if (distanciaTotal !== undefined && duracionTotal !== undefined) {
        document.getElementById('distancia').textContent = distanciaTotal.toFixed(2);
        document.getElementById('duracion').textContent = duracionTotal.toFixed(1);
        document.getElementById('ruta-detalles').style.display = 'block';
    }
}

/**
 * Función principal que se ejecuta cuando se carga la página
 * @param {Array} datosRutas - Datos de las rutas desde Django
 * @param {number} distanciaTotal - Distancia total calculada
 * @param {number} duracionTotal - Duración total calculada
 * @param {string} paginaAnterior - URL de la página anterior
 */
function inicializarMapaRutas(datosRutas, distTotal, durTotal, paginaAnt) {
    // Asignar variables globales
    rutasData = datosRutas;
    distanciaTotal = distTotal;
    duracionTotal = durTotal;
    window.paginaAnterior = paginaAnt;
    
    // Inicializar el mapa
    inicializarMapa();
    
    // Mostrar las rutas si existen
    if (rutasData && rutasData.length > 0) {
        mostrarRutas(rutasData);
        actualizarInformacionHeader();
    } else {
        console.warn("No se encontraron rutas para mostrar");
    }
}

// Hacer las funciones disponibles globalmente para el template
window.inicializarMapaRutas = inicializarMapaRutas;
window.regresarPaginaAnterior = regresarPaginaAnterior;
