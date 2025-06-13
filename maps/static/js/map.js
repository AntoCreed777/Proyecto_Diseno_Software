
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

async function obtenerDireccion(latitud, longitud) {
    const url = `https://nominatim.openstreetmap.org/reverse?lat=${encodeURIComponent(latitud)}&lon=${encodeURIComponent(longitud)}&format=json`

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (data) {
            const direccion = data.display_name

            console.log(`Direccion de Latitud ${latitud}", Longitud ${longitud}: "${direccion}"`);
            return direccion;
        } else {
            console.log("No se encontraron resultados para la direccion");
            return null;
        }
    } catch (error) {
        console.error("Error al obtener la direccion:", error);
    }
}

function generarColorAleatorio() {
    const randomColor = Math.floor(Math.random() * 16777215).toString(16);
    return `#${randomColor}`;
}

function dibujarPolilineaConFlechas(coordinates, color = 'blue', mensaje = '') {
    // Crear la polilínea base
    const polyline = L.polyline(coordinates, { color, weight: 4 }).addTo(map);
    
    // Añadir un popup con el mensaje, si se proporciona
    if (mensaje !== '') {
        polyline.bindPopup(mensaje);
    }

    const decorator = L.polylineDecorator(polyline, {
        patterns: [
            {
                offset: '5%',
                repeat: '10%',
                symbol: L.Symbol.arrowHead({
                    pixelSize: 15,
                    polygon: false,
                    pathOptions: { stroke: true, color: color },
                })
            }
        ]
    });

    // Añadir la decoración a la polilínea
    decorator.addTo(map).bindPopup(mensaje);
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
async function mostrarNodoCercanoConMarcador(lat, lon, radius = 50) {
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
 * Calcula la ruta entre nodos y obtiene los pasos con nombres de calles para cada tramo.
 *
 * @param {Array} nodos - Lista de nodos [{lat, lon}, ...]
 * @param {boolean} roundtrip - Indica si debe regresar al punto inicial (opcional, por defecto true)
 */
async function calcularRutaEntreNodos(nodos, roundtrip = true) {
    try {
        if (nodos.length < 2) {
            console.log("Se necesitan al menos 2 nodos para calcular una ruta.");
            return;
        }

        // Si roundtrip es true, agregamos el primer nodo al final para cerrar el ciclo
        let nodosRuta = [...nodos];
        if (roundtrip) {
            nodosRuta.push(nodos[0]);
        }

        // Mostrar el nodo más cercano a los nodos
        for (let i = 0; i < nodosRuta.length; i++) {
            const nodo = nodosRuta[i];

            const nodo_cercano = await mostrarNodoCercanoConMarcador(nodo.lat, nodo.lon, 50);
            if (nodo_cercano) {
                nodosRuta[i] = nodo_cercano; // Reemplazar el nodo original por el más cercano
            }
        }

        const coordenadas = nodosRuta.map(nodo => `${nodo.lon},${nodo.lat}`).join(";");

        const routeUrl = `https://router.project-osrm.org/route/v1/driving/${coordenadas}?overview=full&steps=true`;

        const routeResponse = await fetch(routeUrl);
        if (!routeResponse.ok) {
            console.error(`Error al consultar OSRM Route: ${routeResponse.statusText}`);
            return;
        }

        const routeData = await routeResponse.json();

        if (!routeData.routes || routeData.routes.length === 0) {
            console.log("No se encontró una ruta con detalles.");
            return;
        }

        if (routeData.routes.length > 1) {
            console.log("Se encontraron múltiples rutas. Usando la primera.");
        }

        // Mostrar la distancia y duración de la ruta
        const routeSummary = routeData.routes[0];
        console.log(`Ruta calculada: ${routeSummary.distance / 1000} km en ${routeSummary.duration / 60} minutos.`);

        // Dibujar los pasos en el mapa y etiquetar las calles
        const steps = routeData.routes[0].legs.flatMap(leg => leg.steps);

        steps.forEach(step => {
            const name = step.name || "Sin nombre";

            // Decodificar la geometría de cada tramo
            const polylineDecoded = polyline.decode(step.geometry);
            const coordinates = polylineDecoded.map(coord => [coord[0], coord[1]]);

            const color = 'red'; //generarColorAleatorio();

            // Dibujar cada tramo con flechas
            dibujarPolilineaConFlechas(coordinates, color, name);
        });

    } catch (error) {
        console.error("Error calculando la ruta con steps:", error);
    }
}
