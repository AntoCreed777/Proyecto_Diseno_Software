/**
 * Funcionalidad de mapas para rutas de entrega
 * Maneja la visualización de rutas de ida y regreso usando Leaflet y OSRM
 * 
 * Dependencias requeridas:
 * - Leaflet.js (para el mapa)
 * - polyline.js (para decodificar polylines de OSRM)
 */

// Variables globales
var map;
var rutasData;
var distanciaTotal;
var duracionTotal;

/**
 * Verifica que las dependencias requeridas estén disponibles
 * Realiza una verificación básica de Leaflet y polyline.js
 * @returns {boolean} True si todas las dependencias están disponibles
 */
function verificarDependencias() {
    if (typeof L === 'undefined') {
        console.error('Error: Leaflet no está disponible');
        return false;
    }
    
    if (typeof polyline === 'undefined') {
        console.warn('Advertencia: polyline.js no disponible, se usarán coordenadas directas');
        return false;
    }
    
    // Prueba rápida de decodificación
    try {
        const polylinePrueba = 'u{~vFvyys@fS]';
        polyline.decode(polylinePrueba);
        console.log('Sistema de polylines funcionando correctamente');
        return true;
    } catch (error) {
        console.warn('Error en polyline.js, se usarán coordenadas directas:', error);
        return false;
    }
}

/**
 * Inicializa el mapa de Leaflet con la configuración predeterminada
 * Crea el mapa centrado en Concepción, Chile y añade la capa base de OpenStreetMap
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
 * Función para regresar a la página anterior del usuario
 * Implementa una estrategia de fallback: primero intenta usar la página anterior
 * configurada desde Django, luego document.referrer, luego history.back(), 
 * y finalmente redirige a la página principal como último recurso
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
 * @param {Object} data - Datos de la ruta que debe contener:
 *   - {string} nombre - Nombre descriptivo de la ruta
 *   - {string} [polyline] - Polyline codificado de la ruta (opcional)
 *   - {Array<Array<number>>} [coordenadas] - Array de coordenadas [lat, lng] (opcional)
 *   - {string} [color] - Color de la línea en formato hex (opcional)
 *   - {number} [distancia_km] - Distancia de la ruta en kilómetros (opcional)
 *   - {number} [duracion_minutos] - Duración estimada en minutos (opcional)
 * @param {number} [index=0] - Índice de la ruta para colores automáticos
 * @returns {Object|null} - Objeto de polilínea de Leaflet o null si hay error
 */
function mostrarRuta(data, index = 0) {
    if (!data) {
        console.warn("No hay datos de ruta para mostrar");
        return;
    }
    
    let coordenadas = [];
    
    // Intentar decodificar polyline si está disponible y la librería está cargada
    if (data.polyline && typeof polyline !== 'undefined') {
        try {
            coordenadas = polyline.decode(data.polyline);
            console.log(`Polyline decodificada para ${data.nombre}: ${coordenadas.length} puntos`);
        } catch (error) {
            console.warn(`Error decodificando polyline de ${data.nombre}, usando coordenadas directas:`, error);
            coordenadas = data.coordenadas || [];
        }
    } else if (data.coordenadas && Array.isArray(data.coordenadas) && data.coordenadas.length > 0) {
        coordenadas = data.coordenadas;
        console.log(`Usando coordenadas directas para ${data.nombre}: ${coordenadas.length} puntos`);
    } else {
        console.error(`Sin datos válidos para renderizar ${data.nombre}`);
        return null;
    }
    
    if (coordenadas.length === 0) {
        console.warn(`No se pudieron obtener coordenadas para ${data.nombre}`);
        return null;
    }
    
    // Validar rango geográfico para Chile
    const [lat1, lng1] = coordenadas[0];
    if (!verificarRangoChile(lat1, lng1)) {
        console.warn(`Coordenadas de ${data.nombre} fuera del rango de Chile: [${lat1}, ${lng1}]`);
    }
    
    // Crear la polilínea en el mapa
    const ruta = L.polyline(coordenadas, {
        color: data.color || (index === 0 ? '#3388ff' : '#ff8833'),
        weight: 5,
        opacity: 0.8
    }).addTo(map);
    
    // Configurar popup informativo
    let popupContent = `<b>${data.nombre}</b><br>`;
    if (data.distancia_km) {
        popupContent += `Distancia: ${data.distancia_km} km<br>`;
    }
    if (data.duracion_minutos) {
        popupContent += `Duración: ${data.duracion_minutos} min<br>`;
    }
    popupContent += `Puntos: ${coordenadas.length}`;
    
    ruta.bindPopup(popupContent);
    
    return ruta;
}

/**
 * Crea marcadores de inicio y destino en el mapa con iconos personalizados
 * @param {Array<number>} coordenadasInicio - Coordenadas del punto de inicio [lat, lng]
 * @param {Array<number>} coordenadasDestino - Coordenadas del punto de destino [lat, lng]
 * @description Crea un marcador verde para el origen (Universidad de Concepción) 
 *              y un marcador azul para el destino de entrega
 */
