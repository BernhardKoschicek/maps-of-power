// Intercept L.tileLayer to ensure crossOrigin is always 'anonymous' for screenshot compatibility
if (typeof L !== 'undefined' && L.tileLayer) {
    const originalTileLayer = L.tileLayer;
    L.tileLayer = function(url, options) {
        options = options || {};
        options.crossOrigin = 'anonymous';
        return originalTileLayer(url, options);
    };
}

const OpenStreetMap_HOT = L.tileLayer(
    "https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
    {
        maxZoom: 25,
        maxNativeZoom: 20,
        attribution: '&copy; OpenStreetMap contributors, Humanitarian style'
    }
);

const OpenStreetMap = L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        maxZoom: 25,
        maxNativeZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
    }
);

// Secure Satellite Layer
const Esri_WorldImagery = L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    {
        maxZoom: 25,
        maxNativeZoom: 19,
        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP'
    }
);

// Modern and secure HTTPS Topographic Layer
const OpenTopoMap = L.tileLayer(
    "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    {
        maxZoom: 17,
        attribution: 'Map data &copy; OpenStreetMap contributors, SRTM | Style &copy; OpenTopoMap'
    }
);

// --- Custom MOP Layers (Requires TMS / Inverted Y-axis) ---
const mopAncient = L.tileLayer(
    "https://data1.geo.univie.ac.at/TMS/DPP/DPP_ancient_12-13/{z}/{x}/{y}.png",
    {
        tms: true,
        minZoom: 5,
        maxZoom: 13,
        maxNativeZoom: 13,
        bounds: L.latLngBounds([28, -13], [60, 69]),
        attribution: "Universität Wien, SRTM, UMD Land Cover, Hansen"
    }
);

const mopModern = L.tileLayer(
    "https://data1.geo.univie.ac.at/TMS/DPP/DPP_modern_12-13/{z}/{x}/{y}.png",
    {
        tms: true,
        minZoom: 5,
        maxZoom: 13,
        minNativeZoom: 5,
        maxNativeZoom: 13,
        bounds: L.latLngBounds([27.5, -13], [60, 71.5]),
        attribution: "Universität Wien, SRTM, UMD Land Cover, Hansen"
    }
);

// --- TIB Layers (TMS, Native Zoom 6-12) ---
const tib1 = L.tileLayer("https://data1.geo.univie.ac.at/TMS/DPP/TIB/TIB_1/{z}/{x}/{y}.png", {
    tms: true, minZoom: 5, maxZoom: 13, minNativeZoom: 6, maxNativeZoom: 12,
    bounds: L.latLngBounds([37.5056236, 21.0838132], [40.2632453, 24.9001428]),
    attribution: "Austrian Academy of Sciences"
});

const tib2 = L.tileLayer("https://data1.geo.univie.ac.at/TMS/DPP/TIB/TIB_2/{z}/{x}/{y}.png", {
    tms: true, minZoom: 5, maxZoom: 13, minNativeZoom: 6, maxNativeZoom: 12,
    bounds: L.latLngBounds([36.29841641050392, 32.91592677666847], [39.94312700597401, 39.18193339450029]),
    attribution: "Austrian Academy of Sciences"
});

const tib3 = L.tileLayer("https://data1.geo.univie.ac.at/TMS/DPP/TIB/TIB_3/{z}/{x}/{y}.png", {
    tms: true, minZoom: 5, maxZoom: 13, minNativeZoom: 6, maxNativeZoom: 12,
    bounds: L.latLngBounds([37.0594764, 17.8194629], [40.7851673, 22.1205782]),
    attribution: "Austrian Academy of Sciences"
});

const tib4 = L.tileLayer("https://data1.geo.univie.ac.at/TMS/DPP/TIB/TIB_4/{z}/{x}/{y}.png", {
    tms: true, minZoom: 5, maxZoom: 13, minNativeZoom: 6, maxNativeZoom: 12,
    bounds: L.latLngBounds([36.86134835260630, 30.47239335005083], [40.85592996949239, 34.89355861745195]),
    attribution: "Austrian Academy of Sciences"
});

const tib5 = L.tileLayer("https://data1.geo.univie.ac.at/TMS/DPP/TIB/TIB_5/{z}/{x}/{y}.png", {
    tms: true, minZoom: 5, maxZoom: 13, minNativeZoom: 6, maxNativeZoom: 12,
    bounds: L.latLngBounds([35.7, 30.5], [38.5, 39.0]),
    attribution: "Austrian Academy of Sciences"
});

