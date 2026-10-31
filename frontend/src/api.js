const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

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
