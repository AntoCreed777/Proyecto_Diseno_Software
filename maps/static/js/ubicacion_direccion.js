/**
 * Funcionalidad específica para mostrar ubicación de una dirección en el mapa
 * Maneja la visualización de un punto específico en el mapa usando Leaflet
 * 
 * Archivos relacionados:
 * - Template: ubicacion_direccion.html
 * - Estilos: ubicacion_direccion.css
 * - Vista: map_direccion (en views.py)
 * 
 * Dependencias requeridas:
 * - Leaflet.js (para el mapa)
 */

// Variables globales
var map;
var coordenadasUbicacion;
var paginaAnterior;

/**
 * Verifica que Leaflet esté disponible
 * @returns {boolean} True si Leaflet está disponible
 */
function verificarDependencias() {
    if (typeof L === 'undefined') {
        console.error('Error: Leaflet no está disponible');
        return false;
    }
    
    console.log('Leaflet disponible correctamente');
    return true;
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
 * Crea un marcador en el mapa para la ubicación especificada
 * @param {Array<number>} coordenadas - Coordenadas del punto [lat, lng]
 * @param {string} direccion - Dirección textual del punto
 * @description Crea un marcador azul para la ubicación y centra el mapa en ella
 */
function crearMarcadorUbicacion(coordenadas, direccion) {
    // Verificar que las coordenadas sean válidas
    if (!coordenadas || coordenadas.length !== 2) {
        console.error('Coordenadas inválidas:', coordenadas);
        return;
    }
    
    const [lat, lng] = coordenadas;
    
    // Verificar rango para Chile
    if (!verificarRangoChile(lat, lng)) {
        console.warn('Coordenadas fuera del rango de Chile:', lat, lng);
    }
    
    // Crear marcador con icono azul
    const marcador = L.marker([lat, lng], {
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        })
    }).addTo(map);
    
    // Añadir popup con la dirección
    marcador.bindPopup(`📍 ${direccion}`).openPopup();
    
    // Centrar el mapa en la ubicación
    map.setView([lat, lng], 16);
    
    console.log('Marcador creado en:', lat, lng);
}

/**
 * Confirma que la ubicación mostrada es correcta
 * Redirige a la página anterior con las coordenadas y flag de confirmación
 */
function confirmarUbicacion() {
    if (!coordenadasUbicacion) {
        console.error('No hay coordenadas disponibles para confirmar');
        return;
    }
    
    // Deshabilitar botones para evitar múltiples clics
    deshabilitarBotones();
    
    // Construir URL con parámetros
    const url = new URL(paginaAnterior, window.location.origin);
    url.searchParams.set('ubicacion_confirmada', 'true');
    url.searchParams.set('lat', coordenadasUbicacion[0]);
    url.searchParams.set('lng', coordenadasUbicacion[1]);
    
    console.log('Ubicación confirmada:', {
        coordenadas: coordenadasUbicacion,
        url: url.toString()
    });
    
    // Redirigir a la página anterior con los parámetros
    window.location.href = url.toString();
}

/**
 * Rechaza la ubicación mostrada como incorrecta
 * Redirige a la página anterior con flag de rechazo
 */
function rechazarUbicacion() {
    // Deshabilitar botones para evitar múltiples clics
    deshabilitarBotones();
    
    // Construir URL con parámetros
    const url = new URL(paginaAnterior, window.location.origin);
    url.searchParams.set('ubicacion_confirmada', 'false');
    
    console.log('Ubicación rechazada, regresando a:', url.toString());
    
    // Redirigir a la página anterior con el flag
    window.location.href = url.toString();
}

/**
 * Deshabilita los botones de confirmación para evitar múltiples clics
 */
function deshabilitarBotones() {
    const btnConfirmar = document.getElementById('btn-confirmar');
    const btnRechazar = document.getElementById('btn-rechazar');
    
    if (btnConfirmar) {
        btnConfirmar.disabled = true;
        btnConfirmar.innerHTML = '<span>⏳</span><span>Procesando...</span>';
    }
    
    if (btnRechazar) {
        btnRechazar.disabled = true;
        btnRechazar.innerHTML = '<span>⏳</span><span>Procesando...</span>';
    }
}

/**
 * Función principal que se ejecuta cuando se carga la página
 * @param {Array<number>} coordenadas - Coordenadas de la ubicación [lat, lng]
 * @param {string} paginaAnt - URL de la página anterior para navegación
 * @description Inicializa el sistema completo: verifica dependencias, configura variables globales,
 *              inicializa el mapa, crea el marcador de ubicación
 */
function inicializarMapaUbicacion(coordenadas, paginaAnt) {
    // Verificar dependencias disponibles
    const dependenciasOK = verificarDependencias();
    
    // Asignar variables globales
    coordenadasUbicacion = coordenadas;
    paginaAnterior = paginaAnt;
    window.paginaAnterior = paginaAnt;
    
    console.log('Inicializando mapa de ubicación:', {
        coordenadas: coordenadas,
        dependencias: dependenciasOK ? 'OK' : 'Error'
    });
    
    // Verificar que Leaflet esté disponible antes de continuar
    if (!dependenciasOK) {
        console.error('No se puede inicializar el mapa sin Leaflet');
        return;
    }
    
    // Inicializar el mapa
    inicializarMapa();
    
    // Crear marcador de ubicación
    const direccion = document.getElementById('direccion-texto')?.textContent || 'Ubicación';
    crearMarcadorUbicacion(coordenadas, direccion);
}

// Hacer las funciones disponibles globalmente para el template
window.inicializarMapaUbicacion = inicializarMapaUbicacion;
window.regresarPaginaAnterior = regresarPaginaAnterior;
window.confirmarUbicacion = confirmarUbicacion;
window.rechazarUbicacion = rechazarUbicacion;
