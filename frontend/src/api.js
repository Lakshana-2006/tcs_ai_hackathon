// Base URL resolution:
// If VITE_API_URL is configured, use it.
// If running on Vite dev server (port 5173) or FastAPI server (port 8000), use relative '' so
// requests seamlessly go through Vite's proxy or same origin, preventing CORS/host mismatches on desktop, tablet, and mobile.
const resolveBaseUrl = () => {
  if (import.meta.env.VITE_API_URL) return import.meta.env.VITE_API_URL;
  if (typeof window !== 'undefined' && window.location) {
    if (window.location.port === '5173' || window.location.port === '8000') {
      return '';
    }
  }
  return 'http://127.0.0.1:8000';
};

const BASE_URL = resolveBaseUrl();

export async function searchCities(query) {
  if (!query || query.trim().length === 0) return [];
  const res = await fetch(`${BASE_URL}/api/geocode?q=${encodeURIComponent(query.trim())}`);
  if (!res.ok) throw new Error(`City search failed: ${res.statusText}`);
  const data = await res.json();
  return data.results || [];
}

export async function fetchCityWeather(lat, lon) {
  const res = await fetch(`${BASE_URL}/api/weather?lat=${lat}&lon=${lon}`);
  if (!res.ok) throw new Error(`Weather fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchCityData(name, country, country_code, lat, lon) {
  const params = new URLSearchParams({
    name: name || 'Chennai',
    country: country || 'India',
    country_code: country_code || 'IN',
    lat: lat || 13.0827,
    lon: lon || 80.2707
  });
  const res = await fetch(`${BASE_URL}/api/city-data?${params.toString()}`);
  if (!res.ok) throw new Error(`Failed to load city data: ${res.statusText}`);
  return res.json();
}

export async function fetchKPIs(cityContext = null) {
  let url = `${BASE_URL}/api/kpis`;
  if (cityContext && cityContext.latitude) {
    const params = new URLSearchParams({
      city: cityContext.name,
      lat: cityContext.latitude,
      lon: cityContext.longitude,
      country_code: cityContext.country_code
    });
    url += `?${params.toString()}`;
  }
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to fetch KPIs: ${res.statusText}`);
  return res.json();
}

export async function fetchZones(cityContext = null) {
  let url = `${BASE_URL}/api/zones`;
  if (cityContext && cityContext.latitude) {
    const params = new URLSearchParams({
      city: cityContext.name,
      lat: cityContext.latitude,
      lon: cityContext.longitude,
      country_code: cityContext.country_code
    });
    url += `?${params.toString()}`;
  }
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to fetch zones: ${res.statusText}`);
  return res.json();
}

export async function fetchInterventionsCatalog() {
  const res = await fetch(`${BASE_URL}/api/interventions`);
  if (!res.ok) throw new Error(`Failed to fetch catalog: ${res.statusText}`);
  return res.json();
}

export async function simulateInterventions(zoneId, interventions, zoneData = null, cityContext = null) {
  const payload = {
    zone_id: zoneId || null,
    city_name: cityContext?.name || 'Global Metro',
    currency_code: cityContext?.currency?.code || 'USD',
    currency_symbol: cityContext?.currency?.symbol || '$',
    currency_rate: cityContext?.currency?.rate_per_usd || 1.0,
    zone_data: zoneData || null,
    interventions: interventions || {}
  };
  const res = await fetch(`${BASE_URL}/api/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(`Simulation failed: ${res.statusText}`);
  return res.json();
}

