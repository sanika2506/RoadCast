/**
 * RoadCast — Commuter Route & Traffic Analytics Application
 * S.Y. B.Tech IT, PCCoE Pune
 * Integrates Leaflet OpenStreetMap, OSRM routing, and historical traffic predictions.
 */

let mapInstance = null;
let routePolylineLayer = null;
let originMarkerLayer = null;
let destMarkerLayer = null;

let currentTileLayer = null;

document.addEventListener("DOMContentLoaded", () => {
  initSideRaysBackground();
  initNavigation();
  initLeafletMap();
  initMapLayerSwitcher();
  initApiKeyModal();
  initRouteForm();
  initPresetButtons();

  // Trigger initial demo route calculation
  executeRouteSearch();
});

/**
 * Tab Navigation Handler
 */
function initNavigation() {
  const navBtns = document.querySelectorAll(".nav-btn, .drawer-btn");
  const panes = document.querySelectorAll(".tab-pane");

  navBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");

      navBtns.forEach(b => b.classList.remove("active"));
      document.querySelectorAll(`[data-tab="${targetTab}"]`).forEach(b => b.classList.add("active"));

      panes.forEach(pane => {
        if (pane.id === `pane-${targetTab}`) {
          pane.classList.add("active");
        } else {
          pane.classList.remove("active");
        }
      });

      // SideRays background radiance adjustment per tab
      const sideRaysBg = document.getElementById("sideRaysBackground");
      if (sideRaysBg) {
        if (targetTab === "route-planner") {
          sideRaysBg.style.opacity = "1";
        } else {
          sideRaysBg.style.opacity = "0.5";
        }
      }

      // Close mobile drawer if open
      const drawer = document.getElementById("mobileDrawer");
      if (drawer) drawer.classList.remove("open");

      // Invalidate Leaflet map size when switching back to route tab
      if (targetTab === "route-planner" && mapInstance) {
        setTimeout(() => mapInstance.invalidateSize(), 200);
      }
    });
  });

  // Mobile menu button toggles
  const mobileMenuBtn = document.getElementById("mobileMenuBtn");
  const closeDrawerBtn = document.getElementById("closeDrawerBtn");
  const mobileDrawer = document.getElementById("mobileDrawer");

  if (mobileMenuBtn && mobileDrawer) {
    mobileMenuBtn.addEventListener("click", () => {
      mobileDrawer.classList.add("open");
    });
  }

  if (closeDrawerBtn && mobileDrawer) {
    closeDrawerBtn.addEventListener("click", () => {
      mobileDrawer.classList.remove("open");
    });
  }
}

/**
 * Tile Layer Factory (Google Maps & OpenStreetMap)
 */
function createTileLayer(providerType) {
  const apiKey = localStorage.getItem("roadcast_google_api_key") || "";
  const keyParam = apiKey ? `&key=${apiKey}` : "";

  if (providerType === "googleTraffic") {
    return L.tileLayer(`https://mt1.google.com/vt/lyrs=m,traffic&x={x}&y={y}&z={z}${keyParam}`, {
      attribution: '&copy; Google Maps Traffic',
      maxZoom: 20
    });
  } else if (providerType === "googleSatellite") {
    return L.tileLayer(`https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}${keyParam}`, {
      attribution: '&copy; Google Maps Satellite',
      maxZoom: 20
    });
  } else if (providerType === "googleRoadmap") {
    return L.tileLayer(`https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}${keyParam}`, {
      attribution: '&copy; Google Maps',
      maxZoom: 20
    });
  } else {
    // Official OpenStreetMap standard tiles (100% free, no watermark, no key required)
    return L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19
    });
  }
}

function setMapProvider(providerType) {
  if (currentTileLayer && mapInstance) {
    mapInstance.removeLayer(currentTileLayer);
  }
  currentTileLayer = createTileLayer(providerType);
  if (mapInstance && currentTileLayer) {
    currentTileLayer.addTo(mapInstance);
    // Ensure route line and markers stay on top
    if (routePolylineLayer) routePolylineLayer.bringToFront();
    if (originMarkerLayer) originMarkerLayer.bringToFront();
    if (destMarkerLayer) destMarkerLayer.bringToFront();
  }
}

/**
 * Leaflet Interactive Map Initialization
 */
function initLeafletMap() {
  const mapElement = document.getElementById("routeMap");
  if (!mapElement) return;

  // Initialize centered on Minneapolis/St. Paul corridor initially
  mapInstance = L.map("routeMap", {
    center: [44.9650, -93.1800],
    zoom: 12,
    zoomControl: true,
    scrollWheelZoom: true
  });

  // Default to Google Maps Roadmap (or saved preference)
  const savedProvider = localStorage.getItem("roadcast_map_provider") || "googleRoadmap";
  const selectEl = document.getElementById("mapLayerSelect");
  if (selectEl) selectEl.value = savedProvider;
  setMapProvider(savedProvider);
}

