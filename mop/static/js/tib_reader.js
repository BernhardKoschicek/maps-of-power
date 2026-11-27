/**
 * Modern HTML5 BookReader for Tabula Imperii Byzantini (TIB)
 * Supports Single & Spread View, Smooth Pan & Zoom, Thumbnails,
 * Keyboard shortcuts, and Deep-Linking (#page/52).
 */

class TibBookReader {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) return;

        this.volumeKey = options.volumeKey || 'tib1';
        this.volumeTitle = options.volumeTitle || 'TIB Reader';
        this.pages = options.pages || [];
        this.totalPages = this.pages.length;
        this.isModal = options.isModal ?? false;
        this.updateHash = options.updateHash ?? (!this.isModal);
        this.onPageChange = options.onPageChange || null;
        this.currentPage = options.initialPage || 1;
        this.isSpread = options.isSpread ?? false;

        // Viewport transform state
        this.zoom = 1.0;
        this.panX = 0;
        this.panY = 0;
        this.isDragging = false;
        this.startX = 0;
        this.startY = 0;

        // Bound event handler references for clean removal
        this._onMouseMove = null;
        this._onMouseUp = null;
        this._onKeyDown = null;
        this._onHashChange = null;
        this._thumbsRendered = false;
        this._thumbObserver = null;

        this.init();
    }

    init() {
        this.renderStructure();
        this.bindEvents();
        if (this.updateHash) {
            this.checkUrlHash();
        }
        this.goToPage(this.currentPage);
    }

    _escapeHtml(str) {
        if (str === null || str === undefined) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    _safeUrl(url) {
        if (typeof url !== 'string') return '';
        const trimmed = url.trim();
        if (trimmed.startsWith('/') && !trimmed.startsWith('//')) return trimmed;
        if (/^https?:\/\//i.test(trimmed)) return trimmed;
        return '';
    }

    renderStructure() {
        const safeTitle = this._escapeHtml(this.volumeTitle);
        this.container.innerHTML = `
            <div class="tib-reader-container">
                <div class="tib-reader-toolbar">
                    <div class="d-flex align-items-center gap-2">
                        <span class="fw-bold text-truncate" style="max-width: 260px;" title="${safeTitle}">
                            ${safeTitle}
                        </span>
                        <span class="badge bg-secondary text-white small">${this.totalPages} Pages</span>
                    </div>

                    <div class="d-flex align-items-center gap-1">
                        <button class="tib-btn-reader" id="btnPrevPage" title="Previous Page (Left Arrow)">
                            <i class="bi bi-chevron-left"></i>
                        </button>
                        <div class="d-flex align-items-center gap-1 px-2">
                            <span>Page</span>
                            <input type="number" id="inputPageNum" class="form-control form-control-sm text-center"
                                   style="width: 65px; height: 30px;" min="1" max="${this.totalPages}"
                                   value="${this.currentPage}">
                            <span>/ ${this.totalPages}</span>
                        </div>
                        <button class="tib-btn-reader" id="btnNextPage" title="Next Page (Right Arrow)">
                            <i class="bi bi-chevron-right"></i>
                        </button>
                    </div>

                    <div class="d-flex align-items-center gap-2">
                        <div class="btn-group btn-group-sm" role="group">
                            <button class="tib-btn-reader ${!this.isSpread ? 'active' : ''}" id="btnSinglePage"
                                    title="Single Page View">
                                <i class="bi bi-file-earmark"></i>
                            </button>
                            <button class="tib-btn-reader ${this.isSpread ? 'active' : ''}" id="btnSpreadPage"
                                    title="Two-Page Spread View">
                                <i class="bi bi-book"></i>
                            </button>
                        </div>

                        <div class="btn-group btn-group-sm" role="group">
                            <button class="tib-btn-reader" id="btnZoomOut" title="Zoom Out (-)">
                                <i class="bi bi-zoom-out"></i>
                            </button>
                            <button class="tib-btn-reader" id="btnZoomReset" title="Reset Zoom">
                                <span id="zoomLevelText">100%</span>
                            </button>
                            <button class="tib-btn-reader" id="btnZoomIn" title="Zoom In (+)">
                                <i class="bi bi-zoom-in"></i>
                            </button>
                        </div>

                        <button class="tib-btn-reader" id="btnToggleThumbs" title="Toggle Thumbnail Strip">
                            <i class="bi bi-grid-3x2-gap"></i>
                        </button>
                        <button class="tib-btn-reader" id="btnFullscreen" title="Toggle Fullscreen (F)">
                            <i class="bi bi-fullscreen"></i>
                        </button>
                    </div>
                </div>

                <div class="tib-reader-viewport" id="readerViewport">
                    <div class="tib-reader-canvas" id="readerCanvas">
                        <!-- Pages dynamically injected here -->
                    </div>
                </div>

                <div class="tib-thumb-drawer d-none" id="thumbDrawer"></div>
            </div>
        `;

        this.canvas = this.container.querySelector('#readerCanvas');
        this.viewport = this.container.querySelector('#readerViewport');
        this.thumbDrawer = this.container.querySelector('#thumbDrawer');
        this.pageInput = this.container.querySelector('#inputPageNum');
        this.zoomText = this.container.querySelector('#zoomLevelText');
    }

    bindEvents() {
        // Page navigation buttons
        this.container.querySelector('#btnPrevPage').addEventListener('click', () => this.prevPage());
        this.container.querySelector('#btnNextPage').addEventListener('click', () => this.nextPage());

        // Page number input
        this.pageInput.addEventListener('change', (e) => {
            const page = parseInt(e.target.value, 10);
            if (!isNaN(page)) this.goToPage(page);
        });

        // View mode toggles
        this.container.querySelector('#btnSinglePage').addEventListener('click', () => this.setSpreadMode(false));
        this.container.querySelector('#btnSpreadPage').addEventListener('click', () => this.setSpreadMode(true));

        // Zoom controls
        this.container.querySelector('#btnZoomIn').addEventListener('click', () => this.changeZoom(0.2));
        this.container.querySelector('#btnZoomOut').addEventListener('click', () => this.changeZoom(-0.2));
        this.container.querySelector('#btnZoomReset').addEventListener('click', () => this.resetZoom());

        // Fullscreen
        this.container.querySelector('#btnFullscreen').addEventListener('click', () => this.toggleFullscreen());

        // Thumbnail Drawer toggle (render and hydrate thumbnails lazily on demand)
        this.container.querySelector('#btnToggleThumbs').addEventListener('click', () => {
            const willShow = this.thumbDrawer.classList.contains('d-none');
            this.thumbDrawer.classList.toggle('d-none');
            if (willShow) {
                this.ensureThumbsRendered();
                this.updateThumbnails();
                this.hydrateVisibleThumbs();
            }
        });

        // Thumbnail click events
        this.thumbDrawer.addEventListener('click', (e) => {
            const item = e.target.closest('.tib-thumb-item');
            if (item) {
                const page = parseInt(item.dataset.page, 10);
                this.goToPage(page);
            }
        });

        // Pan & Drag events on viewport
        this.viewport.addEventListener('mousedown', (e) => this.startDrag(e));

        this._onMouseMove = (e) => this.onDrag(e);
        this._onMouseUp = () => this.endDrag();
        window.addEventListener('mousemove', this._onMouseMove);
        window.addEventListener('mouseup', this._onMouseUp);

        // Wheel Zoom
        this.viewport.addEventListener('wheel', (e) => {
            e.preventDefault();
            const delta = e.deltaY < 0 ? 0.15 : -0.15;
            this.changeZoom(delta);
        }, { passive: false });

        // Keyboard Shortcuts (only when reader container is visible)
        this._onKeyDown = (e) => {
            if (!this.container || !this.container.offsetParent) return;
            if (['input', 'textarea'].includes(document.activeElement?.tagName.toLowerCase())) return;
            if (e.key === 'ArrowLeft') this.prevPage();
            if (e.key === 'ArrowRight') this.nextPage();
            if (e.key === '+' || e.key === '=') this.changeZoom(0.2);
            if (e.key === '-') this.changeZoom(-0.2);
            if (e.key === '0') this.resetZoom();
            if (e.key.toLowerCase() === 'f') this.toggleFullscreen();
        };
        window.addEventListener('keydown', this._onKeyDown);

        // Listen to hash change only if updateHash is enabled
        if (this.updateHash) {
            this._onHashChange = () => this.checkUrlHash();
            window.addEventListener('hashchange', this._onHashChange);
        }
    }

    checkUrlHash() {
        const hash = window.location.hash;
        const match = hash.match(/#page\/(\d+)/);
        if (match) {
            const page = parseInt(match[1], 10);
            if (!isNaN(page) && page !== this.currentPage) {
                this.goToPage(page);
            }
        }
    }

    goToPage(pageNumber) {
        if (pageNumber < 1) pageNumber = 1;
        if (pageNumber > this.totalPages) pageNumber = this.totalPages;

        this.currentPage = pageNumber;
        if (this.pageInput) this.pageInput.value = this.currentPage;

        // Update URL hash only if enabled
        if (this.updateHash && window.location.hash !== `#page/${this.currentPage}`) {
            history.replaceState(null, '', `#page/${this.currentPage}`);
        }

        this.renderPages();
        this.updateThumbnails();
        this.preloadAdjacent();

        if (typeof this.onPageChange === 'function') {
            this.onPageChange(this.currentPage);
        }
    }

    prevPage() {
        const step = this.isSpread ? 2 : 1;
        this.goToPage(this.currentPage - step);
    }

    nextPage() {
        const step = this.isSpread ? 2 : 1;
        this.goToPage(this.currentPage + step);
    }

    setSpreadMode(isSpread) {
        this.isSpread = isSpread;
        this.container.querySelector('#btnSinglePage').classList.toggle('active', !isSpread);
        this.container.querySelector('#btnSpreadPage').classList.toggle('active', isSpread);
        this.renderPages();
    }

    renderPages() {
        this.canvas.innerHTML = '';

        if (!this.isSpread) {
            const page = this.pages[this.currentPage - 1];
            if (page) {
                const img = document.createElement('img');
                img.className = 'tib-reader-page';
                img.src = page.url;
                img.alt = `Page ${page.page_num}`;
                this.canvas.appendChild(img);
            }
        } else {
            // Two-page spread
            const spreadDiv = document.createElement('div');
            spreadDiv.className = 'tib-reader-spread';

            // Align facing pages (even on left, odd on right)
            const leftIdx = (this.currentPage % 2 === 0) ? this.currentPage - 1 : this.currentPage - 2;
            const rightIdx = leftIdx + 1;

            if (leftIdx >= 0 && this.pages[leftIdx]) {
                const leftImg = document.createElement('img');
                leftImg.className = 'tib-reader-page';
                leftImg.src = this.pages[leftIdx].url;
                leftImg.alt = `Page ${this.pages[leftIdx].page_num}`;
                spreadDiv.appendChild(leftImg);
            }

            if (rightIdx < this.totalPages && this.pages[rightIdx]) {
                const rightImg = document.createElement('img');
                rightImg.className = 'tib-reader-page';
                rightImg.src = this.pages[rightIdx].url;
                rightImg.alt = `Page ${this.pages[rightIdx].page_num}`;
                spreadDiv.appendChild(rightImg);
            }

            this.canvas.appendChild(spreadDiv);
        }

        this.applyTransform();
    }

    preloadAdjacent() {
        const toPreload = [this.currentPage + 1, this.currentPage + 2, this.currentPage - 1];
        toPreload.forEach((pNum) => {
            if (pNum >= 1 && pNum <= this.totalPages) {
                const img = new Image();
                img.src = this.pages[pNum - 1].url;
            }
        });
    }

    ensureThumbsRendered() {
        if (this._thumbsRendered || !this.thumbDrawer) return;
        this._thumbsRendered = true;
        this.thumbDrawer.innerHTML = this.pages.map((p) => {
            const pNum = Number.parseInt(p.page_num, 10) || 0;
            const safeUrl = this._escapeHtml(this._safeUrl(p.url));
            return `
            <div class="tib-thumb-item ${pNum === this.currentPage ? 'active' : ''}"
                 data-page="${pNum}" title="Page ${pNum}">
                <img class="tib-thumb-img" data-src="${safeUrl}" loading="lazy" decoding="async" alt="P. ${pNum}">
            </div>
        `;
        }).join('');

        if ('IntersectionObserver' in window) {
            this._thumbObserver = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        const img = entry.target.querySelector('img[data-src]');
                        if (img && !img.getAttribute('src')) {
                            img.setAttribute('src', img.dataset.src);
                        }
                        this._thumbObserver.unobserve(entry.target);
                    }
                });
            }, { root: this.thumbDrawer, rootMargin: '120px' });

            this.thumbDrawer.querySelectorAll('.tib-thumb-item').forEach((item) => {
                this._thumbObserver.observe(item);
            });
        }
    }

    hydrateVisibleThumbs() {
        if (!this._thumbsRendered || !this.thumbDrawer) return;
        const start = Math.max(1, this.currentPage - 4);
        const end = Math.min(this.totalPages, this.currentPage + 4);
        for (let p = start; p <= end; p++) {
            const img = this.thumbDrawer.querySelector(`.tib-thumb-item[data-page="${p}"] img[data-src]`);
            if (img && !img.getAttribute('src')) {
                img.setAttribute('src', img.dataset.src);
            }
        }
    }

    updateThumbnails() {
        if (!this.thumbDrawer || this.thumbDrawer.classList.contains('d-none')) return;
        this.ensureThumbsRendered();
        const active = this.thumbDrawer.querySelector('.tib-thumb-item.active');
        if (active) active.classList.remove('active');

        const current = this.thumbDrawer.querySelector(`.tib-thumb-item[data-page="${this.currentPage}"]`);
        if (current) {
            current.classList.add('active');
            current.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
        }
        this.hydrateVisibleThumbs();
    }

    changeZoom(delta) {
        this.zoom = Math.min(Math.max(0.4, this.zoom + delta), 3.0);
        this.zoomText.textContent = `${Math.round(this.zoom * 100)}%`;
        this.applyTransform();
    }

    resetZoom() {
        this.zoom = 1.0;
        this.panX = 0;
        this.panY = 0;
        this.zoomText.textContent = '100%';
        this.applyTransform();
    }

    applyTransform() {
        this.canvas.style.transform = `translate(${this.panX}px, ${this.panY}px) scale(${this.zoom})`;
    }

    startDrag(e) {
        this.isDragging = true;
        this.startX = e.clientX - this.panX;
        this.startY = e.clientY - this.panY;
    }

    onDrag(e) {
        if (!this.isDragging) return;
        this.panX = e.clientX - this.startX;
        this.panY = e.clientY - this.startY;
        this.applyTransform();
    }

    endDrag() {
        this.isDragging = false;
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            this.container.requestFullscreen().catch(() => {});
        } else {
            document.exitFullscreen().catch(() => {});
        }
    }

    destroy() {
        if (this._onMouseMove) window.removeEventListener('mousemove', this._onMouseMove);
        if (this._onMouseUp) window.removeEventListener('mouseup', this._onMouseUp);
        if (this._onKeyDown) window.removeEventListener('keydown', this._onKeyDown);
        if (this._onHashChange) window.removeEventListener('hashchange', this._onHashChange);
        if (this._thumbObserver) {
            this._thumbObserver.disconnect();
            this._thumbObserver = null;
        }
        if (this.container) this.container.innerHTML = '';
    }
}

window.TibBookReader = TibBookReader;