function crearMarcadores(coordenadasInicio, coordenadasDestino) {
    // Marcador de origen (verde) - Universidad de Concepción
    L.marker(coordenadasInicio, {
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        })
    }).addTo(map).bindPopup("🏠 Universidad de Concepción");
    
    // Marcador de destino (azul) - Dirección de entrega
    L.marker(coordenadasDestino, {
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        })
    }).addTo(map).bindPopup("📦 Destino de entrega");
}

/**
 * Muestra los pasos detallados de una ruta individual como polilíneas
 * @param {Object} rutaData - Datos de la ruta que contiene:
 *   - {string} nombre - Nombre de la ruta
 *   - {Array<Object>} [pasos] - Array de pasos con coordenadas e instrucciones
 * @param {number} index - Índice de la ruta para generar colores únicos
 * @description Renderiza cada paso como una polilínea con colores diferenciados
 *              y popups informativos con instrucciones de navegación
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
 * Función para mostrar todas las rutas en el mapa
 * @param {Array<Object>} rutasArray - Array con los datos de todas las rutas, donde cada ruta contiene:
 *   - {string} nombre - Nombre descriptivo de la ruta
 *   - {string} [polyline] - Polyline codificado (opcional)
 *   - {Array<Array<number>>} [coordenadas] - Coordenadas directas (opcional)
 *   - {string} [color] - Color personalizado (opcional)
 *   - {number} [distancia_km] - Distancia en kilómetros (opcional)
 *   - {number} [duracion_minutos] - Duración en minutos (opcional)
 * @description Procesa y renderiza todas las rutas, coloca marcadores de inicio/destino,
 *              muestra pasos detallados si están disponibles y ajusta la vista del mapa
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
            if (!marcadoresColocados) {
                let coordenadas = [];
                
                // Obtener coordenadas para marcadores
                if (rutaData.polyline && typeof polyline !== 'undefined') {
                    try {
                        coordenadas = polyline.decode(rutaData.polyline);
                    } catch (error) {
                        coordenadas = rutaData.coordenadas || [];
                    }
                } else {
                    coordenadas = rutaData.coordenadas || [];
                }
                
                if (coordenadas.length > 0) {
                    const destinoCoordenada = coordenadas[coordenadas.length - 1];
                    crearMarcadores(coordenadas[0], destinoCoordenada);
                    marcadoresColocados = true;
                }
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
 * Actualiza la información mostrada en el header de la página
 * Muestra la distancia total, duración total y hace visible la sección de detalles
 * @description Utiliza las variables globales distanciaTotal y duracionTotal
 *              para actualizar los elementos DOM correspondientes
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
 * @param {Array<Object>} datosRutas - Array de datos de las rutas desde Django, donde cada ruta contiene:
 *   - {string} nombre - Nombre de la ruta
 *   - {string} [polyline] - Polyline codificado
 *   - {Array<Array<number>>} [coordenadas] - Coordenadas directas
 *   - {Object} [pasos] - Pasos detallados de navegación
 * @param {number} distTotal - Distancia total calculada en kilómetros
 * @param {number} durTotal - Duración total calculada en minutos  
 * @param {string} paginaAnt - URL de la página anterior para navegación
 * @description Inicializa el sistema completo: verifica dependencias, configura variables globales,
 *              inicializa el mapa, procesa y muestra las rutas, y actualiza la información del header
 */
function inicializarMapaRutas(datosRutas, distTotal, durTotal, paginaAnt) {
    // Verificar dependencias disponibles
    const dependenciasOK = verificarDependencias();
    
    // Asignar variables globales
    rutasData = datosRutas;
    distanciaTotal = distTotal;
    duracionTotal = durTotal;
    window.paginaAnterior = paginaAnt;
    
    console.log('Inicializando mapa de rutas:', {
        rutas: rutasData ? rutasData.length : 0,
        distancia: distTotal + ' km',
        duracion: durTotal + ' min',
        dependencias: dependenciasOK ? 'OK' : 'Parciales'
    });
    
    // Verificar que al menos Leaflet esté disponible antes de continuar
    if (typeof L === 'undefined') {
        console.error('No se puede inicializar el mapa sin Leaflet');
        return;
    }
    
    // Inicializar el mapa
    inicializarMapa();
    
    // Mostrar las rutas si existen
    if (rutasData && rutasData.length > 0) {
        mostrarRutas(rutasData);
        actualizarInformacionHeader();
        console.log('Mapa inicializado exitosamente con', rutasData.length, 'rutas');
    } else {
        console.warn('No se encontraron rutas para mostrar');
    }
}

// Hacer las funciones disponibles globalmente para el template
window.inicializarMapaRutas = inicializarMapaRutas;
window.regresarPaginaAnterior = regresarPaginaAnterior;
