
// Inicializa el mapa con botones de zoom
var map = L.map('map', {
    zoomControl: true
}).setView([-36.8146, -73.0509], 14);

// Añade una capa base
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19
}).addTo(map);

/**
 * Función para obtener coordenadas a partir de una dirección
 *
 * @param {string} direccion - Dirección a buscar
 * @returns {Object} - Objeto con latitud y longitud
 */
async function obtenerCoordenadas(direccion) {
    const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(direccion)}&format=json`;

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (data && data.length > 0) {
            if (data.length > 1) {
                console.log("Se encontraron múltiples resultados. Usando el primero.");
            }

            const lat = data[0].lat;
            const lon = data[0].lon;
            console.log(`Coordenadas de "${direccion}": Latitud ${lat}, Longitud ${lon}`);
            return { lat, lon };
        } else {
            console.log("No se encontraron resultados para la dirección.");
            return null;
        }
    } catch (error) {
        console.error("Error al obtener coordenadas:", error);
    }
}

/**
 * Función para encontrar el nombre de la calle a partir de coordenadas
 *
 * Idealmente las coordenadas deberían ser de un nodo, pero se puede usar cualquier coordenada
 *
 * @param {number} lat - Latitud
 * @param {number} lon - Longitud
 * @returns {string} - Nombre de la calle o "Sin nombre"
 */
async function encontrarNombreCalle(lat, lon) {
    const query = `
        [out:json];
            way["highway"](around:15, ${lat}, ${lon});
        out body;
    `;
    const url = `https://overpass-api.de/api/interpreter?data=${encodeURIComponent(query)}`;

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (data.elements && data.elements.length > 0) {
            for (const way of data.elements) {
                if (way.tags?.name) {
                    return way.tags.name;
                }
            }
        }

        return "Sin nombre";
    } catch (error) {
        console.error("Error al obtener el nombre de la calle:", error);
        return "Sin nombre";
    }
}


/**
 * Función para mostrar calles cercanas a una ubicación
 *
 * @param {number} lat - Latitud
 * @param {number} lon - Longitud
 * @param {number} radius - Radio de búsqueda en metros
 */
async function mostrarCallesCercanas(lat, lon, radius = 500) {
    // API de Overpass para obtener calles cercanas
    const query = `
        [out:json];
        (
            way["highway"](around:${radius}, ${lat}, ${lon});
        );
        out geom;`;

    const url = `https://overpass-api.de/api/interpreter?data=${encodeURIComponent(query)}`;

    try {
        const response = await fetch(url);
        const data = await response.json();

        // Procesar y añadir calles al mapa
        data.elements.forEach(element => {
            if (element.type === 'way' && element.geometry) {
                const latlngs = element.geometry.map(coord => [coord.lat, coord.lon]);
                L.polyline(latlngs, { color: 'blue', weight: 4 }).addTo(map)
                    .bindPopup(`Calle: ${element.tags.name || 'Desconocida'}`);
            }
        });
    } catch (error) {
        console.error("Error al obtener las calles principales:", error);
    }
}

/**
 * Función para calcular la distancia entre dos puntos usando la fórmula de Haversine
 *
 * @param {number} lat1 - Latitud del primer punto
 * @param {number} lon1 - Longitud del primer punto
 * @param {number} lat2 - Latitud del segundo punto
 * @param {number} lon2 - Longitud del segundo punto
 * @returns {number} - Distancia en metros
 */
function haversineDist(lat1, lon1, lat2, lon2) {
    const R = 6371000; // radio de la Tierra en metros
    const toRad = angle => angle * Math.PI / 180;

    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);

    const a = Math.sin(dLat/2) ** 2 +
            Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
            Math.sin(dLon/2) ** 2;

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c; // distancia en metros
}

/**
 * Función para encontrar el nodo más cercano de un array a un punto dado
 *
 * @param {number} lat - Latitud del punto
 * @param {number} lon - Longitud del punto
 * @param {Array} nodos - Array de nodos a comparar
 * @returns {Object} - Nodo más cercano
 */