export async function optimizeBudget({
  budgetLocal,
  equityWeighting = true,
  focusObjective = 'balanced',
  cityContext = null,
  zones = []
}) {
  const payload = {
    city_name: cityContext?.name || 'Global Metro',
    country_code: cityContext?.country_code || 'US',
    currency_code: cityContext?.currency?.code || 'USD',
    currency_symbol: cityContext?.currency?.symbol || '$',
    currency_rate: cityContext?.currency?.rate_per_usd || 1.0,
    total_budget_local: Number(budgetLocal),
    equity_weighting: Boolean(equityWeighting),
    focus_objective: focusObjective,
    zones: zones || []
  };
  const res = await fetch(`${BASE_URL}/api/optimize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(`Optimizer failed: ${res.statusText}`);
  return res.json();
}

export async function sendChatMessage(message, conversationHistory = [], context = null) {
  const payload = {
    message,
    conversation_history: conversationHistory,
    context: context || null
  };
  const res = await fetch(`${BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Chat request failed: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchSatelliteStatus() {
  const res = await fetch(`${BASE_URL}/api/satellite/status`);
  if (!res.ok) throw new Error(`Satellite status check failed: ${res.statusText}`);
  return res.json();
}

export async function fetchCitySatellite(city, lat = null, lon = null) {
  const params = new URLSearchParams({ city });
  if (lat !== null) params.append('lat', lat);
  if (lon !== null) params.append('lon', lon);
  const res = await fetch(`${BASE_URL}/api/satellite/city?${params.toString()}`);
  if (!res.ok) throw new Error(`Satellite city fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchSatelliteZones(city, lat = null, lon = null) {
  const params = new URLSearchParams({ city });
  if (lat !== null) params.append('lat', lat);
  if (lon !== null) params.append('lon', lon);
  const res = await fetch(`${BASE_URL}/api/satellite/zones?${params.toString()}`);
  if (!res.ok) throw new Error(`Satellite zones fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchZoneSatellite(zoneId, city = null, lat = null, lon = null) {
  const params = new URLSearchParams();
  if (city) params.append('city', city);
  if (lat !== null) params.append('lat', lat);
  if (lon !== null) params.append('lon', lon);
  const res = await fetch(`${BASE_URL}/api/satellite/zones/${zoneId}?${params.toString()}`);
  if (!res.ok) throw new Error(`Zone satellite fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchSatelliteTiles(lat, lon, layer = 'lst') {
  const params = new URLSearchParams({
    lat,
    lon,
    layer
  });
  const res = await fetch(`${BASE_URL}/api/satellite/tiles?${params.toString()}`);
  if (!res.ok) throw new Error(`Satellite tiles fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchSatelliteAnalysis(city = 'Chennai', zoneId = null, daysBack = 90) {
  const params = new URLSearchParams({ city, days_back: daysBack });
  if (zoneId) params.append('zone_id', zoneId);
  const res = await fetch(`${BASE_URL}/api/satellite/analysis?${params.toString()}`);
  if (!res.ok) throw new Error(`Satellite analysis fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchSatelliteHistory(city = 'Chennai', startDate = '2024-01-01', endDate = '2024-06-30') {
  const params = new URLSearchParams({ city, start_date: startDate, end_date: endDate });
  const res = await fetch(`${BASE_URL}/api/satellite/history?${params.toString()}`);
  if (!res.ok) throw new Error(`Satellite history fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchSatelliteProvenance() {
  const res = await fetch(`${BASE_URL}/api/satellite/provenance`);
  if (!res.ok) throw new Error(`Satellite provenance fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchDatasets(classification = null) {
  let url = `${BASE_URL}/api/datasets`;
  if (classification) {
    url += `?classification=${encodeURIComponent(classification)}`;
  }
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Datasets fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchDatasetDetails(datasetId) {
  const res = await fetch(`${BASE_URL}/api/datasets/${datasetId}`);
  if (!res.ok) throw new Error(`Dataset details fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchSpatialAlignment(cityName = 'Chennai') {
  const res = await fetch(`${BASE_URL}/api/datasets/spatial-alignment?city=${encodeURIComponent(cityName)}`);
  if (!res.ok) throw new Error(`Spatial alignment fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchTemporalPast(city, lat, lon, startDate, endDate) {
  const params = new URLSearchParams({
    city: city || 'Chennai',
    start_date: startDate || '2024-05-15',
    end_date: endDate || '2024-05-22'
  });
  if (lat !== null && lat !== undefined) params.append('lat', lat);
  if (lon !== null && lon !== undefined) params.append('lon', lon);
  const res = await fetch(`${BASE_URL}/api/temporal/past?${params.toString()}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Historical weather fetch failed: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchTemporalPresent(city, lat, lon) {
  const params = new URLSearchParams({ city: city || 'Chennai' });
  if (lat !== null && lat !== undefined) params.append('lat', lat);
  if (lon !== null && lon !== undefined) params.append('lon', lon);
  const res = await fetch(`${BASE_URL}/api/temporal/present?${params.toString()}`);
  if (!res.ok) throw new Error(`Current live temporal fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchTemporalFuture(city, lat, lon, days = 7) {
  const params = new URLSearchParams({
    city: city || 'Chennai',
    days: days
  });
  if (lat !== null && lat !== undefined) params.append('lat', lat);
  if (lon !== null && lon !== undefined) params.append('lon', lon);
  const res = await fetch(`${BASE_URL}/api/temporal/future?${params.toString()}`);
  if (!res.ok) throw new Error(`Forecast weather fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchTemporalClimate(city, lat, lon, model = 'EC_Earth3P_HR') {
  const params = new URLSearchParams({
    city: city || 'Chennai',
    model
  });
  if (lat !== null && lat !== undefined) params.append('lat', lat);
  if (lon !== null && lon !== undefined) params.append('lon', lon);
  const res = await fetch(`${BASE_URL}/api/temporal/climate?${params.toString()}`);
  if (!res.ok) throw new Error(`Climate projections fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchTemporalComparison(city, lat, lon) {
  const params = new URLSearchParams({ city: city || 'Chennai' });
  if (lat !== null && lat !== undefined) params.append('lat', lat);
  if (lon !== null && lon !== undefined) params.append('lon', lon);
  const res = await fetch(`${BASE_URL}/api/temporal/compare?${params.toString()}`);
  if (!res.ok) throw new Error(`Temporal comparison fetch failed: ${res.statusText}`);
  return res.json();
}

export async function submitFeedback(feedbackData) {
  let res;
  try {
    res = await fetch(`${BASE_URL}/api/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(feedbackData)
    });
  } catch (netErr) {
    throw new Error(`Network connection error: Unable to reach backend server at ${BASE_URL || window.location.origin}. Please check that the backend is running.`);
  }

  if (!res.ok) {
    const errorJson = await res.json().catch(() => ({}));
    let detailMsg = errorJson.detail;
    if (Array.isArray(detailMsg)) {
      // Cleanly format FastAPI/Pydantic validation errors
      detailMsg = detailMsg
        .map(d => `${d.loc ? d.loc.filter(x => x !== 'body').join('.') + ': ' : ''}${d.msg}`)
        .join('; ');
    } else if (typeof detailMsg === 'object' && detailMsg !== null) {
      detailMsg = JSON.stringify(detailMsg);
    }
    throw new Error(detailMsg || `Feedback submission failed (HTTP ${res.status}): ${res.statusText}`);
  }
  return res.json();
}

export async function fetchFeedbackSummary() {
  let res;
  try {
    res = await fetch(`${BASE_URL}/api/feedback/summary`);
  } catch (netErr) {
    throw new Error(`Failed to connect to backend summary endpoint: ${netErr.message}`);
  }
  if (!res.ok) throw new Error(`Feedback summary fetch failed (HTTP ${res.status}): ${res.statusText}`);
  return res.json();
}

export async function fetchFeedbackList(limit = 50, offset = 0) {
  let res;
  try {
    const params = new URLSearchParams({ limit, offset });
    res = await fetch(`${BASE_URL}/api/feedback?${params.toString()}`);
  } catch (netErr) {
    throw new Error(`Failed to connect to feedback records endpoint: ${netErr.message}`);
  }
  if (!res.ok) throw new Error(`Feedback list fetch failed (HTTP ${res.status}): ${res.statusText}`);
  return res.json();
}

export async function fetchSingleFeedback(feedbackId) {
  const res = await fetch(`${BASE_URL}/api/feedback/${encodeURIComponent(feedbackId)}`);
  if (!res.ok) throw new Error(`Failed to retrieve feedback ${feedbackId}: ${res.statusText}`);
  return res.json();
}
