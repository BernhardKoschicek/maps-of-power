// Initialize Leaflet Map
var map = L.map('map').setView([30, 0], 2);

L.control.scale().addTo(map);

// Add native Fullscreen control if loaded
if (typeof L.Control.FullScreen !== 'undefined') {
    map.addControl(new L.Control.FullScreen({
        position: 'topleft',
        title: 'Fullscreen View',
        titleCancel: 'Exit Fullscreen'
    }));
} else if (typeof L.control.fullscreen !== 'undefined') {
    L.control.fullscreen({
        position: 'topleft'
    }).addTo(map);
}

// Add native-styled Download Control for capturing map image
var downloadControl = L.control({position: 'topleft'});

downloadControl.onAdd = function (map) {
    var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
    var button = L.DomUtil.create('a', 'leaflet-control-button', container);
    button.innerHTML = '<i class="bi bi-camera" style="font-size: 14px; vertical-align: middle;"></i>';
    button.title = 'Download Map as Image';
    button.href = '#';
    button.style.display = 'flex';
    button.style.alignItems = 'center';
    button.style.justifyContent = 'center';
    button.style.width = '30px';
    button.style.height = '30px';
    button.style.cursor = 'pointer';

    L.DomEvent.on(button, 'click', function(e) {
        L.DomEvent.stop(e);
        
        var originalHTML = button.innerHTML;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" style="width: 12px; height: 12px; border-width: 1.5px; color: #1c7ed6;"></span>';
        
        var mapElement = document.getElementById('map');
        if (typeof html2canvas !== 'undefined') {
            // Dynamically calculate scale to target at least 2000px resolution
            var mapWidth = mapElement.offsetWidth || 500;
            var targetWidth = 2000;
            var dynamicScale = Math.max(2, Math.ceil(targetWidth / mapWidth));

            html2canvas(mapElement, {
                useCORS: true,
                allowTaint: false,
                logging: false,
                scale: dynamicScale // Guaranteed high-resolution export
            }).then(function(canvas) {
                var filename = (typeof entityName !== 'undefined' ? entityName : "entity").replace(/\s+/g, '_') + "_map.png";
                var imgUrl = canvas.toDataURL("image/png");
                
                var downloadAnchor = document.createElement('a');
                downloadAnchor.setAttribute("href", imgUrl);
                downloadAnchor.setAttribute("download", filename);
                document.body.appendChild(downloadAnchor);
                downloadAnchor.click();
                downloadAnchor.remove();
                
                button.innerHTML = originalHTML;
            }).catch(function(err) {
                console.error("Map image export failed:", err);
                alert("Could not export map as image. Some map tiles may restrict screenshotting.");
                button.innerHTML = originalHTML;
            });
        } else {
            alert("Screenshot library not loaded. Please try again.");
            button.innerHTML = originalHTML;
        }
    });

    return container;
};

downloadControl.addTo(map);

// Define category color mapping (matching network visualizer)
var categoryColors = {
    'selected': { fill: '#fab005', stroke: '#f59f00', weight: 4 },
    'place': { fill: '#339af0', stroke: '#1c7ed6', weight: 2 },
    'actor': { fill: '#ff6b6b', stroke: '#fa5252', weight: 2 },
    'event': { fill: '#be4bdb', stroke: '#7048e8', weight: 2 },
    'reference': { fill: '#51cf66', stroke: '#37b24d', weight: 2 },
    'other': { fill: '#adb5bd', stroke: '#868e96', weight: 2 }
};

// Map system classes to visual categories
function getFeatureCategory(feature) {
    if (!feature || !feature.properties) return 'other';
    var sc = feature.properties.systemClass;
    if (!sc) return 'other';
    sc = sc.toLowerCase();
    if (sc === 'selected') return 'selected';
    if (['place', 'feature', 'stratigraphic_unit'].indexOf(sc) !== -1) return 'place';
    if (['person', 'group', 'actor'].indexOf(sc) !== -1) return 'actor';
    if (['acquisition', 'activity', 'event', 'move', 'production', 'creation'].indexOf(sc) !== -1) return 'event';
    if (['bibliography', 'edition', 'external_reference', 'reference', 'source'].indexOf(sc) !== -1) return 'reference';
    return 'other';
}

// Styling for vectors (polygons and lines)
function styleFeature(feature) {
    var cat = getFeatureCategory(feature);
    var colors = categoryColors[cat] || categoryColors['other'];
    return {
        color: colors.stroke,
        fillColor: colors.fill,
        fillOpacity: 0.5,
        weight: colors.weight
    };
}

// Custom rendering for Points as Circle Markers
function pointToLayer(feature, latlng) {
    var cat = getFeatureCategory(feature);
    var colors = categoryColors[cat] || categoryColors['other'];
    return L.circleMarker(latlng, {
        radius: 8,
        fillColor: colors.fill,
        color: colors.stroke,
        weight: colors.weight,
        opacity: 1,
        fillOpacity: 0.8
    });
}