/**
 * Map Layer Provider Switcher
 */
function initMapLayerSwitcher() {
  const selectEl = document.getElementById("mapLayerSelect");
  if (!selectEl) return;

  selectEl.addEventListener("change", (e) => {
    const provider = e.target.value;
    localStorage.setItem("roadcast_map_provider", provider);
    setMapProvider(provider);
  });
}

/**
 * Google Maps API Key Modal
 */
function initApiKeyModal() {
  const modal = document.getElementById("apiKeyModal");
  const btnOpen = document.getElementById("btnApiKeyModal");
  const btnClose = document.getElementById("btnCloseApiKeyModal");
  const btnSave = document.getElementById("btnSaveApiKey");
  const btnRemove = document.getElementById("btnRemoveApiKey");
  const inputKey = document.getElementById("googleMapsApiKeyInput");

  if (!modal) return;

  const existingKey = localStorage.getItem("roadcast_google_api_key") || "";
  if (inputKey) inputKey.value = existingKey;

  if (btnOpen) {
    btnOpen.addEventListener("click", () => {
      if (inputKey) inputKey.value = localStorage.getItem("roadcast_google_api_key") || "";
      modal.style.display = "flex";
    });
  }

  if (btnClose) {
    btnClose.addEventListener("click", () => {
      modal.style.display = "none";
    });
  }

  if (btnSave) {
    btnSave.addEventListener("click", () => {
      const val = inputKey ? inputKey.value.trim() : "";
      if (val) {
        localStorage.setItem("roadcast_google_api_key", val);
        alert("Google Maps API Key saved successfully!");
      } else {
        localStorage.removeItem("roadcast_google_api_key");
      }
      modal.style.display = "none";
      const currentProvider = document.getElementById("mapLayerSelect")?.value || "googleRoadmap";
      setMapProvider(currentProvider);
    });
  }

  if (btnRemove) {
    btnRemove.addEventListener("click", () => {
      localStorage.removeItem("roadcast_google_api_key");
      if (inputKey) inputKey.value = "";
      alert("API Key cleared. Using default raster tiles.");
      modal.style.display = "none";
      const currentProvider = document.getElementById("mapLayerSelect")?.value || "googleRoadmap";
      setMapProvider(currentProvider);
    });
  }
}


/**
 * Route Form Submission
 */
function initRouteForm() {
  const form = document.getElementById("routeSearchForm");
  if (!form) return;

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    executeRouteSearch();
  });
}

/**
 * Preset Demo Buttons
 */
function initPresetButtons() {
  const btnI94 = document.getElementById("presetI94");
  const btnPune = document.getElementById("presetPune");

  if (btnI94) {
    btnI94.addEventListener("click", () => {
      document.getElementById("routeOrigin").value = "Minneapolis, MN";
      document.getElementById("routeDestination").value = "St. Paul, MN";
      document.getElementById("routeHour").value = "8";
      document.getElementById("routeDay").value = "Tuesday";
      executeRouteSearch();
    });
  }

  if (btnPune) {
    btnPune.addEventListener("click", () => {
      document.getElementById("routeOrigin").value = "PCCOE Akurdi";
      document.getElementById("routeDestination").value = "Shivajinagar Pune";
      document.getElementById("routeHour").value = "8";
      document.getElementById("routeDay").value = "Tuesday";
      executeRouteSearch();
    });
  }
}

/**
 * Execute Route Search & Connect Predictions
 */
async function executeRouteSearch() {
  const originVal = document.getElementById("routeOrigin").value.trim();
  const destVal = document.getElementById("routeDestination").value.trim();
  const hourVal = parseInt(document.getElementById("routeHour").value, 10);
  const dayVal = document.getElementById("routeDay").value;
  const btn = document.getElementById("btnShowRoute");

  if (!originVal || !destVal) {
    alert("Please provide both starting point and destination.");
    return;
  }

  if (btn) {
    btn.classList.add("loading");
    btn.querySelector("span").textContent = "Calculating Route...";
  }

  try {
    const payload = {
      origin: originVal,
      destination: destVal,
      departure_hour: hourVal,
      departure_day: dayVal,
      weather_condition: "Clear"
    };

    const response = await fetch("/api/v1/route", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Route calculation failed.");
    }

    const data = await response.json();
    displayRouteResults(data);
  } catch (error) {
    console.error("Route error:", error);
    alert(`Could not calculate route: ${error.message}`);
  } finally {
    if (btn) {
      btn.classList.remove("loading");
      btn.querySelector("span").textContent = "Show My Route";
    }
  }
}