const tib6 = L.tileLayer("https://data1.geo.univie.ac.at/TMS/DPP/TIB/TIB_6/{z}/{x}/{y}.png", {
    tms: true, minZoom: 5, maxZoom: 13, minNativeZoom: 6, maxNativeZoom: 12,
    bounds: L.latLngBounds([40.3599311, 23.0396877], [43.4904032, 28.3106118]),
    attribution: "Austrian Academy of Sciences"
});

const tib7 = L.tileLayer("https://data1.geo.univie.ac.at/TMS/DPP/TIB/TIB_7/{z}/{x}/{y}.png", {
    tms: true, minZoom: 5, maxZoom: 13, minNativeZoom: 6, maxNativeZoom: 12,
    bounds: L.latLngBounds([36.00258581774740, 28.21663266812830], [40.18733448316670, 32.54683411226862]),
    attribution: "Austrian Academy of Sciences"
});

const tib8 = L.tileLayer("https://data1.geo.univie.ac.at/TMS/DPP/TIB/TIB_8/{z}/{x}/{y}.png", {
    tms: true, minZoom: 5, maxZoom: 13, minNativeZoom: 6, maxNativeZoom: 12,
    bounds: L.latLngBounds([36.00292764517943, 28.22388227347041], [38.31413193787299, 32.53880263685949]),
    attribution: "Austrian Academy of Sciences"
});

const tib9 = L.tileLayer("https://data1.geo.univie.ac.at/TMS/DPP/TIB/TIB_9/{z}/{x}/{y}.png", {
    tms: true, minZoom: 5, maxZoom: 13, minNativeZoom: 6, maxNativeZoom: 12,
    bounds: L.latLngBounds([39.62414311606063, 29.75535402729850], [42.34297488855310, 35.27022713808258]),
    attribution: "Austrian Academy of Sciences"
});

const tib10 = L.tileLayer("https://data1.geo.univie.ac.at/TMS/DPP/TIB/TIB_10/{z}/{x}/{y}.png", {
    tms: true, minZoom: 5, maxZoom: 13, minNativeZoom: 6, maxNativeZoom: 12,
    bounds: L.latLngBounds([37.8998867, 22.1459079], [41.1721745, 27.3404046]),
    attribution: "Austrian Academy of Sciences"
});

const tib11 = L.tileLayer("https://data1.geo.univie.ac.at/TMS/DPP/TIB/TIB_11/{z}/{x}/{y}.png", {
    tms: true, minZoom: 5, maxZoom: 13, minNativeZoom: 6, maxNativeZoom: 12,
    bounds: L.latLngBounds([39.86126128194356, 19.10483739433357], [42.83911173576866, 25.00525922680330]),
    attribution: "Austrian Academy of Sciences"
});

const tib12 = L.tileLayer("https://data1.geo.univie.ac.at/TMS/DPP/TIB/TIB_12/{z}/{x}/{y}.png", {
    tms: true, minZoom: 5, maxZoom: 13, minNativeZoom: 6, maxNativeZoom: 12,
    bounds: L.latLngBounds([39.9548868, 25.4058545], [42.0852886, 29.4403767]),
    attribution: "Austrian Academy of Sciences"
});

const tib15 = L.tileLayer("https://data1.geo.univie.ac.at/TMS/DPP/TIB/TIB_15/{z}/{x}/{y}.png", {
    tms: true, minZoom: 5, maxZoom: 13, minNativeZoom: 6, maxNativeZoom: 12,
    bounds: L.latLngBounds([34.47119913354862, 35.59615606162166], [38.09147286603758, 40.71847654859658]),
    attribution: "Austrian Academy of Sciences"
});

// --- Custom Regional Layers (TMS) ---
const regionSkopjePrilep = L.tileLayer(
    "https://data1.geo.univie.ac.at/TMS/DPP/Region_Skopje_Prilep/{z}/{x}/{y}.png",
    {
        tms: true,
        minZoom: 5,
        maxZoom: 13,
        minNativeZoom: 8,
        maxNativeZoom: 13,
        bounds: L.latLngBounds([41.2888502463, 21.052079034], [42.085788719, 21.8077264134]),
        attribution: "OpenStreetMap, SRTM, CORINE Landcover, Geonames (M. St. Popović / B. Koschicek)"
    }
);

