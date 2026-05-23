/**
 * Network Visualization Controller
 * Powered by vis-network with custom caching, CIDOC CRM color-coding,
 * interactive legend filtering, and a sticky detail popup panel.
 */

(function () {
    let network = null;
    let nodesDataSet = null;
    let edgesDataSet = null;
    let nodesView = null;
    let physicsEnabled = true;
    let labelsEnabled = false;
    let currentDepth = 2;
    let rawNodesData = [];
    
    // Set to keep track of globally deactivated node classes
    const hiddenCategories = new Set();
    
    // In-memory request caching keyed by depth
    const fetchCache = {};

    // Saturated, vibrant CIDOC CRM color definitions for high contrast & visibility
    const COLOR_PALETTE = {
        // Selected / Central Entity Node (Premium Gold theme)
        center: {
            background: '#fff9db',
            border: '#f59f00',
            highlight: { background: '#ffe066', border: '#f08c00' },
            hover: { background: '#ffe066', border: '#f08c00' }
        },
        // Places (Vibrant blue)
        place: {
            background: '#d0ebff',
            border: '#1c7ed6',
            highlight: { background: '#a5d8ff', border: '#1971c2' },
            hover: { background: '#a5d8ff', border: '#1971c2' }
        },
        // Persons (Teal)
        person: {
            background: '#e3fafc',
            border: '#0b7285',
            highlight: { background: '#c5f6fa', border: '#09677a' },
            hover: { background: '#c5f6fa', border: '#09677a' }
        },
        // Groups (Warm Coral/Red)
        group: {
            background: '#ffe3e3',
            border: '#fa5252',
            highlight: { background: '#ffc9c9', border: '#e03131' },
            hover: { background: '#ffc9c9', border: '#e03131' }
        },
        // Generic Actor (Deep Rose)
        actor: {
            background: '#fff0f6',
            border: '#e64980',
            highlight: { background: '#ffdeeb', border: '#d01c5a' },
            hover: { background: '#ffdeeb', border: '#d01c5a' }
        },
        // Events & Activities (Vivid Purple/Violet)
        event: {
            background: '#f3f0ff',
            border: '#7048e8',
            highlight: { background: '#e5dbff', border: '#5f3dc4' },
            hover: { background: '#e5dbff', border: '#5f3dc4' }
        },
        // References, Bibliographies & Sources (Fresh Green)
        reference: {
            background: '#ebfbee',
            border: '#37b24d',
            highlight: { background: '#d3f9d8', border: '#2f9e44' },
            hover: { background: '#d3f9d8', border: '#2f9e44' }
        },
        // Fallback default (Gray)
        default: {
            background: '#f1f3f5',
            border: '#495057',
            highlight: { background: '#e9ecef', border: '#343a40' },
            hover: { background: '#e9ecef', border: '#343a40' }
        }
    };

    // CIDOC CRM grouping arrays
    const EVENT_CLASSES = ['event', 'activity', 'production', 'modification', 'acquisition', 'creation', 'move', 'destruction'];
    const REF_CLASSES = ['reference_system', 'bibliography', 'source', 'reference', 'edition', 'file', 'external_reference', 'external reference'];

    function getPaletteCategory(systemClass) {
        if (!systemClass) return 'default';
        const sc = systemClass.toLowerCase();
        
        if (EVENT_CLASSES.includes(sc)) return 'event';
        if (REF_CLASSES.includes(sc)) return 'reference';
        if (sc === 'place') return 'place';
        if (sc === 'person') return 'person';
        if (sc === 'group') return 'group';
        if (sc === 'actor') return 'actor';
        
        return 'default';
    }

    // Helper to get colors based on systemClass and central highlighting
    function getNodeColors(systemClass, isCenter) {
        if (isCenter) return COLOR_PALETTE.center;
        const category = getPaletteCategory(systemClass);
        return COLOR_PALETTE[category] || COLOR_PALETTE.default;
    }

    // Load data from proxy API with in-memory caching
    async function fetchNetworkData(id, depth) {
        const cacheKey = `${id}-${depth}`;
        if (fetchCache[cacheKey]) {
            console.log(`Serving network depth ${depth} from in-memory cache.`);
            return fetchCache[cacheKey];
        }

        const url = `/api/network/${id}?depth=${depth}`;
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        fetchCache[cacheKey] = data; // Cache the response
        return data;
    }

    // Process nodes and build unique edges
    function processGraphData(results, centerId) {
        const processedNodes = [];
        const processedEdges = [];
        const nodeMap = new Map();
        const edgeSet = new Set();

        // 1. Gather all nodes from results
        results.forEach(node => {
            nodeMap.set(node.id, node);
        });

        // 2. Build nodes dataset
        results.forEach(node => {
            const isCenter = String(node.id) === String(centerId);
            const colors = getNodeColors(node.systemClass, isCenter);
            
            // Build premium HTML tooltip for hover
            const tooltipHtml = document.createElement('div');
            tooltipHtml.className = 'p-1';
            tooltipHtml.innerHTML = `
                <div style="font-weight:700; margin-bottom:4px; font-size:14px; color:#1c1e21;">${node.label}</div>
                <div style="margin-bottom:6px;">
                  <span class="badge rounded-pill text-capitalize" style="background:${colors.background}; color:${colors.border}; font-size:10px; padding:3px 8px; border:1px solid ${colors.border};">
                    ${node.systemClass.replace('_', ' ')}
                  </span>
                </div>
                <div style="font-size:11px; color:#65676b;">ID: ${node.id}</div>
                <div style="font-size:11px; color:#65676b;">Relations: ${node.relations ? node.relations.length : 0}</div>
            `;

            processedNodes.push({
                id: node.id,
                systemClass: node.systemClass,
                label: labelsEnabled ? node.label : '',
                title: tooltipHtml,
                shape: isCenter ? 'diamond' : 'dot',
                size: isCenter ? 25 : 12,
                borderWidth: isCenter ? 3.5 : 1.5,
                borderWidthSelected: isCenter ? 5 : 2.5,
                color: colors,
                font: {
                    face: 'Mulish',
                    size: isCenter ? 14 : 11,
                    color: '#212529',
                    strokeWidth: 2,
                    strokeColor: '#ffffff'
                },
                shadow: {
                    enabled: isCenter,
                    color: 'rgba(0,0,0,0.15)',
                    size: 10,
                    x: 0,
                    y: 4
                }
            });

            // 3. Build unique edges from relations list
            if (node.relations) {
                node.relations.forEach(targetId => {
                    if (nodeMap.has(targetId) && targetId !== node.id) {
                        const edgeKey = [node.id, targetId].sort().join('-');
                        if (!edgeSet.has(edgeKey)) {
                            edgeSet.add(edgeKey);
                            processedEdges.push({
                                from: node.id,
                                to: targetId,
                                color: {
                                    color: '#dee2e6',
                                    highlight: '#7048e8',
                                    hover: '#a5d8ff'
                                },
                                width: 1,
                                hoverWidth: 2,
                                selectionWidth: 2,
                                smooth: {
                                    type: 'continuous',
                                    roundness: 0.5
                                }
                            });
                        }
                    }
                });
            }
        });

        return { nodes: processedNodes, edges: processedEdges };
    }

    // Render network
    function initNetwork(container, nodes, edges, centerId) {
        nodesDataSet = new vis.DataSet(nodes);
        edgesDataSet = new vis.DataSet(edges);

        // Dynamic Filtering View
        nodesView = new vis.DataView(nodesDataSet, {
            filter: function (node) {
                if (String(node.id) === String(centerId)) return true;
                const category = getPaletteCategory(node.systemClass);
                return !hiddenCategories.has(category);
            }
        });

        const data = {
            nodes: nodesView,
            edges: edgesDataSet
        };

        const options = {
            physics: {
                enabled: physicsEnabled,
                barnesHut: {
                    gravitationalConstant: -6000,
                    centralGravity: 0.15,
                    springLength: 170,
                    springConstant: 0.04,
                    damping: 0.09,
                    avoidOverlap: 0.2
                },
                stabilization: {
                    enabled: true,
                    iterations: 150,
                    updateInterval: 25
                }
            },
            layout: {
                improvedLayout: false
            },
            interaction: {
                hover: true,
                tooltipDelay: 100,
                hideEdgesOnDrag: true,
                hideEdgesOnZoom: true
            },
            nodes: {
                borderWidth: 1.5,
                shadow: false
            },
            edges: {
                shadow: false
            }
        };

        network = new vis.Network(container, data, options);

        // Physics stabilization events
        const overlay = document.getElementById('network-overlay');
        const loaderText = document.getElementById('network-loader-text');

        network.on("stabilizationProgress", function (params) {
            const progress = Math.round((params.iterations / params.total) * 100);
            if (loaderText) {
                loaderText.innerText = `Positioning nodes... ${progress}%`;
            }
        });

        network.on("stabilizationIterationsDone", function () {
            if (overlay) {
                overlay.style.opacity = '0';
                setTimeout(() => overlay.classList.add('d-none'), 300);
            }
            network.fit();
        });

        // Click event on nodes to display details in a floating panel (sticky detail window)
        network.on("click", function (params) {
            const detailPanel = document.getElementById('network-node-detail');
            if (params.nodes.length > 0) {
                const clickedNodeId = params.nodes[0];
                const nodeData = rawNodesData.find(n => String(n.id) === String(clickedNodeId));
                
                if (nodeData && detailPanel) {
                    const titleElem = document.getElementById('detail-node-title');
                    const classElem = document.getElementById('detail-node-class');
                    const idElem = document.getElementById('detail-node-id');
                    const relationsElem = document.getElementById('detail-node-relations');
                    const linkElem = document.getElementById('detail-node-link');
                    
                    if (titleElem) titleElem.innerText = nodeData.label;
                    if (classElem) {
                        const isCenter = String(clickedNodeId) === String(centerId);
                        const colors = getNodeColors(nodeData.systemClass, isCenter);
                        classElem.innerHTML = `
                            <span class="badge text-capitalize" style="background: ${colors.background}; color: ${colors.border}; border: 1px solid ${colors.border}; padding: 4px 10px;">
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
                    
                    // Reveal the details panel
                    detailPanel.classList.remove('d-none');
                }
            }
        });
    }

    // Main loading process
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
            detailPanel.classList.add('d-none'); // Hide the details panel on refetch
        }

        try {
            const rawData = await fetchNetworkData(id, depth);
            rawNodesData = rawData.results || [];
            
            const graph = processGraphData(rawNodesData, id);
            const container = document.getElementById('network-viz');
            
            if (network) {
                network.destroy();
                network = null;
            }

            initNetwork(container, graph.nodes, graph.edges, id);
        } catch (error) {
            console.error("Failed to render network:", error);
            if (loaderText) {
                loaderText.innerHTML = `<span class="text-danger fw-semibold">Failed to load network.</span><br><small class="text-muted">${error.message}</small>`;
            }
        }
    }

    // Set up control event listeners
    function setupControls(id) {
        // 1. Depth select
        const depthSelect = document.getElementById('network-depth');
        if (depthSelect) {
            depthSelect.addEventListener('change', function (e) {
                currentDepth = parseInt(e.target.value);
                loadNetwork(id, currentDepth);
            });
        }

        // 2. Labels toggle
        const labelToggle = document.getElementById('toggle-labels');
        if (labelToggle) {
            labelToggle.addEventListener('change', function (e) {
                labelsEnabled = e.target.checked;
                if (nodesDataSet) {
                    const updates = nodesDataSet.get().map(node => {
                        const rawNode = rawNodesData.find(rn => rn.id === node.id);
                        return {
                            id: node.id,
                            label: labelsEnabled && rawNode ? rawNode.label : ''
                        };
                    });
                    nodesDataSet.update(updates);
                }
            });
        }

        // 3. Stop physics
        const stopPhysicsBtn = document.getElementById('btn-stop-layout');
        if (stopPhysicsBtn) {
            stopPhysicsBtn.addEventListener('click', function () {
                physicsEnabled = !physicsEnabled;
                if (network) {
                    network.setOptions({ physics: { enabled: physicsEnabled } });
                }
                
                if (physicsEnabled) {
                    stopPhysicsBtn.innerHTML = '<i class="bi bi-pause-fill me-1"></i>Stop Physics';
                    stopPhysicsBtn.className = 'btn btn-sm btn-outline-warning rounded-pill d-flex align-items-center';
                } else {
                    stopPhysicsBtn.innerHTML = '<i class="bi bi-play-fill me-1"></i>Start Physics';
                    stopPhysicsBtn.className = 'btn btn-sm btn-outline-success rounded-pill d-flex align-items-center';
                }
            });
        }

        // 4. Floating Detail Panel Close Button
        const closeDetailBtn = document.getElementById('btn-close-detail');
        const detailPanel = document.getElementById('network-node-detail');
        if (closeDetailBtn && detailPanel) {
            closeDetailBtn.addEventListener('click', function () {
                detailPanel.classList.add('d-none');
            });
        }

        // 5. Interactive Legend Toggling (Filters)
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
                    
                    // UX polish: Hide sticky detail panel if it displays a node from the newly hidden category
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
                
                // Instantly re-evaluate DataView filters completely client-side
                if (nodesView) {
                    nodesView.refresh();
                }
            });
        });

        // 6. Fullscreen
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
                            network.setSize('100%', '100%');
                            network.fit();
                        }, 100);
                    }
                });
            });
        }
    }

    // Hook into Bootstrap Tab change events to trigger network loading
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
                        setTimeout(() => network.fit(), 50);
                    }
                }
            });
        }
    });

})();