// Interactive popups for map features
function onEachFeature(feature, layer) {
    if (feature.properties) {
        var sc = feature.properties.systemClass || 'Entity';
        var catLabel = sc.replace('_', ' ').toUpperCase();
        var popupContent = '<div style="font-family: \'Inter\', sans-serif; min-width: 150px;">';
        
        // Add sleek category badge
        popupContent += '<span class="badge mb-2 d-inline-block text-capitalize" style="background:' + 
                        (categoryColors[getFeatureCategory(feature)]?.stroke || '#868e96') + '; color:#fff; font-size: 9px; padding: 2px 6px; border-radius: 4px;">' + 
                        catLabel + '</span>';
        
        // Add title and description
        popupContent += '<h6 class="fw-bold mb-1 text-dark" style="font-size:13px; margin:0 0 4px 0;">' + feature.properties.title + '</h6>';
        if (feature.properties.description) {
            popupContent += '<p class="text-muted mb-2" style="font-size: 11px; margin:0 0 6px 0; line-height: 1.4;">' + feature.properties.description + '</p>';
        }
        
        // Add View Entity button for related entities
        if (feature.properties.id && getFeatureCategory(feature) !== 'selected' && window.entityViewUrlTemplate) {
            var url = window.entityViewUrlTemplate.replace('999999', feature.properties.id);
            popupContent += '<hr style="margin:6px 0; opacity:0.15;">' +
                            '<a href="' + url + '" class="btn btn-primary btn-sm text-white rounded-pill px-3 py-1 w-100 text-center d-flex align-items-center justify-content-center" style="font-size:11px; font-weight:600; text-decoration:none;">' +
                            '<i class="bi bi-eye me-1"></i>View Entity</a>';
        }
        
        popupContent += '</div>';
        layer.bindPopup(popupContent);
    }
}

// Track layers to calculate combined boundaries
var mapLayers = [];

// 1. Render Main Entity Geometries
if (gisData) {
    var formattedMainData = gisData;
    if (gisData.type !== 'Feature' && gisData.type !== 'FeatureCollection') {
        formattedMainData = {
            "type": "Feature",
            "geometry": gisData,
            "properties": {
                "title": entityName,
                "systemClass": "selected",
                "id": window.gisDataEntityId
            }
        };
    } else if (gisData.type === 'Feature') {
        if (!formattedMainData.properties) {
            formattedMainData.properties = {};
        }
        formattedMainData.properties.systemClass = 'selected';
        formattedMainData.properties.title = entityName;
        formattedMainData.properties.id = window.gisDataEntityId;
    }

    var mainLayer = L.geoJSON(formattedMainData, {
        style: styleFeature,
        pointToLayer: pointToLayer,
        onEachFeature: onEachFeature
    }).addTo(map);
    mapLayers.push(mainLayer);
}

// 2. Render Related Geometries
if (gisRelatedPlaces && gisRelatedPlaces.length > 0) {
    var relatedLayer = L.geoJSON(gisRelatedPlaces, {
        style: styleFeature,
        pointToLayer: pointToLayer,
        onEachFeature: onEachFeature
    }).addTo(map);
    mapLayers.push(relatedLayer);
}

// 3. Zoom map dynamically to show all layered geometries
if (mapLayers.length > 0) {
    var group = new L.FeatureGroup(mapLayers);
    map.fitBounds(group.getBounds(), {
        padding: [40, 40],
        maxZoom: 13
    });
}

// Add default basemap, grouped overlays control, and 3-column TIB formatting
setupPremiumMapLayers(map);

// --- Glassmorphic Legend Control ---

var legend = L.control({position: 'bottomleft'});

legend.onAdd = function (map) {
    var div = L.DomUtil.create('div', 'map-legend info legend');
    div.style.background = 'rgba(255, 255, 255, 0.9)';
    div.style.backdropFilter = 'blur(10px)';
    div.style.webkitBackdropFilter = 'blur(10px)';
    div.style.padding = '10px 14px';
    div.style.border = '1px solid rgba(0, 0, 0, 0.1)';
    div.style.borderRadius = '12px';
    div.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.08)';
    div.style.fontFamily = 'Inter, system-ui, sans-serif';
    div.style.fontSize = '11px';
    div.style.color = '#333';
    div.style.lineHeight = '1.8';

    var categories = [
        { name: 'Selected Entity', color: '#fab005', border: '#f59f00' },
        { name: 'Place', color: '#339af0', border: '#1c7ed6' },
        { name: 'Actor (Person/Group)', color: '#ff6b6b', border: '#fa5252' },
        { name: 'Event / Activity', color: '#be4bdb', border: '#7048e8' },
        { name: 'Reference / Source', color: '#51cf66', border: '#37b24d' }
    ];

    var html = '<h6 class="fw-bold text-dark" style="font-size:12px; margin:0 0 8px 0; letter-spacing:0.02em; font-weight:700;">Map Legend</h6>';
    categories.forEach(function (cat) {
        html += '<div class="d-flex align-items-center mb-1" style="display:flex; align-items:center; margin-bottom: 4px;">' +
                '<span style="display:inline-block; width:12px; height:12px; border-radius:50%; background:' + cat.color + '; border:2px solid ' + cat.border + '; margin-right:8px; flex-shrink:0;"></span>' +
                '<span style="font-weight:600; color:#495057;">' + cat.name + '</span>' +
                '</div>';
    });

    div.innerHTML = html;
    return div;
};

legend.addTo(map);