const strumicaValley = L.tileLayer(
    "https://data1.geo.univie.ac.at/TMS/DPP/River_Strumica/{z}/{x}/{y}.png",
    {
        tms: true,
        minZoom: 5,
        maxZoom: 13,
        minNativeZoom: 6,
        maxNativeZoom: 13,
        bounds: L.latLngBounds([41.25, 21.9], [41.9, 23.1]),
        attribution: "OpenStreetMap, SRTM, Hansen"
    }
);

const reliefMontenegro = L.tileLayer(
    "https://data1.geo.univie.ac.at/TMS/DPP/Cetinje/{z}/{x}/{y}.png",
    {
        tms: true,
        minZoom: 5,
        maxZoom: 13,
        minNativeZoom: 5,
        maxNativeZoom: 13,
        bounds: L.latLngBounds([41.6, 17.9], [43.8, 20.8]),
        attribution: "Njegoš Museum Biljarda"
    }
);

const baseMaps = {
    "Landscape": OpenStreetMap_HOT,
    "Streetmap": OpenStreetMap,
    "Satellite": Esri_WorldImagery,
    "Topography": OpenTopoMap,
    "MOP (Ancient)": mopAncient,
    "MOP Modern": mopModern
};

const groupedOverlays = {
    "Tabula Imperii Byzantini (TIB)": {
        "TIB 1": tib1,
        "TIB 2": tib2,
        "TIB 3": tib3,
        "TIB 4": tib4,
        "TIB 5": tib5,
        "TIB 6": tib6,
        "TIB 7": tib7,
        "TIB 8": tib8,
        "TIB 9": tib9,
        "TIB 10": tib10,
        "TIB 11": tib11,
        "TIB 12": tib12,
        "TIB 15": tib15
    },
    "Detailed Regions": {
        "Region Skopje-Prilep": regionSkopjePrilep,
        "Strumica Valley": strumicaValley,
        "Relief of Montenegro (1916)": reliefMontenegro
    }
};

// Arrange TIB layers in a clean 3-column grid layout for space-saving readability
function columnizeTIBLayers() {
    const groupContainers = document.querySelectorAll('.leaflet-control-layers-group');
    groupContainers.forEach(container => {
        const nameSpan = container.querySelector('.leaflet-control-layers-group-name');
        if (nameSpan && nameSpan.textContent.includes('Tabula Imperii Byzantini')) {
            if (container.querySelector('.tib-column-wrapper')) return;

            const labelWrapper = document.createElement('div');
            labelWrapper.className = 'tib-column-wrapper';
            labelWrapper.style.display = 'grid';
            labelWrapper.style.gridTemplateColumns = 'repeat(3, 1fr)';
            labelWrapper.style.gap = '4px 8px';
            labelWrapper.style.marginTop = '6px';
            labelWrapper.style.paddingLeft = '4px';

            const labels = Array.from(container.querySelectorAll('label'));
            labels.forEach(label => {
                label.style.display = 'flex';
                label.style.alignItems = 'center';
                label.style.gap = '4px';
                label.style.margin = '0';
                label.style.whiteSpace = 'nowrap';
                label.style.fontSize = '11px';
                
                const input = label.querySelector('input');
                if (input) {
                    input.style.margin = '0';
                }
                labelWrapper.appendChild(label);
            });

            container.appendChild(labelWrapper);
        }
    });
}

// Global setup helper
window.setupPremiumMapLayers = function (mapInstance) {
    if (!mapInstance) return null;
    
    // Add default basemap
    baseMaps.Landscape.addTo(mapInstance);

    // Add grouped layer control
    const control = L.control.groupedLayers(baseMaps, groupedOverlays, {
        groupCheckboxes: true
    }).addTo(mapInstance);

    // Arrange TIB layers
    columnizeTIBLayers();
    
    // Run columnizer on hover/expand to make sure dynamic items are styled
    const controlContainer = control.getContainer();
    if (controlContainer) {
        controlContainer.addEventListener('mouseenter', columnizeTIBLayers);
        controlContainer.addEventListener('click', function() {
            setTimeout(columnizeTIBLayers, 0);
        });
    }

    return control;
};
