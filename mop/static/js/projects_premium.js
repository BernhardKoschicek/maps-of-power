/**
 * ==========================================================================
 * PROJECTS PORTAL PREMIUM INTERACTION MANAGER (ES6 Module)
 * ==========================================================================
 */

window.initPremiumProjectsPortal = function (projectsData) {
  console.log("Initializing premium projects portal with data count:", Object.keys(projectsData).length);
  
  // Track Leaflet map instances for compare deck to avoid re-init crashes
  const microMaps = {};
  
  // State for comparison
  let selectedToCompare = [];

  // ==========================================
  // PART 1: 3D CARD TILT INTERACTIVITY
  // ==========================================
  function init3DTilt() {
    const cards = document.querySelectorAll(".premium-project-card");
    cards.forEach(card => {
      // Create and inject the "Compare" checkbox-button if not already present
      if (!card.querySelector(".compare-check-btn")) {
        const acronym = card.closest(".project-card-item").getAttribute("data-acronym");
        const compareBtn = document.createElement("div");
        compareBtn.className = "compare-check-btn";
        compareBtn.setAttribute("data-acronym", acronym);
        compareBtn.innerHTML = `
          <input type="checkbox" id="comp-chk-${acronym}">
          <label for="comp-chk-${acronym}" style="cursor:pointer; margin:0;">Compare</label>
        `;
        card.appendChild(compareBtn);

        // Click logic for the button
        compareBtn.addEventListener("click", (e) => {
          e.stopPropagation();
          const checkbox = compareBtn.querySelector("input");
          if (e.target !== checkbox) {
            checkbox.checked = !checkbox.checked;
          }
          toggleCompareProject(acronym, checkbox.checked);
        });
      }

      card.addEventListener("mousemove", (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const w = rect.width;
        const h = rect.height;
        
        // Calculate tilt
        const rotateX = -((y - h / 2) / h) * 12; // max 12 deg
        const rotateY = ((x - w / 2) / w) * 12;
        
        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
        card.style.setProperty("--mouse-x", `${(x / w) * 100}%`);
        card.style.setProperty("--mouse-y", `${(y / h) * 100}%`);
      });

      card.addEventListener("mouseleave", () => {
        card.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)";
      });
    });
  }

  // ==========================================
  // PART 2: PROJECT COMPARISON DECK
  // ==========================================
  function toggleCompareProject(acronym, isChecked) {
    const btn = document.querySelector(`.compare-check-btn[data-acronym="${acronym}"]`);
    const checkbox = document.getElementById(`comp-chk-${acronym}`);
    if (checkbox) checkbox.checked = isChecked;

    if (isChecked) {
      if (selectedToCompare.length >= 3) {
        alert("You can compare a maximum of 3 projects side-by-side.");
        if (checkbox) checkbox.checked = false;
        return;
      }
      if (!selectedToCompare.includes(acronym)) {
        selectedToCompare.push(acronym);
      }
      if (btn) btn.classList.add("selected");
    } else {
      selectedToCompare = selectedToCompare.filter(item => item !== acronym);
      if (btn) btn.classList.remove("selected");
    }
    
    updateComparisonDrawer();
  }

  function updateComparisonDrawer() {
    const drawer = document.getElementById("project-compare-drawer");
    if (!drawer) return;

    if (selectedToCompare.length === 0) {
      drawer.classList.remove("show");
      // Destroy existing maps
      Object.keys(microMaps).forEach(k => {
        if (microMaps[k]) {
          microMaps[k].remove();
          delete microMaps[k];
        }
      });
      return;
    }

    drawer.classList.add("show");
    
    // Build comparison table markup
    const tableContainer = document.getElementById("compare-table-container");
    if (!tableContainer) return;

    let columnsHtml = "";
    selectedToCompare.forEach(acronym => {
      const proj = projectsData[acronym];
      if (!proj) return;

      const piList = proj.pi ? proj.pi.join(", ") : "N/A";
      
      let fundNames = [];
      if (proj.funded_by) {
        proj.funded_by.forEach(f => {
          fundNames.push(f.name || f);
        });
      }
      const funding = fundNames.length > 0 ? fundNames.join(", ") : "N/A";

      let hostNames = [];
      if (proj.host_institutes) {
        proj.host_institutes.forEach(h => {
          hostNames.push(h.name || h);
        });
      }
      const hosting = hostNames.length > 0 ? hostNames.join(", ") : "N/A";
      
      const teamSize = (proj.pi ? proj.pi.length : 0) + (proj.employees ? proj.employees.length : 0);

      columnsHtml += `
        <td class="compare-td text-dark" id="col-compare-${acronym}">
          <div class="compare-project-head">
            <h5 class="fw-bold mb-0 text-primary">${proj.title} (${proj.acronym.toUpperCase()})</h5>
            <button class="compare-close-btn text-muted" data-acronym="${acronym}">&times;</button>
          </div>
          <hr class="my-2">
          <div class="mb-3">
            <span class="d-block small text-muted fw-bold text-uppercase">Timeline</span>
            <span class="small fw-semibold"><i class="bi bi-calendar-range me-1"></i> ${proj.begin} &mdash; ${proj.end}</span>
          </div>
          <div class="mb-3">
            <span class="d-block small text-muted fw-bold text-uppercase">Project Investigator (PI)</span>
            <span class="small fw-semibold">${piList}</span>
          </div>
          <div class="mb-3">
            <span class="d-block small text-muted fw-bold text-uppercase">Host Institution</span>
            <span class="small" style="font-size:0.8rem;">${hosting}</span>
          </div>
          <div class="mb-3">
            <span class="d-block small text-muted fw-bold text-uppercase">Funding Body</span>
            <span class="small" style="font-size:0.8rem;">${funding}</span>
          </div>
          <div class="mb-3">
            <span class="d-block small text-muted fw-bold text-uppercase">Team Count</span>
            <span class="badge bg-secondary text-dark rounded-pill">${teamSize} researchers</span>
          </div>
          <div>
            <span class="d-block small text-muted fw-bold text-uppercase mb-1">Dataset Coordinates Map</span>
            <div class="micro-map-container" id="micro-map-${acronym}"></div>
          </div>
        </td>
      `;
    });

    tableContainer.innerHTML = `
      <table class="compare-table">
        <tbody>
          <tr>
            ${columnsHtml}
          </tr>
        </tbody>
      </table>
    `;

    // Bind close buttons inside drawer columns
    tableContainer.querySelectorAll(".compare-close-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const acronym = btn.getAttribute("data-acronym");
        toggleCompareProject(acronym, false);
      });
    });

    // Initialize micro maps for each column
    selectedToCompare.forEach(acronym => {
      initMicroMap(acronym);
    });
  }

  function initMicroMap(acronym) {
    const containerId = `micro-map-${acronym}`;
    const container = document.getElementById(containerId);
    if (!container) return;

    // Clean up if it was previously active
    if (microMaps[acronym]) {
      microMaps[acronym].remove();
      delete microMaps[acronym];
    }

    // Initialize Leaflet Map inside comparing column
    const m = L.map(containerId, {
      zoomControl: false,
      attributionControl: false
    }).setView([42.505, 19.5], 5);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18
    }).addTo(m);

    microMaps[acronym] = m;

    // Load locations for this project via map api
    const url = `/api/project/places/${acronym}`;
    fetch(url)
      .then(res => res.json())
      .then(data => {
        if (data.places && data.places.length > 0) {
          const bounds = L.latLngBounds();
          let validCount = 0;
          
          data.places.forEach(place => {
            if (place.geometry && place.geometry.coordinates) {
              const coords = place.geometry.coordinates;
              const latLng = [coords[1], coords[0]];
              if (!isNaN(latLng[0]) && !isNaN(latLng[1])) {
                L.circleMarker(latLng, {
                  radius: 5,
                  fillColor: '#246D8B',
                  color: '#fff',
                  weight: 1,
                  opacity: 1,
                  fillOpacity: 0.8
                }).addTo(m);
                bounds.extend(latLng);
                validCount++;
              }
            }
          });

          if (validCount > 0) {
            m.fitBounds(bounds, { padding: [10, 10] });
          }
        }
      })
      .catch(err => console.error(`Error loading micro map places for ${acronym}:`, err));
  }

  // ==========================================
  // PART 3: INTERACTIVE TEMPORAL ROADMAP
  // ==========================================
  function parseDateString(str) {
    if (!str) return null;
    const parts = str.split(".");
    if (parts.length !== 3) return null;
    return new Date(parts[2], parts[1] - 1, parts[0]);
  }

  function initTimelineRoadmap() {
    const roadmapContainer = document.getElementById("roadmap-rows-container");
    if (!roadmapContainer) return;

    roadmapContainer.innerHTML = "";

    const keys = Object.keys(projectsData);
    if (keys.length === 0) return;

    // We build the layout spanning 2020 to 2030 (10-year timeline span)
    const minYear = 2020;
    const maxYear = 2030;
    const totalYearsRange = maxYear - minYear;

    // Gather gridlines
    const gridlinesContainer = document.querySelector(".roadmap-year-cols");
    if (gridlinesContainer) {
      gridlinesContainer.innerHTML = "";
      for (let y = minYear; y <= maxYear; y++) {
        const line = document.createElement("div");
        line.className = "roadmap-year-line";
        line.setAttribute("data-year", y);
        gridlinesContainer.appendChild(line);
      }
    }

    const today = new Date();

    keys.forEach(acronym => {
      const proj = projectsData[acronym];
      const start = parseDateString(proj.begin);
      const end = parseDateString(proj.end);
      if (!start || !end) return;

      // Status class determination
      let statusClass = "completed";
      if (today >= start && today <= end) {
        statusClass = "active";
      } else if (today < start) {
        statusClass = "upcoming";
      }

      // Calculate percentage positions
      const startYearFraction = start.getFullYear() + start.getMonth() / 12 + start.getDate() / 365;
      const endYearFraction = end.getFullYear() + end.getMonth() / 12 + end.getDate() / 365;

      let startPct = ((startYearFraction - minYear) / totalYearsRange) * 100;
      let endPct = ((endYearFraction - minYear) / totalYearsRange) * 100;

      // Bound to [0, 100]
      startPct = Math.max(0, Math.min(100, startPct));
      endPct = Math.max(0, Math.min(100, endPct));
      const widthPct = Math.max(1.5, endPct - startPct); // At least 1.5% visible width

      const row = document.createElement("div");
      row.className = "roadmap-row";
      row.setAttribute("data-acronym", acronym);
      row.setAttribute("data-start-year", start.getFullYear());
      row.setAttribute("data-end-year", end.getFullYear());

      row.innerHTML = `
        <div class="roadmap-label" title="${proj.title}">${proj.acronym.toUpperCase()}</div>
        <div class="roadmap-bar-container">
          <div class="roadmap-bar ${statusClass}" 
               style="left: ${startPct}%; width: ${widthPct}%;"
               data-acronym="${acronym}">
          </div>
        </div>
      `;

      roadmapContainer.appendChild(row);
    });

    // Handle Tooltip actions
    const tooltip = document.getElementById("roadmap-hover-tooltip");
    const bars = document.querySelectorAll(".roadmap-bar");

    bars.forEach(bar => {
      bar.addEventListener("mouseenter", (e) => {
        const acronym = bar.getAttribute("data-acronym");
        const proj = projectsData[acronym];
        if (!proj) return;

        // Count team members
        const teamSize = (proj.pi ? proj.pi.length : 0) + (proj.employees ? proj.employees.length : 0);

        tooltip.innerHTML = `
          <h6 class="fw-bold text-primary mb-1">${proj.title}</h6>
          <div class="small text-muted mb-2"><strong>Acronym:</strong> ${proj.acronym.toUpperCase()}</div>
          <div class="small mb-1"><strong>Duration:</strong> ${proj.begin} - ${proj.end}</div>
          <div class="small mb-1"><strong>PI:</strong> ${proj.pi ? proj.pi[0] : 'N/A'}</div>
          <div class="small"><strong>Researchers:</strong> ${teamSize}</div>
        `;
        tooltip.classList.add("show");
      });

      bar.addEventListener("mousemove", (e) => {
        const containerRect = document.querySelector(".roadmap-grid").getBoundingClientRect();
        const left = e.clientX - containerRect.left;
        const top = e.clientY - containerRect.top;
        
        tooltip.style.left = `${left}px`;
        tooltip.style.top = `${top}px`;
      });

      bar.addEventListener("mouseleave", () => {
        tooltip.classList.remove("show");
      });
    });

    // Slider filter event
    const slider = document.getElementById("timeline-year-slider");
    const sliderValBadge = document.getElementById("timeline-slider-year-val");

    if (slider && sliderValBadge) {
      const filterTimeline = () => {
        const selectedYear = parseInt(slider.value);
        sliderValBadge.textContent = selectedYear;

        const rows = document.querySelectorAll(".roadmap-row");
        rows.forEach(row => {
          const startYear = parseInt(row.getAttribute("data-start-year"));
          const endYear = parseInt(row.getAttribute("data-end-year"));

          if (selectedYear >= startYear && selectedYear <= endYear) {
            row.classList.remove("filtered-out");
          } else {
            row.classList.add("filtered-out");
          }
        });
      };

      slider.addEventListener("input", filterTimeline);
      // Run once initially
      filterTimeline();
    }
  }

  // ==========================================
  // PART 4: RESEARCH ANALYTICS DASHBOARD
  // ==========================================
  function initAnalyticsDashboard() {
    const statsTotal = document.getElementById("analytics-stat-total");
    const statsActive = document.getElementById("analytics-stat-active");
    const statsCompleted = document.getElementById("analytics-stat-completed");
    const statsResearchers = document.getElementById("analytics-stat-researchers");

    let totalProjects = 0;
    let activeProjects = 0;
    let completedProjects = 0;
    const uniqueResearchers = new Set();

    const fundingCount = {};
    const instituteCount = {};
    const collaboratorProjects = {}; // name -> Set of project acronyms
    const collaboratorRole = {};     // name -> "PI" or "Employee"

    const today = new Date();

    Object.keys(projectsData).forEach(acronym => {
      const proj = projectsData[acronym];
      totalProjects++;

      const start = parseDateString(proj.begin);
      const end = parseDateString(proj.end);
      let isActive = false;
      if (start && end) {
        isActive = (today >= start && today <= end) || (today < start);
      }
      
      if (isActive) activeProjects++;
      else completedProjects++;

      // Track PIs
      if (proj.pi) {
        proj.pi.forEach(p => {
          const name = p.trim();
          uniqueResearchers.add(name);
          if (!collaboratorProjects[name]) collaboratorProjects[name] = new Set();
          collaboratorProjects[name].add(acronym);
          collaboratorRole[name] = "PI";
        });
      }

      // Track Employees
      if (proj.employees) {
        proj.employees.forEach(e => {
          const name = e.trim();
          uniqueResearchers.add(name);
          if (!collaboratorProjects[name]) collaboratorProjects[name] = new Set();
          collaboratorProjects[name].add(acronym);
          if (!collaboratorRole[name] || collaboratorRole[name] === "Employee") {
            collaboratorRole[name] = "Employee";
          }
        });
      }

      // Track Funding bodies
      if (proj.funded_by) {
        proj.funded_by.forEach(f => {
          const name = f.name || f;
          fundingCount[name] = (fundingCount[name] || 0) + 1;
        });
      }

      // Track Hosting Institutes
      if (proj.host_institutes) {
        proj.host_institutes.forEach(h => {
          const name = h.name || h;
          instituteCount[name] = (instituteCount[name] || 0) + 1;
        });
      }
    });

    // Write numerical statistics
    if (statsTotal) statsTotal.textContent = totalProjects;
    if (statsActive) statsActive.textContent = activeProjects;
    if (statsCompleted) statsCompleted.textContent = completedProjects;
    if (statsResearchers) statsResearchers.textContent = uniqueResearchers.size;

    // Render CSS SVG Donut Chart for Funding Distribution
    renderDonutChart("funding-donut-chart-container", "funding-chart-legend", fundingCount, "Grants");

    // Render CSS SVG Donut Chart for Institute Distribution
    renderDonutChart("institute-donut-chart-container", "institute-chart-legend", instituteCount, "Hosts");

    // Render Collaborator Crossover Directory
    renderCollaboratorsList(collaboratorProjects, collaboratorRole);
  }

  function renderDonutChart(containerId, legendId, data, centerLabelText) {
    const donutContainer = document.getElementById(containerId);
    if (!donutContainer) return;

    donutContainer.innerHTML = "";

    const entries = Object.entries(data).sort((a, b) => b[1] - a[1]);
    const total = entries.reduce((acc, curr) => acc + curr[1], 0);

    if (total === 0) {
      donutContainer.innerHTML = `<span class="text-muted">No data available</span>`;
      return;
    }

    const colors = ["#246D8B", "#a0c223", "#f59f00", "#ae3ec9", "#3bc4fc", "#fa5252", "#12c167", "#868e96"];
    
    let svgHtml = `<svg class="donut-svg" viewBox="0 0 42 42">
      <circle class="donut-ring" cx="21" cy="21" r="15.91549430918954"></circle>
    `;

    let accumulatedPct = 0;

    entries.forEach(([name, count], idx) => {
      const pct = (count / total) * 100;
      const strokeDashArray = `${pct} ${100 - pct}`;
      const strokeDashOffset = 100 - accumulatedPct + 25; // add 25 to rotate to top center
      const color = colors[idx % colors.length];

      svgHtml += `
        <circle class="donut-segment" 
                cx="21" cy="21" r="15.91549430918954" 
                stroke="${color}" 
                stroke-dasharray="${strokeDashArray}" 
                stroke-dashoffset="${strokeDashOffset}"
                data-name="${name}" 
                data-count="${count}"
                data-pct="${pct.toFixed(0)}">
        </circle>
      `;

      accumulatedPct += pct;
    });

    svgHtml += `</svg>`;
    
    // Add center labels
    svgHtml += `
      <div class="chart-center-label text-dark">
        <span class="d-block fw-bold fs-4" id="${containerId}-center-val">${total}</span>
        <span class="text-muted text-uppercase" style="font-size:0.6rem; letter-spacing:0.05em; font-weight:700;">${centerLabelText}</span>
      </div>
    `;

    donutContainer.innerHTML = svgHtml;

    // Generate Chart Legend
    const legendContainer = document.getElementById(legendId);
    if (legendContainer) {
      legendContainer.innerHTML = "";
      entries.forEach(([name, count], idx) => {
        const color = colors[idx % colors.length];
        const item = document.createElement("div");
        item.className = "legend-item text-dark";
        item.innerHTML = `
          <div class="d-flex align-items-center">
            <span class="legend-color-box" style="background:${color};"></span>
            <span class="fw-semibold text-truncate" style="max-width:180px;" title="${name}">${name}</span>
          </div>
          <span class="fw-bold ms-2">${count}</span>
        `;
        legendContainer.appendChild(item);
      });
    }

    // Interactivity on Donut segments
    const segments = donutContainer.querySelectorAll(".donut-segment");
    const centerVal = document.getElementById(`${containerId}-center-val`);
    const centerLbl = donutContainer.querySelector(".chart-center-label span.text-muted");

    segments.forEach(segment => {
      segment.addEventListener("mouseenter", () => {
        const name = segment.getAttribute("data-name");
        const count = segment.getAttribute("data-count");
        const pct = segment.getAttribute("data-pct");

        if (centerVal) centerVal.textContent = `${pct}%`;
        if (centerLbl) {
          centerLbl.textContent = name;
          centerLbl.style.fontSize = "0.55rem";
        }
      });

      segment.addEventListener("mouseleave", () => {
        if (centerVal) centerVal.textContent = total;
        if (centerLbl) {
          centerLbl.textContent = centerLabelText;
          centerLbl.style.fontSize = "0.6rem";
        }
      });
    });
  }

  function renderCollaboratorsList(collaborators, roles) {
    const listContainer = document.getElementById("collaborator-directory-list");
    if (!listContainer) return;

    listContainer.innerHTML = "";

    const sortedNames = Object.keys(collaborators).sort((a, b) => {
      // Sort by involvement count, then alphabetically
      const diff = collaborators[b].size - collaborators[a].size;
      return diff !== 0 ? diff : a.localeCompare(b);
    });

    sortedNames.forEach(name => {
      const projSet = collaborators[name];
      const isCrossover = projSet.size > 1;
      const role = roles[name] || "Researcher";

      const projBadgesHtml = Array.from(projSet).map(acronym => 
        `<span class="collab-badge-project">${acronym.toUpperCase()}</span>`
      ).join("");

      const card = document.createElement("div");
      card.className = "collaborator-card";
      card.setAttribute("data-name", name.toLowerCase());
      card.setAttribute("data-projects", Array.from(projSet).join(" ").toLowerCase());

      card.innerHTML = `
        <div class="collab-info">
          <span class="collab-name">${name}</span>
          <span class="collab-role">${role}</span>
          <div class="collab-badges">
            ${projBadgesHtml}
          </div>
        </div>
        ${isCrossover ? `<span class="hub-tag ms-2"><i class="bi bi-diagram-3-fill me-1"></i>Crossover Hub</span>` : ""}
      `;

      listContainer.appendChild(card);
    });

    // Implement real-time live-search in Directory
    const searchInput = document.getElementById("collaborator-search-input");
    if (searchInput) {
      searchInput.addEventListener("input", () => {
        const query = searchInput.value.toLowerCase().trim();
        const cards = listContainer.querySelectorAll(".collaborator-card");

        cards.forEach(card => {
          const name = card.getAttribute("data-name");
          const projs = card.getAttribute("data-projects");

          if (name.includes(query) || projs.includes(query)) {
            card.style.display = "flex";
          } else {
            card.style.display = "none";
          }
        });
      });
    }
  }

  // ==========================================
  // INITIALIZE ALL TABS EVENT LISTENERS
  // ==========================================
  init3DTilt();

  // Listen to bootstrap tab switches to draw layouts properly
  const roadmapTab = document.getElementById("projects-tab-timeline-roadmap");
  const analyticsTab = document.getElementById("projects-tab-research-analytics");

  if (roadmapTab) {
    roadmapTab.addEventListener("shown.bs.tab", () => {
      initTimelineRoadmap();
    });
  }

  if (analyticsTab) {
    analyticsTab.addEventListener("shown.bs.tab", () => {
      initAnalyticsDashboard();
    });
  }
};