/**
 * Render Route Results on Map & Interface
 */
function displayRouteResults(data) {
  // 1. Update Metrics
  const durationEl = document.getElementById("resDuration");
  const distanceEl = document.getElementById("resDistance");
  const trafficStatusEl = document.getElementById("resTrafficStatus");
  const corridorBadge = document.getElementById("mapCorridorBadge");

  if (durationEl) durationEl.textContent = `${data.duration_minutes} mins`;
  if (distanceEl) distanceEl.textContent = `${data.distance_km} km`;

  if (trafficStatusEl) {
    let tagClass = "tag-standard";
    if (data.is_supported_corridor) {
      if (data.traffic_category === "Low") tagClass = "tag-low";
      else if (data.traffic_category === "Moderate") tagClass = "tag-moderate";
      else tagClass = "tag-heavy";
    }
    trafficStatusEl.innerHTML = `<span class="traffic-tag ${tagClass}">${data.traffic_status_label}</span>`;
  }

  if (corridorBadge) {
    corridorBadge.textContent = data.corridor_name;
    corridorBadge.style.color = data.is_supported_corridor ? "#5DE4C7" : "#7AA7FF";
  }

  // 2. Update Interactive Leaflet Map
  if (mapInstance && data.route_coordinates && data.route_coordinates.length > 0) {
    // Remove previous layers
    if (routePolylineLayer) mapInstance.removeLayer(routePolylineLayer);
    if (originMarkerLayer) mapInstance.removeLayer(originMarkerLayer);
    if (destMarkerLayer) mapInstance.removeLayer(destMarkerLayer);

    const coords = data.route_coordinates;
    const polyColor = data.traffic_color || "#5DE4C7";

    // Draw route polyline with outer glow effect
    routePolylineLayer = L.polyline(coords, {
      color: polyColor,
      weight: 6,
      opacity: 0.9,
      lineJoin: "round",
      dashArray: data.is_supported_corridor ? null : "8, 6"
    }).addTo(mapInstance);

    // Custom Origin marker (Green circle pin)
    const originCoords = [data.origin.lat, data.origin.lon];
    originMarkerLayer = L.circleMarker(originCoords, {
      radius: 9,
      fillColor: "#5DE4C7",
      color: "#FFFFFF",
      weight: 2,
      opacity: 1,
      fillOpacity: 0.9
    }).addTo(mapInstance);
    originMarkerLayer.bindPopup(`<strong>Origin:</strong> ${data.origin.name}`).openPopup();

    // Custom Destination marker (Red circle pin)
    const destCoords = [data.destination.lat, data.destination.lon];
    destMarkerLayer = L.circleMarker(destCoords, {
      radius: 9,
      fillColor: "#FF727F",
      color: "#FFFFFF",
      weight: 2,
      opacity: 1,
      fillOpacity: 0.9
    }).addTo(mapInstance);
    destMarkerLayer.bindPopup(`<strong>Destination:</strong> ${data.destination.name}`);

    // Zoom and pan to fit entire route
    mapInstance.fitBounds(routePolylineLayer.getBounds(), {
      padding: [40, 40],
      maxZoom: 14
    });
  }

  // 3. Update Commuter Guidance & Traffic Intelligence
  const noticeBox = document.getElementById("insightsNoticeBox");
  const insightsBadge = document.getElementById("insightsBadge");
  const bestDepText = document.getElementById("bestDepartureText");
  const bottlenecksContainer = document.getElementById("bottlenecksContainer");
  const alternateRoutesContainer = document.getElementById("alternateRoutesContainer");
  const travelTipsList = document.getElementById("travelTipsList");

  if (insightsBadge) {
    insightsBadge.textContent = data.traffic_level_text || "Commuter Guidance";
    insightsBadge.style.color = data.traffic_color || "#5DE4C7";
  }

  if (noticeBox) {
    const hourSelect = document.getElementById("routeHour");
    const daySelect = document.getElementById("routeDay");
    const timeStr = hourSelect ? hourSelect.selectedOptions[0].text : "Selected Time";
    const dayStr = daySelect ? daySelect.value : "";
    
    noticeBox.innerHTML = `
      <div class="outlook-glass-box">
        <div class="outlook-badge-row">
          <span class="status-pill" style="background:${data.traffic_color || '#5DE4C7'}26; color:${data.traffic_color || '#5DE4C7'}; border:1px solid ${data.traffic_color || '#5DE4C7'}50;">
            ${data.traffic_category || 'Traffic'} Forecast &bull; ${dayStr}
          </span>
          <span class="time-label">${timeStr}</span>
        </div>
        <p class="outlook-text">${data.traffic_outlook || 'Normal traffic flow observed along this travel corridor.'}</p>
      </div>
    `;
    noticeBox.style.borderLeftColor = data.traffic_color || "#5DE4C7";
  }

  if (bestDepText) {
    bestDepText.textContent = data.best_departure_window || "Normal commute hours recommended. No major delays expected.";
  }

  // Render Traffic Choke Points & Bottlenecks in Clear Points
  if (bottlenecksContainer) {
    bottlenecksContainer.innerHTML = "";
    const bList = data.bottlenecks || [];
    if (bList.length > 0) {
      bList.forEach((b, index) => {
        const item = document.createElement("div");
        item.className = "bottleneck-card glass-panel";
        const delayStr = b.delay || b.delay_tag || "+10-15 mins delay";
        const isHigh = delayStr.includes("15+") || delayStr.includes("20+") || delayStr.includes("Heavy");
        item.innerHTML = `
          <div class="bottleneck-header">
            <div class="bottleneck-place-wrap">
              <span class="point-badge">${index + 1}</span>
              <strong class="bottleneck-place">📍 ${b.place}</strong>
            </div>
            <span class="bottleneck-delay ${isHigh ? 'delay-high' : 'delay-med'}">${delayStr}</span>
          </div>
          <div class="bottleneck-condition">${b.condition || 'High commuter volume convergence.'}</div>
          <div class="bottleneck-tip">💡 <strong>Commuter Advice:</strong> ${b.tip || 'Proceed with caution and maintain safe distance.'}</div>
        `;
        bottlenecksContainer.appendChild(item);
      });
    } else {
      bottlenecksContainer.innerHTML = `
        <div class="empty-state-notice glass-panel">
          ✨ <strong>Clear Roads:</strong> No major bottlenecks or congested choke points predicted for your departure time.
        </div>
      `;
    }
  }

  // Render Suggested Alternate Routes
  if (alternateRoutesContainer) {
    alternateRoutesContainer.innerHTML = "";
    const aList = data.alternate_routes || [];
    if (aList.length > 0) {
      aList.forEach((alt, idx) => {
        const item = document.createElement("div");
        item.className = "alternate-route-card glass-panel";
        const titleStr = alt.name || alt.title || `Route Option ${idx + 1}`;
        const benefitStr = alt.status || alt.savings || "Recommended Alternate";
        item.innerHTML = `
          <div class="alt-route-header">
            <span class="alt-route-title">🛣️ ${titleStr}</span>
            <span class="alt-route-savings">${benefitStr}</span>
          </div>
          <div class="alt-route-meta">
            <span>⏱️ Est. Travel Time: <strong>${alt.duration}</strong></span>
            <span>📍 Route Distance: <strong>${alt.distance}</strong></span>
          </div>
          <div class="alt-route-desc">${alt.advantage || alt.description || 'Reliable alternative bypass.'}</div>
        `;
        alternateRoutesContainer.appendChild(item);
      });
    } else {
      alternateRoutesContainer.innerHTML = `
        <div class="empty-state-notice glass-panel">
          🎯 Current primary route is optimal. No alternative diversions needed.
        </div>
      `;
    }
  }

  // Render Commuter Travel Tips in Bullet Points
  if (travelTipsList) {
    travelTipsList.innerHTML = "";
    const tList = data.travel_tips || [
      "Plan departure around optimal windows to avoid peak congestion.",
      "Keep electronic toll pass active for quicker transit.",
      "Check alternate bypass routes if heavy queues form near central entry points."
    ];
    tList.forEach(tip => {
      const item = document.createElement("div");
      item.className = "travel-tip-item glass-panel";
      item.innerHTML = `
        <span class="tip-check">✓</span>
        <span class="tip-text">${tip}</span>
      `;
      travelTipsList.appendChild(item);
    });
  }
}



/**
 * Initializes the React Bits <SideRays /> component background
 * Creates the interactive WebGL2 atmospheric light shafts on the first page
 */
function initSideRaysBackground() {
  const container = document.getElementById("sideRaysBackground");
  if (!container || typeof window.initSideRays !== "function") return;

  try {
    window.sideRaysInstance = window.initSideRays(container, {
      rayColor1: "#FFC46B",
      rayColor2: "#96c8ff",
      blend: 0.6,
      origin: "top-right",
      speed: 2.5,
      intensity: 2.0,
      spread: 2.0,
      density: 5,
      sharpness: 0.5,
      tilt: 0,
      falloff: 1.6,
      glow: 1.1,
      saturation: 1.0,
      dust: 0.35,
      followMouse: true,
      mouseInfluence: 0.5,
      intro: true,
      lightMode: false,
      opacity: 1.0,
      maxDevicePixelRatio: 2
    });
  } catch (err) {
    console.warn("Failed to initialize SideRays WebGL:", err);
  }
}
