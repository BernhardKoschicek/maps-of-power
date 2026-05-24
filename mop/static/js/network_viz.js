/**
 * Network Visualization Controller
 * Powered by Sigma.js and Graphology with custom caching, color-coding,
 * interactive legend filtering, and a sticky detail popup panel.
 */

(function () {
    let network = null;
    let graph = null;
    let physicsEnabled = true;
    let labelsEnabled = false;
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
        if (sc.includes('place')) return 'place';
        if (sc.includes('person')) return 'person';
        if (sc.includes('group')) return 'group';
        if (sc.includes('event')) return 'event';
        if (sc.includes('source_translation')) return 'source_translation';
        if (sc.includes('source')) return 'source';
        if (sc.includes('artifact')) return 'artifact';
        if (sc.includes('bibliography')) return 'bibliography';
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

    function applySpringLayout(graph, iterations = 80) {
        const width = 800;
        const height = 500;
        const k = Math.sqrt((width * height) / (graph.order || 1));

        // Initialize circularly
        const radius = 180;
        let idx = 0;
        graph.forEachNode(node => {
          const angle = (idx / graph.order) * 2 * Math.PI;
          graph.setNodeAttribute(node, 'x', radius * Math.cos(angle));
          graph.setNodeAttribute(node, 'y', radius * Math.sin(angle));
          idx++;
        });

        // Repulsive and attractive force iterations
        for (let iter = 0; iter < iterations; iter++) {
          const disp = {};
          graph.forEachNode(node => {
            disp[node] = { x: 0, y: 0 };
          });

          graph.forEachNode(v => {
            graph.forEachNode(u => {
              if (u !== v) {
                const dx = graph.getNodeAttribute(v, 'x') - graph.getNodeAttribute(u, 'x');
                const dy = graph.getNodeAttribute(v, 'y') - graph.getNodeAttribute(u, 'y');
                const dist = Math.sqrt(dx * dx + dy * dy) || 1;
                const force = (k * k) / dist;
                disp[v].x += (dx / dist) * force;
                disp[v].y += (dy / dist) * force;
              }
            });
          });

          graph.forEachEdge((edge, attributes, source, target) => {
            const dx = graph.getNodeAttribute(target, 'x') - graph.getNodeAttribute(source, 'x');
            const dy = graph.getNodeAttribute(target, 'y') - graph.getNodeAttribute(source, 'y');
            const dist = Math.sqrt(dx * dx + dy * dy) || 1;
            const force = (dist * dist) / k;
            disp[target].x -= (dx / dist) * force;
            disp[target].y -= (dy / dist) * force;
            disp[source].x += (dx / dist) * force;
            disp[source].y += (dy / dist) * force;
          });

          const t = Math.max(1, 40 - iter);
          graph.forEachNode(node => {
            const d = disp[node];
            const dist = Math.sqrt(d.x * d.x + d.y * d.y) || 1;
            const limit = Math.min(dist, t);
            const nx = graph.getNodeAttribute(node, 'x') + (d.x / dist) * limit;
            const ny = graph.getNodeAttribute(node, 'y') + (d.y / dist) * limit;
            graph.setNodeAttribute(node, 'x', nx);
            graph.setNodeAttribute(node, 'y', ny);
          });
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
            const systemClass = item.systemClass || 'default';
            const palette = isCenter ? COLOR_PALETTE['center'] : (COLOR_PALETTE[systemClass] || COLOR_PALETTE['default']);
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
            if (physicsEnabled) {
                applySpringLayout(graph);
            } else {
                // simple circular layout if physics disabled
                let idx = 0;
                graph.forEachNode(node => {
                    const angle = (idx / graph.order) * 2 * Math.PI;
                    graph.setNodeAttribute(node, 'x', 150 * Math.cos(angle));
                    graph.setNodeAttribute(node, 'y', 150 * Math.sin(angle));
                    idx++;
                });
            }

            network = new SigmaConstructor(graph, container, {
                allowOuterBounds: true,
                renderLabels: true
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
                        const palette = isCenter ? COLOR_PALETTE['center'] : (COLOR_PALETTE[nodeData.systemClass] || COLOR_PALETTE['default']);
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
        const watermarkOption = document.getElementById('exportWatermark');

        const format = formatOption ? formatOption.value : 'png';
        const bgType = bgOption ? bgOption.value : 'transparent';
        const includeWatermark = watermarkOption ? watermarkOption.checked : true;

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
            const cardHeight = 70 * scaleFactor;
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
            ctx.fillText("Maps of Power", cardX + 15 * scaleFactor, cardY + 28 * scaleFactor);

            ctx.font = `${10 * scaleFactor}px "Outfit", "Inter", sans-serif`;
            ctx.fillStyle = secondaryTextColor;
            ctx.fillText("Historical Geography & Digital Humanities Initiative", cardX + 15 * scaleFactor, cardY + 45 * scaleFactor);
            ctx.fillText("https://atlas.maps-of-power.at/", cardX + 15 * scaleFactor, cardY + 58 * scaleFactor);

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

        const stopPhysicsBtn = document.getElementById('btn-stop-layout');
        if (stopPhysicsBtn) {
            stopPhysicsBtn.addEventListener('click', function () {
                physicsEnabled = !physicsEnabled;
                renderNetworkGraph();
                
                if (physicsEnabled) {
                    stopPhysicsBtn.innerHTML = '<i class="bi bi-pause-fill me-1"></i>Stop Physics';
                    stopPhysicsBtn.className = 'btn btn-sm btn-outline-warning rounded-pill d-flex align-items-center';
                } else {
                    stopPhysicsBtn.innerHTML = '<i class="bi bi-play-fill me-1"></i>Start Physics';
                    stopPhysicsBtn.className = 'btn btn-sm btn-outline-success rounded-pill d-flex align-items-center';
                }
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
