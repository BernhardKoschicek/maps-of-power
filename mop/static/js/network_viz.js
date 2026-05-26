/**
 * Network Visualization Controller
 * Powered by Sigma.js and Graphology with custom caching, color-coding,
 * interactive legend filtering, and a sticky detail popup panel.
 */

(function () {
    let network = null;
    let graph = null;
    let spacingFactor = 1.0;
    let labelsEnabled = true;
    let currentDepth = 2;
    let rawNodesData = [];
    let currentCenterId = null;
    
    // Set to keep track of globally deactivated node classes
    const hiddenCategories = new Set();
    
    // In-memory request caching keyed by depth
    const fetchCache = {};

    const COLOR_PALETTE = {
        center: { color: '#f59f00' },
        place: { color: '#1c7ed6' },
        person: { color: '#0b7285' },
        group: { color: '#fa5252' },
        event: { color: '#ae3ec9' },
        source: { color: '#f59f00' },
        source_translation: { color: '#d6336c' },
        artifact: { color: '#37b24d' },
        bibliography: { color: '#495057' },
        default: { color: '#ced4da' }
    };

    function getPaletteCategory(systemClass) {
        if (!systemClass) return 'default';
        const sc = systemClass.toLowerCase();
        if (sc.includes('place') || sc.includes('feature') || sc.includes('stratigraphic_unit')) return 'place';
        if (sc.includes('person')) return 'person';
        if (sc.includes('group')) return 'group';
        if (sc.includes('event') || sc.includes('activity') || sc.includes('acquisition') || sc.includes('move') || sc.includes('production') || sc.includes('creation')) return 'event';
        if (sc.includes('source_translation')) return 'source_translation';
        if (sc.includes('source')) return 'source';
        if (sc.includes('artifact') || sc.includes('human_remains')) return 'artifact';
        if (sc.includes('bibliography') || sc.includes('edition') || sc.includes('external_reference')) return 'bibliography';
        return 'default';
    }

    async function fetchNetworkData(id, depth) {
        const cacheKey = `${id}-${depth}`;
        if (fetchCache[cacheKey]) {
            return fetchCache[cacheKey];
        }
        const response = await fetch(`/api/network/${id}?depth=${depth}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        fetchCache[cacheKey] = data;
        return data;
    }

    function applySpringLayout(graph, iterations) {
        const nodes = graph.nodes();
        const numNodes = nodes.length;
        if (numNodes === 0) return;

        // Scale iterations: enough to converge, but capped to stay responsive
        if (!iterations) {
            iterations = numNodes > 200 ? 80 : (numNodes > 80 ? 120 : 200);
        }

        // Pre-build adjacency for O(1) neighbor lookup
        const adjacency = {};
        nodes.forEach(n => { adjacency[n] = []; });
        graph.forEachEdge((edge, attrs, source, target) => {
            adjacency[source].push(target);
            adjacency[target].push(source);
        });

        // Optimal spacing constant (Fruchterman-Reingold)
        const area = 800 * 600;
        const k = Math.sqrt(area / numNodes) * 1.2;
        const kSq = k * k;

        // spacingFactor boosts repulsion relative to attraction
        // so the camera auto-fit doesn't neutralize the effect
        const repulsionMultiplier = spacingFactor * spacingFactor;

        // Gravity pulls everything toward center to prevent drift
        const gravity = 0.05;

        // Initialize positions: jittered circle to break symmetry
        const positions = {};
        const radius = k * Math.sqrt(numNodes) * 0.3;
        for (let i = 0; i < numNodes; i++) {
            const angle = (i / numNodes) * 2 * Math.PI;
            const jitter = 0.8 + Math.random() * 0.4;
            positions[nodes[i]] = {
                x: radius * Math.cos(angle) * jitter,
                y: radius * Math.sin(angle) * jitter
            };
        }

        // Temperature schedule: start high, cool exponentially
        const tempStart = radius * 0.5;
        const tempMin = 0.5;

        for (let iter = 0; iter < iterations; iter++) {
            // Exponential cooling
            const progress = iter / iterations;
            const temp = Math.max(tempMin, tempStart * Math.pow(0.01, progress));

            const disp = {};
            for (let i = 0; i < numNodes; i++) {
                disp[nodes[i]] = { x: 0, y: 0 };
            }

            // 1. Repulsive forces between all node pairs (symmetric)
            for (let i = 0; i < numNodes; i++) {
                const v = nodes[i];
                const posV = positions[v];
                for (let j = i + 1; j < numNodes; j++) {
                    const u = nodes[j];
                    const posU = positions[u];
                    const dx = posV.x - posU.x;
                    const dy = posV.y - posU.y;
                    const distSq = dx * dx + dy * dy;
                    const dist = Math.sqrt(distSq) || 0.01;

                    // Repulsive force boosted by repulsionMultiplier
                    const force = (kSq * repulsionMultiplier) / dist;
                    const fx = (dx / dist) * force;
                    const fy = (dy / dist) * force;

                    disp[v].x += fx;
                    disp[v].y += fy;
                    disp[u].x -= fx;
                    disp[u].y -= fy;
                }
            }

            // 2. Attractive forces along edges (unchanged by spacing)
            graph.forEachEdge((edge, attributes, source, target) => {
                const posS = positions[source];
                const posT = positions[target];
                const dx = posT.x - posS.x;
                const dy = posT.y - posS.y;
                const dist = Math.sqrt(dx * dx + dy * dy) || 0.01;

                // Attractive force: dist^2 / k (unscaled)
                const force = (dist * dist) / k;
                const fx = (dx / dist) * force;
                const fy = (dy / dist) * force;

                disp[source].x += fx;
                disp[source].y += fy;
                disp[target].x -= fx;
                disp[target].y -= fy;
            });

            // 3. Gravity toward center
            for (let i = 0; i < numNodes; i++) {
                const node = nodes[i];
                const pos = positions[node];
                const distToCenter = Math.sqrt(pos.x * pos.x + pos.y * pos.y) || 0.01;
                disp[node].x -= gravity * pos.x;
                disp[node].y -= gravity * pos.y;
            }

            // 4. Apply displacements clamped by temperature
            for (let i = 0; i < numNodes; i++) {
                const node = nodes[i];
                const d = disp[node];
                const dist = Math.sqrt(d.x * d.x + d.y * d.y) || 0.01;
                const capped = Math.min(dist, temp);
                positions[node].x += (d.x / dist) * capped;
                positions[node].y += (d.y / dist) * capped;
            }
        }

        // Write final positions back to graphology
        for (let i = 0; i < numNodes; i++) {
            graph.setNodeAttribute(nodes[i], 'x', positions[nodes[i]].x);
            graph.setNodeAttribute(nodes[i], 'y', positions[nodes[i]].y);
        }
    }

    function renderNetworkGraph() {
        const container = document.getElementById('network-viz');
        if (!container) return;

        if (network) {
            network.kill();
            network = null;
        }

        container.innerHTML = "";

        const GraphConstructor = typeof graphology !== 'undefined' && graphology.Graph ? graphology.Graph : null;
        const SigmaConstructor = typeof Sigma !== 'undefined' ? Sigma : (typeof sigma !== 'undefined' && sigma.Sigma ? sigma.Sigma : null);

        if (!GraphConstructor || !SigmaConstructor) {
            console.error("Graphology or Sigma constructor not found globally.");
            return;
        }

        graph = new GraphConstructor();

        // 1. Filter nodes based on active legend items
        const filteredNodes = rawNodesData.filter(node => {
            if (String(node.id) === String(currentCenterId)) return true;
            const category = getPaletteCategory(node.systemClass);
            return !hiddenCategories.has(category);
        });

        const nodeIds = new Set(filteredNodes.map(item => item.id));

        // 2. Add nodes to graph
        filteredNodes.forEach(item => {
            const isCenter = String(item.id) === String(currentCenterId);
            const category = getPaletteCategory(item.systemClass);
            const palette = isCenter ? COLOR_PALETTE['center'] : (COLOR_PALETTE[category] || COLOR_PALETTE['default']);
            const deg = item.relations ? item.relations.length : 0;
            const size = isCenter ? 15 : Math.min(22, Math.max(7, 7 + deg * 0.4));

            graph.addNode(item.id.toString(), {
                label: labelsEnabled ? (item.label || `ID: ${item.id}`) : '',
                x: 0,
                y: 0,
                size: size,
                color: palette.color
            });
        });

        // 3. Fast O(E) Edge creation
        const edgeSet = new Set();
        filteredNodes.forEach(item => {
            if (item.relations) {
                item.relations.forEach(targetId => {
                    const s = item.id;
                    const t = targetId;
                    if (nodeIds.has(t)) {
                        const edgeKey = s < t ? `${s}-${t}` : `${t}-${s}`;
                        if (!edgeSet.has(edgeKey)) {
                            edgeSet.add(edgeKey);
                            graph.addEdge(s.toString(), t.toString(), {
                                color: '#e9ecef',
                                size: 1.5
                            });
                        }
                    }
                });
            }
        });

        if (graph.order > 0) {
            applySpringLayout(graph);

            network = new SigmaConstructor(graph, container, {
                allowOuterBounds: true,
                renderLabels: true
            });

            // Node Dragging Interaction
            let draggedNode = null;
            let isDragging = false;

            network.on("downNode", (e) => {
                isDragging = true;
                draggedNode = e.node;
                graph.setNodeAttribute(draggedNode, "highlighted", true);
                network.getCamera().disable(); // Prevent panning camera while dragging
            });

            network.getMouseCaptor().on("mousemovebody", (e) => {
                if (!isDragging || !draggedNode) return;

                // Convert mouse position to graph coordinates
                const pos = network.viewportToGraph(e);

                // Update node position in graphology
                graph.setNodeAttribute(draggedNode, "x", pos.x);
                graph.setNodeAttribute(draggedNode, "y", pos.y);

                // Prevent camera movement
                if (e.preventSigmaDefault) {
                    e.preventSigmaDefault();
                } else if (e.originalEvent && e.originalEvent.preventDefault) {
                    e.originalEvent.preventDefault();
                }
            });

            const endDrag = () => {
                if (draggedNode) {
                    graph.removeNodeAttribute(draggedNode, "highlighted");
                    draggedNode = null;
                    isDragging = false;
                    network.getCamera().enable(); // Re-enable camera panning
                }
            };

            network.getMouseCaptor().on("mouseup", endDrag);
            network.getMouseCaptor().on("mousedown", () => {
                if (!isDragging) {
                    endDrag();
                }
            });

            // Handle node click to show floating detail panel
            network.on("clickNode", function (event) {
                const clickedNodeId = event.node;
                const nodeData = rawNodesData.find(n => String(n.id) === String(clickedNodeId));
                const detailPanel = document.getElementById('network-node-detail');

                if (nodeData && detailPanel) {
                    const titleElem = document.getElementById('detail-node-title');
                    const classElem = document.getElementById('detail-node-class');
                    const idElem = document.getElementById('detail-node-id');
                    const relationsElem = document.getElementById('detail-node-relations');
                    const linkElem = document.getElementById('detail-node-link');

                    if (titleElem) titleElem.innerText = nodeData.label;
                    if (classElem) {
                        const isCenter = String(clickedNodeId) === String(currentCenterId);
                        const category = getPaletteCategory(nodeData.systemClass);
                        const palette = isCenter ? COLOR_PALETTE['center'] : (COLOR_PALETTE[category] || COLOR_PALETTE['default']);
                        classElem.innerHTML = `
                            <span class="badge text-capitalize" style="background: #fff; color: ${palette.color}; border: 1px solid ${palette.color}; padding: 4px 10px;">
                                ${nodeData.systemClass.replace('_', ' ')}
                            </span>
                        `;
                    }
                    if (idElem) idElem.innerText = nodeData.id;
                    if (relationsElem) relationsElem.innerText = nodeData.relations ? nodeData.relations.length : 0;
                    
                    if (linkElem) {
                        if (window.entityViewUrlTemplate) {
                            linkElem.href = window.entityViewUrlTemplate.replace('999999', nodeData.id);
                        } else {
                            linkElem.href = `/entity/${nodeData.id}`;
                        }
                    }

                    detailPanel.classList.remove('d-none');
                }
            });
        }
    }

    async function loadNetwork(id, depth) {
        const overlay = document.getElementById('network-overlay');
        const loaderText = document.getElementById('network-loader-text');
        const detailPanel = document.getElementById('network-node-detail');
        
        if (overlay) {
            overlay.classList.remove('d-none');
            overlay.style.opacity = '1';
        }
        if (loaderText) {
            loaderText.innerText = 'Fetching graph data...';
        }
        if (detailPanel) {
            detailPanel.classList.add('d-none');
        }

        try {
            const rawData = await fetchNetworkData(id, depth);
            rawNodesData = rawData.results || [];
            currentCenterId = id;
            
            renderNetworkGraph();

            if (overlay) {
                overlay.style.opacity = '0';
                setTimeout(() => overlay.classList.add('d-none'), 300);
            }
        } catch (error) {
            console.error("Failed to render network:", error);
            if (loaderText) {
                loaderText.innerHTML = `<span class="text-danger fw-semibold">Failed to load network.</span><br><small class="text-muted">${error.message}</small>`;
            }
        }
    }

    function exportGraphAsImage(id) {
        if (!network) return;

        const container = document.getElementById('network-viz');
        const visCanvas = container ? container.querySelector('canvas') : null;
        if (!visCanvas) {
            console.error("Canvas element not found!");
            return;
        }

        const formatOption = document.querySelector('input[name="exportFormat"]:checked');
        const bgOption = document.querySelector('input[name="exportBg"]:checked');

        const format = formatOption ? formatOption.value : 'png';
        const bgType = bgOption ? bgOption.value : 'transparent';
        const includeWatermark = true;

        const exportCanvas = document.createElement('canvas');
        exportCanvas.width = visCanvas.width;
        exportCanvas.height = visCanvas.height;
        const ctx = exportCanvas.getContext('2d');

        if (bgType === 'white') {
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, exportCanvas.width, exportCanvas.height);
        } else if (bgType === 'dark') {
            ctx.fillStyle = '#0b0e14';
            ctx.fillRect(0, 0, exportCanvas.width, exportCanvas.height);
        } else {
            if (format === 'jpeg') {
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(0, 0, exportCanvas.width, exportCanvas.height);
            }
        }

        ctx.drawImage(visCanvas, 0, 0);

        if (includeWatermark) {
            const isDark = bgType === 'dark';
            const primaryTextColor = isDark ? '#f8f9fa' : '#212529';
            const secondaryTextColor = isDark ? '#a1a1aa' : '#6c757d';
            
            ctx.save();
            const dpr = window.devicePixelRatio || 1;
            const scaleFactor = Math.max(1, dpr * 0.75);
            
            const padding = 20 * scaleFactor;
            const cardWidth = 320 * scaleFactor;
            const cardHeight = 85 * scaleFactor;
            const cardX = padding;
            const cardY = exportCanvas.height - cardHeight - padding;
            const cornerRadius = 8 * scaleFactor;

            ctx.fillStyle = isDark ? 'rgba(15, 23, 42, 0.92)' : 'rgba(255, 255, 255, 0.92)';
            ctx.strokeStyle = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)';
            ctx.lineWidth = 1 * scaleFactor;
            
            ctx.shadowColor = 'rgba(0,0,0,0.1)';
            ctx.shadowBlur = 10 * scaleFactor;
            ctx.shadowOffsetX = 0;
            ctx.shadowOffsetY = 4 * scaleFactor;

            ctx.beginPath();
            if (typeof ctx.roundRect === 'function') {
                ctx.roundRect(cardX, cardY, cardWidth, cardHeight, cornerRadius);
            } else {
                ctx.rect(cardX, cardY, cardWidth, cardHeight);
            }
            ctx.fill();
            ctx.shadowColor = 'transparent';
            ctx.stroke();

            ctx.font = `bold ${13 * scaleFactor}px "Outfit", "Inter", sans-serif`;
            ctx.fillStyle = primaryTextColor;
            ctx.fillText("Maps of Power", cardX + 15 * scaleFactor, cardY + 25 * scaleFactor);

            ctx.font = `${10 * scaleFactor}px "Outfit", "Inter", sans-serif`;
            ctx.fillStyle = secondaryTextColor;
            ctx.fillText("Historical Geography & Digital Humanities Initiative", cardX + 15 * scaleFactor, cardY + 41 * scaleFactor);
            ctx.fillText("https://atlas.maps-of-power.at/", cardX + 15 * scaleFactor, cardY + 54 * scaleFactor);

            // Clean name helper
            function cleanNames(namesStr) {
                if (!namesStr) return 'Mihailo Popović';
                return namesStr.split(',').map(function(name) {
                    return name.replace(/\s*\([^)]*\)/g, '').trim();
                }).join(', ');
            }
            const cleanedPIs = cleanNames(window.projectPIs || 'Mihailo Popović');
            const licenseText = "CC-BY 4.0 \u00A9 " + cleanedPIs;

            // Font scale scaling for multiple or long PIs names list
            let fontSize = 10 * scaleFactor;
            ctx.font = `${fontSize}px "Outfit", "Inter", sans-serif`;
            let textWidth = ctx.measureText(licenseText).width;
            const maxTextWidth = cardWidth - (30 * scaleFactor);
            if (textWidth > maxTextWidth) {
                fontSize = Math.max(7.5 * scaleFactor, fontSize * (maxTextWidth / textWidth));
                ctx.font = `${fontSize}px "Outfit", "Inter", sans-serif`;
            }
            ctx.fillText(licenseText, cardX + 15 * scaleFactor, cardY + 70 * scaleFactor);

            ctx.restore();
        }

        const mime = format === 'jpeg' ? 'image/jpeg' : 'image/png';
        const dataUrl = exportCanvas.toDataURL(mime, format === 'jpeg' ? 0.9 : undefined);
        const link = document.createElement('a');
        link.download = `maps_of_power_network_${id}.${format}`;
        link.href = dataUrl;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        const closeBtn = document.querySelector('#networkExportModal .btn-close');
        if (closeBtn) {
            closeBtn.click();
        }
    }

    function setupControls(id) {
        const depthSelect = document.getElementById('network-depth');
        if (depthSelect) {
            depthSelect.addEventListener('change', function (e) {
                currentDepth = parseInt(e.target.value);
                loadNetwork(id, currentDepth);
            });
        }

        const labelToggle = document.getElementById('toggle-labels');
        if (labelToggle) {
            labelToggle.addEventListener('change', function (e) {
                labelsEnabled = e.target.checked;
                renderNetworkGraph();
            });
        }

        const spacingSelect = document.getElementById('network-spacing');
        if (spacingSelect) {
            spacingSelect.addEventListener('change', function (e) {
                spacingFactor = parseFloat(e.target.value);
                renderNetworkGraph();
            });
        }

        const closeDetailBtn = document.getElementById('btn-close-detail');
        const detailPanel = document.getElementById('network-node-detail');
        if (closeDetailBtn && detailPanel) {
            closeDetailBtn.addEventListener('click', function () {
                detailPanel.classList.add('d-none');
            });
        }

        const legendItems = document.querySelectorAll('.network-legend .legend-item[role="button"]');
        legendItems.forEach(item => {
            item.addEventListener('click', function () {
                const category = item.getAttribute('data-category');
                if (!category) return;
                
                if (hiddenCategories.has(category)) {
                    hiddenCategories.delete(category);
                    item.classList.remove('inactive');
                } else {
                    hiddenCategories.add(category);
                    item.classList.add('inactive');
                    
                    if (detailPanel && !detailPanel.classList.contains('d-none')) {
                        const detailIdElem = document.getElementById('detail-node-id');
                        if (detailIdElem) {
                            const activeNodeId = detailIdElem.innerText;
                            const activeNode = rawNodesData.find(n => String(n.id) === String(activeNodeId));
                            if (activeNode && getPaletteCategory(activeNode.systemClass) === category) {
                                detailPanel.classList.add('d-none');
                            }
                        }
                    }
                }
                
                renderNetworkGraph();
            });
        });

        const fullscreenBtn = document.getElementById('btn-fullscreen');
        const container = document.getElementById('network-container');

        if (fullscreenBtn && container) {
            fullscreenBtn.addEventListener('click', function () {
                if (!document.fullscreenElement &&    
                    !document.mozFullScreenElement && !document.webkitFullscreenElement && !document.msFullscreenElement) {  
                    
                    if (container.requestFullscreen) {
                        container.requestFullscreen();
                    } else if (container.msRequestFullscreen) {
                        container.msRequestFullscreen();
                    } else if (container.mozRequestFullScreen) {
                        container.mozRequestFullScreen();
                    } else if (container.webkitRequestFullscreen) {
                        container.webkitRequestFullscreen(Element.ALLOW_KEYBOARD_INPUT);
                    }
                } else {
                    if (document.exitFullscreen) {
                        document.exitFullscreen();
                    } else if (document.msExitFullscreen) {
                        document.msExitFullscreen();
                    } else if (document.mozCancelFullScreen) {
                        document.mozCancelFullScreen();
                    } else if (document.webkitExitFullscreen) {
                        document.webkitExitFullscreen();
                    }
                }
            });

            const fullscreenEvents = ['fullscreenchange', 'webkitfullscreenchange', 'mozfullscreenchange', 'MSFullscreenChange'];
            fullscreenEvents.forEach(eventName => {
                document.addEventListener(eventName, function () {
                    const isFullscreen = document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement;
                    if (isFullscreen) {
                        fullscreenBtn.innerHTML = '<i class="bi bi-fullscreen-exit me-1"></i>Exit Fullscreen';
                    } else {
                        fullscreenBtn.innerHTML = '<i class="bi bi-fullscreen me-1"></i>Fullscreen';
                    }
                    if (network) {
                        setTimeout(() => {
                            network.refresh();
                        }, 100);
                    }
                });
            });
        }

        const formatPng = document.getElementById('formatPng');
        const formatJpeg = document.getElementById('formatJpeg');
        const bgTransparent = document.getElementById('bgTransparent');
        const bgWhite = document.getElementById('bgWhite');

        if (formatPng && formatJpeg && bgTransparent && bgWhite) {
            formatJpeg.addEventListener('change', function() {
                if (formatJpeg.checked) {
                    bgTransparent.disabled = true;
                    bgTransparent.nextElementSibling.style.opacity = '0.4';
                    bgTransparent.nextElementSibling.style.pointerEvents = 'none';
                    if (bgTransparent.checked) {
                        bgWhite.checked = true;
                    }
                }
            });
            formatPng.addEventListener('change', function() {
                if (formatPng.checked) {
                    bgTransparent.disabled = false;
                    bgTransparent.nextElementSibling.style.opacity = '1';
                    bgTransparent.nextElementSibling.style.pointerEvents = 'auto';
                }
            });
        }

        const doExportBtn = document.getElementById('btn-do-export');
        if (doExportBtn) {
            doExportBtn.addEventListener('click', function() {
                const originalText = doExportBtn.innerHTML;
                doExportBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Generating...';
                doExportBtn.disabled = true;

                setTimeout(() => {
                    try {
                        exportGraphAsImage(id);
                    } catch (err) {
                        console.error("Export failed:", err);
                        alert("Failed to export image: " + err.message);
                    } finally {
                        doExportBtn.innerHTML = originalText;
                        doExportBtn.disabled = false;
                    }
                }, 150);
            });
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        const currentEntityId = window.gisDataEntityId || (typeof entityName !== 'undefined' ? 237 : null);
        
        if (!currentEntityId) return;

        const networkTab = document.getElementById('network-tab');
        if (networkTab) {
            let loadedOnce = false;
            networkTab.addEventListener('shown.bs.tab', function () {
                if (!loadedOnce) {
                    loadedOnce = true;
                    loadNetwork(currentEntityId, currentDepth);
                    setupControls(currentEntityId);
                } else {
                    if (network) {
                        setTimeout(() => network.refresh(), 50);
                    }
                }
            });
        }
    });

})();
