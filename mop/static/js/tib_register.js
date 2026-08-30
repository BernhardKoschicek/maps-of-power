/**
 * TIB Register Interactive Table & Modal Reader Controller
 * Fast asynchronous search, volume filtering, and modal book reader launcher.
 */

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('tibSearchInput');
    const clearBtn = document.getElementById('tibSearchClear');
    const volumeSelect = document.getElementById('tibVolumeSelect');
    const tableBody = document.getElementById('tibTableBody');
    const countBadge = document.getElementById('tibResultCount');
    const paginationContainer = document.getElementById('tibPagination');
    const limitSelect = document.getElementById('tibLimitSelect');
    const loadingSpinner = document.getElementById('tibLoadingSpinner');
    const modalEl = document.getElementById('tibReaderModal');

    if (!tableBody) return;

    let currentQuery = searchInput ? searchInput.value.trim() : '';
    let currentVolume = volumeSelect ? volumeSelect.value : 'all';
    let currentPage = 1;
    let currentLimit = limitSelect ? parseInt(limitSelect.value, 10) : 50;
    let debounceTimer = null;
    let modalReaderInstance = null;

    // Cache of reader page availability per volume
    const readerVolumes = ['tib1', 'tib2', 'tib3', 'tib4', 'tib5', 'tib6', 'tib7', 'tib12', 'tib13'];

    function fetchResults(page = 1) {
        currentPage = page;
        const offset = (currentPage - 1) * currentLimit;

        if (loadingSpinner) loadingSpinner.classList.remove('d-none');
        tableBody.style.opacity = '0.4';

        const params = new URLSearchParams({
            q: currentQuery,
            volume: currentVolume,
            limit: currentLimit,
            offset: offset
        });

        fetch(`/api/tib/search?${params.toString()}`)
            .then(res => res.json())
            .then(data => {
                renderTable(data);
                renderPagination(data.total, data.limit, data.offset);
                updateUrlParams();
            })
            .catch(err => {
                console.error('TIB search error:', err);
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="5" class="text-center py-4 text-danger">
                            <i class="bi bi-exclamation-triangle me-2"></i>Error loading register data.
                        </td>
                    </tr>
                `;
            })
            .finally(() => {
                if (loadingSpinner) loadingSpinner.classList.add('d-none');
                tableBody.style.opacity = '1.0';
            });
    }

    function renderTable(data) {
        if (!data.results || data.results.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center py-5 text-muted">
                        <i class="bi bi-search display-6 d-block mb-3 text-secondary"></i>
                        <h5>No toponyms found</h5>
                        <p class="small">Try adjusting your search query or volume filter.</p>
                    </td>
                </tr>
            `;
            if (countBadge) countBadge.textContent = '0 toponyms';
            return;
        }

        if (countBadge) {
            countBadge.textContent = `${data.total.toLocaleString()} toponyms`;
        }

        const rowsHtml = data.results.map(row => {
            const volKey = `tib${row.volume_id}`;
            const hasReader = readerVolumes.includes(volKey);
            const safeName = escapeHtml(row.name);

            // Render citation pills using data attributes for clean event delegation
            const citationsHtml = (row.pages || []).map(cit => {
                const isMainClass = cit.is_main ? 'tib-citation-main' : '';
                const targetPg = cit.target_page || cit.page_start || 1;

                if (hasReader) {
                    return `
                        <button type="button" class="tib-citation-pill ${isMainClass}"
                                data-volume="${volKey}"
                                data-page="${targetPg}"
                                data-name="${safeName}"
                                title="Open in Book Reader (Page ${targetPg})">
                            <i class="bi bi-book-half me-1"></i>${escapeHtml(cit.display_str)}
                        </button>
                    `;
                } else {
                    return `
                        <span class="tib-citation-pill ${isMainClass}">
                            ${escapeHtml(cit.display_str)}
                        </span>
                    `;
                }
            }).join('');

            const readerActionBtn = hasReader ? `
                <button type="button" class="btn btn-sm btn-outline-primary rounded-pill px-3 btn-tib-reader"
                        data-volume="${volKey}"
                        data-page="${row.pages?.[0]?.target_page || 1}"
                        data-name="${safeName}">
                    <i class="bi bi-book me-1"></i>Reader
                </button>
            ` : `
                <span class="text-muted small">No scans</span>
            `;

            return `
                <tr>
                    <td>
                        <span class="tib-toponym-name">${highlightMatch(row.name, currentQuery)}</span>
                    </td>
                    <td>
                        <span class="tib-volume-badge">${escapeHtml(row.volume)}</span>
                    </td>
                    <td>
                        <div class="d-flex flex-wrap align-items-center">
                            ${citationsHtml || '<span class="text-muted small">-</span>'}
                        </div>
                    </td>
                    <td class="text-secondary small">
                        ${highlightMatch(row.notes || '', currentQuery)}
                    </td>
                    <td class="text-end">
                        ${readerActionBtn}
                    </td>
                </tr>
            `;
        }).join('');

        tableBody.innerHTML = rowsHtml;
    }

    // Delegated click handler on tableBody for citation buttons
    tableBody.addEventListener('click', (e) => {
        const btn = e.target.closest('.tib-citation-pill, .btn-tib-reader');
        if (btn && btn.dataset.volume) {
            e.preventDefault();
            const vol = btn.dataset.volume;
            const page = parseInt(btn.dataset.page, 10) || 1;
            const name = btn.dataset.name || '';
            openTibReaderModal(vol, page, name);
        }
    });

    function renderPagination(total, limit, offset) {
        if (!paginationContainer) return;
        const totalPages = Math.ceil(total / limit);
        if (totalPages <= 1) {
            paginationContainer.innerHTML = '';
            return;
        }

        const currentP = Math.floor(offset / limit) + 1;
        let html = '<ul class="pagination pagination-sm justify-content-center mb-0 gap-1">';

        // Prev Button
        html += `
            <li class="page-item ${currentP === 1 ? 'disabled' : ''}">
                <button class="page-link rounded-pill px-3" data-page="${currentP - 1}">
                    <i class="bi bi-chevron-left me-1"></i>Prev
                </button>
            </li>
        `;

        // Determine visible page numbers
        const maxVisible = 5;
        let startP = Math.max(1, currentP - 2);
        let endP = Math.min(totalPages, startP + maxVisible - 1);
        if (endP - startP < maxVisible - 1) {
            startP = Math.max(1, endP - maxVisible + 1);
        }

        if (startP > 1) {
            html += `<li class="page-item"><button class="page-link rounded-circle" data-page="1">1</button></li>`;
            if (startP > 2) html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }

        for (let p = startP; p <= endP; p++) {
            html += `
                <li class="page-item ${p === currentP ? 'active' : ''}">
                    <button class="page-link rounded-circle" data-page="${p}">${p}</button>
                </li>
            `;
        }

        if (endP < totalPages) {
            if (endP < totalPages - 1) html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            html += `<li class="page-item"><button class="page-link rounded-circle" data-page="${totalPages}">
                ${totalPages}</button></li>`;
        }

        // Next Button
        html += `
            <li class="page-item ${currentP === totalPages ? 'disabled' : ''}">
                <button class="page-link rounded-pill px-3" data-page="${currentP + 1}">
                    Next<i class="bi bi-chevron-right ms-1"></i>
                </button>
            </li>
        `;
        html += '</ul>';

        paginationContainer.innerHTML = html;

        // Bind clicks
        paginationContainer.querySelectorAll('button[data-page]').forEach(btn => {
            btn.addEventListener('click', () => {
                const targetP = parseInt(btn.dataset.page, 10);
                if (targetP && targetP !== currentP) {
                    fetchResults(targetP);
                    window.scrollTo({ top: tableBody.offsetTop - 150, behavior: 'smooth' });
                }
            });
        });
    }

    function updateUrlParams() {
        const url = new URL('/tib/register', window.location.origin);
        if (currentQuery) url.searchParams.set('q', currentQuery);
        if (currentVolume && currentVolume !== 'all') url.searchParams.set('vol', currentVolume);
        if (currentPage > 1) url.searchParams.set('page', currentPage);

        history.replaceState(null, '', url.toString());
    }

    function highlightMatch(text, query) {
        if (!query || !text) return escapeHtml(text);
        const safeQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const re = new RegExp(`(${safeQuery})`, 'gi');
        return escapeHtml(text).replace(re, '<mark class="bg-warning text-dark p-0">$1</mark>');
    }

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // Bind Search Input
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            currentQuery = e.target.value.trim();
            if (clearBtn) clearBtn.classList.toggle('d-none', !currentQuery);

            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                fetchResults(1);
            }, 250);
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            if (searchInput) searchInput.value = '';
            currentQuery = '';
            clearBtn.classList.add('d-none');
            fetchResults(1);
        });
    }

    // Bind Volume Selector
    if (volumeSelect) {
        volumeSelect.addEventListener('change', (e) => {
            currentVolume = e.target.value;
            fetchResults(1);
        });
    }

    // Bind Volume Filter Pills (if present)
    document.querySelectorAll('.tib-filter-pill').forEach(pill => {
        pill.addEventListener('click', (e) => {
            e.preventDefault();
            document.querySelectorAll('.tib-filter-pill').forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            currentVolume = pill.dataset.volume || 'all';
            if (volumeSelect) volumeSelect.value = currentVolume;
            fetchResults(1);
        });
    });

    // Limit Selector
    if (limitSelect) {
        limitSelect.addEventListener('change', (e) => {
            currentLimit = parseInt(e.target.value, 10);
            fetchResults(1);
        });
    }

    // Global Modal Reader Launcher
    window.openTibReaderModal = function(volumeKey, targetPage = 1, toponymName = '') {
        if (!modalEl) {
            window.open(`/tib/reader/${volumeKey}#page/${targetPage}`, '_blank');
            return;
        }

        const modalTitle = document.getElementById('tibModalReaderTitle');
        const modalContainer = document.getElementById('tibModalReaderContainer');
        const openWindowBtn = document.getElementById('tibModalOpenWindowBtn');

        const updateModalHeader = (pg) => {
            if (modalTitle) {
                const prefix = toponymName ? `${toponymName} — ` : '';
                modalTitle.textContent = `${prefix}${volumeKey.toUpperCase()} (Page ${pg})`;
            }
            if (openWindowBtn) {
                openWindowBtn.href = `/tib/reader/${volumeKey}#page/${pg}`;
            }
        };

        updateModalHeader(targetPage);
        const bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);

        // If reader instance already exists for this volume, jump directly to targetPage
        if (modalReaderInstance && modalReaderInstance.volumeKey === volumeKey) {
            modalReaderInstance.goToPage(targetPage);
            bsModal.show();
            return;
        }

        // If volume changed, destroy previous reader instance
        if (modalReaderInstance && typeof modalReaderInstance.destroy === 'function') {
            modalReaderInstance.destroy();
            modalReaderInstance = null;
        }

        // Fetch reader pages and init
        fetch(`/api/tib/reader/${volumeKey}/pages`)
            .then(res => res.json())
            .then(data => {
                if (data.pages && data.pages.length > 0) {
                    modalContainer.innerHTML = '<div id="modalReaderApp" style="height: 100%;"></div>';
                    modalReaderInstance = new TibBookReader('modalReaderApp', {
                        volumeKey: volumeKey,
                        volumeTitle: `${volumeKey.toUpperCase()} Book Reader`,
                        pages: data.pages,
                        initialPage: targetPage,
                        isModal: true,
                        updateHash: false,
                        onPageChange: (pg) => updateModalHeader(pg)
                    });

                    bsModal.show();
                } else {
                    alert('No digital scans available for this volume.');
                }
            })
            .catch(err => {
                console.error('Failed to load reader scans:', err);
                alert('Could not load reader scans.');
            });
    };

    // Clean up any leftover hash when closing modal
    if (modalEl) {
        modalEl.addEventListener('hidden.bs.modal', () => {
            if (window.location.hash.startsWith('#page/')) {
                history.replaceState(null, '', window.location.pathname + window.location.search);
            }
        });
    }

    // Initial Load from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('q')) {
        currentQuery = urlParams.get('q');
        if (searchInput) searchInput.value = currentQuery;
        if (clearBtn) clearBtn.classList.remove('d-none');
    }
    if (urlParams.has('vol')) {
        currentVolume = urlParams.get('vol');
        if (volumeSelect) volumeSelect.value = currentVolume;
        const activePill = document.querySelector(`.tib-filter-pill[data-volume="${currentVolume}"]`);
        if (activePill) {
            document.querySelectorAll('.tib-filter-pill').forEach(p => p.classList.remove('active'));
            activePill.classList.add('active');
        }
    }
    if (urlParams.has('page')) {
        currentPage = parseInt(urlParams.get('page'), 10) || 1;
    }

    fetchResults(currentPage);
});