function nodoMasCercano(lat, lon, nodos) {
    let nodoCercano = null;
    let minDist = Infinity;

    nodos.forEach(nodo => {
        const dist = haversineDist(lat, lon, nodo.lat, nodo.lon);
        if(dist < minDist) {
            minDist = dist;
            nodoCercano = nodo;
        }
    });

    return nodoCercano;
}

/**
 * Función para mostrar el nodo más cercano a una ubicación y añade un marcador
 *
 * @param {number} lat - Latitud
 * @param {number} lon - Longitud
 * @param {number} radius - Radio de búsqueda en metros
 */
async function mostrarNodoCercanoConMarcador(lat, lon, radius = 100) {
    const query = `
        [out:json];
        way(around:${radius},${lat},${lon})["highway"];
        out body;
    `;
    const url = `https://overpass-api.de/api/interpreter?data=${encodeURIComponent(query)}`;

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (!data.elements || data.elements.length === 0) {
            console.log("No se encontraron calles cercanas");
            return;
        }

        // Extrae los nodos de los `way`
        const nodeIds = data.elements.flatMap(way => way.nodes);

        // Otra consulta para obtener los nodos de los `way`
        const nodesQuery = `
            [out:json];
            node(id:${nodeIds.join(',')});
            out body;
        `;
        const nodesUrl = `https://overpass-api.de/api/interpreter?data=${encodeURIComponent(nodesQuery)}`;

        const nodesResponse = await fetch(nodesUrl);
        const nodesData = await nodesResponse.json();

        if (!nodesData.elements || nodesData.elements.length === 0) {
            console.log("No se encontraron nodos asociados a las calles");
            return;
        }

        // Encuentra el nodo más cercano y coloca un marcador
        const nodo = nodoMasCercano(lat, lon, nodesData.elements);

        let nameCalleNodo = await encontrarNombreCalle(nodo.lat, nodo.lon);

        if (nodo) {
            L.marker([nodo.lat, nodo.lon])
                .addTo(map)
                .bindPopup(`Nodo en calle: ${nameCalleNodo ? nameCalleNodo : "Sin nombre"}`)
                //.openPopup();
        } else {
            console.log("No se encontró ningún nodo cercano");
        }

        return nodo;

    } catch (error) {
        console.error("Error al obtener datos:", error);
    }
}

/**
 * Función para calcular la ruta más corta entre dos nodos, y agregar marcadores
 *
 * @param {number} lat1 - Latitud del primer nodo
 * @param {number} lon1 - Longitud del primer nodo
 * @param {number} lat2 - Latitud del segundo nodo
 * @param {number} lon2 - Longitud del segundo nodo
 */
async function calcularRutaMasCortaEntreNodos(lat1, lon1, lat2, lon2) {
    let nodo1 = await mostrarNodoCercanoConMarcador(lat1, lon1);
    let nodo2 = await mostrarNodoCercanoConMarcador(lat2, lon2);

    if (!nodo1 || !nodo2) {
        console.log("No se encontraron nodos cercanos");
        return;
    }

    // URL de OSRM para calcular la ruta
    const url = `https://router.project-osrm.org/route/v1/driving/${nodo1.lon},${nodo1.lat};${nodo2.lon},${nodo2.lat}?overview=full&steps=true`;

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (data.routes && data.routes.length > 0 && data.routes[0].legs.length > 0 && data.routes[0].legs[0].steps.length > 0) {       
            const steps = data.routes[0].legs[0].steps;

            steps.forEach(step => {
                const name = step.name || "Sin nombre";

                const polylineDecoded = polyline.decode(step.geometry); // Decodifica la geometría
                const coordinates = polylineDecoded.map(coord => [coord[0], coord[1]]);

                // Crear una línea en el mapa para cada tramo
                L.polyline(coordinates, { color: 'red', weight: 4 }).addTo(map)
                    .bindPopup(`Calle: ${name}`);
            });

        } else {
            console.log("No se encontró una ruta entre los nodos");
        }
    } catch (error) {
        console.error("Error calculando la ruta:", error);
    }
}

