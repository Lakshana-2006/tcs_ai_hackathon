import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Polygon, Marker, Tooltip, useMap } from 'react-leaflet';
import L from 'leaflet';
import { 
  Layers, 
  Satellite, 
  Info, 
  Sparkles, 
  MapPin, 
  AlertCircle, 
  CheckCircle2,
  Calendar,
  Eye,
  Sliders
} from 'lucide-react';

// Fix Leaflet's default icon path in bundlers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Helper component to smoothly fly/pan map when selected city coordinates change
function MapController({ center, zoom = 12 }) {
  const map = useMap();
  useEffect(() => {
    if (center && center.length === 2 && !isNaN(center[0]) && !isNaN(center[1])) {
      map.flyTo(center, zoom, { duration: 1.5 });
    }
  }, [center, zoom, map]);
  return null;
}

export default function HeatMap({ 
  city, 
  zones, 
  selectedZoneId, 
  onSelectZone, 
  simulationResult,
  satelliteLayers = {},
  satelliteStatus = null
}) {
  const [activeLayer, setActiveLayer] = useState('risk'); // 'risk', 'hazard', 'vulnerability', 'exposure'
  const [activeSatelliteRaster, setActiveSatelliteRaster] = useState('none'); // 'none', 'lst', 'ndvi', 'ndwi', 'ndbi'

  const centerPos = city 
    ? [city.latitude, city.longitude] 
    : [13.0827, 80.2707];

  const isEeAuth = satelliteStatus?.authenticated;

  // Get color scale based on active metric
  const getZoneColor = (zone) => {
    let val = 0;
    if (activeLayer === 'risk') {
      if (simulationResult && simulationResult.zone_id === zone.id) {
        val = simulationResult.simulated.composite_risk;
      } else {
        val = zone.baseline_risk;
      }
      if (val >= 78) return '#e11d48'; // Critical Red
      if (val >= 65) return '#f97316'; // High Orange
      if (val >= 45) return '#eab308'; // Moderate Yellow
      return '#22c55e'; // Resilient Green
    }

    if (activeLayer === 'hazard') {
      val = zone.baseline_hazard?.hazard_score ?? 50;
      if (val >= 80) return '#ef4444';
      if (val >= 60) return '#f97316';
      if (val >= 40) return '#fbbf24';
      return '#10b981';
    }

    if (activeLayer === 'vulnerability') {
      val = zone.baseline_vulnerability?.vulnerability_score ?? 50;
      if (val >= 80) return '#a855f7';
      if (val >= 60) return '#ec4899';
      if (val >= 40) return '#3b82f6';
      return '#06b6d4';
    }

    if (activeLayer === 'exposure') {
      val = zone.baseline_exposure?.exposure_score ?? 50;
      if (val >= 80) return '#f43f5e';
      if (val >= 60) return '#fb923c';
      if (val >= 40) return '#38bdf8';
      return '#4ade80';
    }

    return '#f43f5e';
  };

  const getMetricDisplay = (zone) => {
    if (activeLayer === 'risk') {
      const isSim = simulationResult && simulationResult.zone_id === zone.id;
      const score = isSim ? simulationResult.simulated.composite_risk : zone.baseline_risk;
      return `Risk: ${score}${isSim ? ' (Simulated)' : ''}`;
    }
    if (activeLayer === 'hazard') {
      const realLst = zone.satellite_data?.landsat_lst?.mean_lst_c;
      if (realLst !== undefined && realLst !== null) {
        return `Sat LST: ${realLst}°C (${zone.baseline_hazard.hazard_score} pts)`;
      }
      return `LST Anomaly: +${zone.baseline_hazard.lst_anomaly_c}°C (${zone.baseline_hazard.hazard_score} pts)`;
    }
    if (activeLayer === 'vulnerability') {
      const ndvi = zone.satellite_data?.sentinel2_indices?.ndvi_mean;
      const ndviText = ndvi !== undefined && ndvi !== null ? ` | NDVI: ${ndvi}` : '';
      return `SVI: ${zone.baseline_vulnerability.svi_score}${ndviText}`;
    }
    if (activeLayer === 'exposure') {
      return `Density: ${(zone.baseline_exposure.population_density_sqkm || 15000).toLocaleString()}/km²`;
    }
    return '';
  };

  const createCustomBadge = (zone, isSelected) => {
    const color = getZoneColor(zone);
    const isSim = simulationResult && simulationResult.zone_id === zone.id;
    const score = isSim ? simulationResult.simulated.composite_risk : zone.baseline_risk;
    const isRealSat = zone.is_real_satellite;

    const html = `
      <div style="
        background: rgba(15, 23, 42, 0.94);
        border: 2px solid ${isSelected ? '#38bdf8' : color};
        border-radius: 9999px;
        padding: 3px 8px;
        color: #f8fafc;
        font-family: inherit;
        font-size: 11px;
        font-weight: 700;
        box-shadow: 0 4px 14px rgba(0,0,0,0.7);
        display: flex;
        align-items: center;
        gap: 5px;
        white-space: nowrap;
        transform: translate(-50%, -50%);
        cursor: pointer;
      ">
        <span style="
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: ${color};
          display: inline-block;
          box-shadow: 0 0 6px ${color};
        "></span>
        <span>${zone.short_name || zone.name}</span>
        <span style="
          background: ${color}22;
          color: ${color};
          padding: 1px 4px;
          border-radius: 4px;
          font-family: monospace;
          font-size: 10px;
        ">${score}</span>
      </div>
    `;

    return L.divIcon({
      html,
      className: 'custom-leaflet-badge',
      iconSize: [0, 0],
    });
  };

  const activeSatTile = satelliteLayers && satelliteLayers[activeSatelliteRaster];

  return (
    <div className="glass-panel rounded-xl p-4 flex flex-col gap-3 relative">
      {/* Map Header & Multi-Layer Controls */}
      <div className="flex flex-col gap-2.5 z-10">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
          <div>
            <h2 className="text-sm font-semibold text-white flex items-center gap-2">
              <span>{city ? city.name : 'Urban'} Climate Resilience Digital Twin</span>
              <span className="text-[10px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded font-normal">
                5 Geographically Defined Sectors
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Center: <span className="font-mono text-slate-300">{centerPos[0].toFixed(4)}°, {centerPos[1].toFixed(4)}°</span> • Authenticated satellite & multi-criteria layers
            </p>
          </div>

          {/* Satellite Pipeline Status Indicator */}
          <div className="flex items-center gap-2">
            <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full flex items-center gap-1 border ${
              isEeAuth 
                ? 'bg-emerald-950/80 text-emerald-400 border-emerald-500/40' 
                : 'bg-slate-900 text-amber-300 border-amber-500/30'
            }`}>
              <Satellite className="w-3 h-3" />
              <span>{isEeAuth ? 'GEE Authenticated' : 'GEE Standby (Auth Required)'}</span>
            </span>
          </div>
        </div>

        {/* Dual Control Bars */}
        <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-slate-800/80">
          {/* 1. Vector Risk Layer Toggles */}
          <div className="flex items-center gap-1 bg-slate-900/90 p-1 rounded-lg border border-slate-800 text-xs">
            <span className="text-[10px] uppercase font-bold text-slate-500 px-2 flex items-center gap-1">
              <Layers className="w-3 h-3" /> Vectors
            </span>
            {[
              { id: 'risk', label: 'Composite Risk' },
              { id: 'hazard', label: 'Hazard & LST' },
              { id: 'vulnerability', label: 'Vulnerability (SVI)' },
              { id: 'exposure', label: 'Exposure' }
            ].map(layer => (
              <button
                key={layer.id}
                type="button"
                onClick={() => setActiveLayer(layer.id)}
                className={`px-2.5 py-1 rounded text-xs font-medium transition ${
                  activeLayer === layer.id
                    ? 'bg-rose-500 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {layer.label}
              </button>
            ))}
          </div>

          {/* 2. Earth Engine Satellite Raster Toggles */}
          <div className="flex items-center gap-1 bg-slate-900/90 p-1 rounded-lg border border-slate-800 text-xs">
            <span className="text-[10px] uppercase font-bold text-cyan-400 px-2 flex items-center gap-1">
              <Satellite className="w-3 h-3 text-cyan-400" /> Satellite Raster
            </span>
            {[
              { id: 'none', label: 'Off' },
              { id: 'lst', label: 'LST Thermal (30m)' },
              { id: 'ndvi', label: 'NDVI Veg (10m)' },
              { id: 'ndwi', label: 'NDWI Water (10m)' },
              { id: 'ndbi', label: 'NDBI Built (20m)' }
            ].map(sat => (
              <button
                key={sat.id}
                type="button"
                onClick={() => setActiveSatelliteRaster(sat.id)}
                className={`px-2 py-1 rounded text-xs font-medium transition ${
                  activeSatelliteRaster === sat.id
                    ? 'bg-cyan-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {sat.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Satellite Metadata Strip */}
      {activeSatelliteRaster !== 'none' && (
        <div className="bg-slate-950/80 border border-cyan-500/30 rounded-lg px-3 py-1.5 text-[11px] text-cyan-200 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Satellite className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            <span>
              <strong>Latest Available Observation:</strong> {activeSatTile?.name || activeSatelliteRaster.toUpperCase()}
            </span>
            <span className="text-slate-400">|</span>
            <span className="font-mono text-[10px] text-slate-300">
              Dataset: {activeSatTile?.dataset || 'Earth Engine ImageCollection'}
            </span>
          </div>

          <div className="flex items-center gap-2 font-mono text-[10px] text-slate-400">
            <span>Resolution: {activeSatTile?.resolution || 'Native Satellite'}</span>
            <span>•</span>
            {activeSatTile?.url ? (
              <span className="text-emerald-400 font-bold">Streaming EE Tiles</span>
            ) : (
              <span className="text-amber-400">Standby (Credentials Required)</span>
            )}
          </div>
        </div>
      )}

      {/* Map Canvas */}
      <div className="h-[430px] rounded-lg overflow-hidden border border-slate-800 relative">
        <MapContainer
          center={centerPos}
          zoom={12}
          scrollWheelZoom={true}
          className="h-full w-full"
          attributionControl={false}
        >
          <MapController center={centerPos} zoom={12} />

          {/* Base Map: OpenStreetMap */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* Genuine Earth Engine Satellite Raster Overlay (if authenticated & active) */}
          {activeSatTile && activeSatTile.url && (
            <TileLayer
              key={activeSatelliteRaster}
              url={activeSatTile.url}
              opacity={0.70}
              zIndex={400}
            />
          )}

          {/* Five Geographically Defined Sector Polygons */}
          {zones && zones.map(zone => {
            const isSelected = selectedZoneId === zone.id;
            const color = getZoneColor(zone);
            const sat = zone.satellite_data;

            return (
              <React.Fragment key={zone.id}>
                {/* Zone Polygon */}
                <Polygon
                  positions={zone.polygon}
                  pathOptions={{
                    color: isSelected ? '#38bdf8' : color,
                    weight: isSelected ? 3 : 2,
                    fillColor: color,
                    fillOpacity: activeSatelliteRaster !== 'none' ? 0.25 : (isSelected ? 0.60 : 0.40),
                    dashArray: isSelected ? '4, 4' : null,
                  }}
                  eventHandlers={{
                    click: () => onSelectZone(zone.id)
                  }}
                >
                  <Tooltip sticky direction="top" className="custom-zone-label">
                    <div className="space-y-1">
                      <div className="font-bold text-rose-300">{zone.name}</div>
                      <div className="text-[11px] text-slate-300">{zone.type}</div>
                      <div className="text-[11px] font-mono text-emerald-400">
                        {getMetricDisplay(zone)}
                      </div>

                      {/* Real Satellite Observations if present */}
                      {sat && sat.landsat_lst?.mean_lst_c !== null && (
                        <div className="pt-1 border-t border-slate-700/80 font-mono text-[10px] text-cyan-300">
                          <div>Landsat 8/9 LST: {sat.landsat_lst.mean_lst_c}°C (Min {sat.landsat_lst.min_lst_c}°C / Max {sat.landsat_lst.max_lst_c}°C)</div>
                          <div>Sentinel-2 NDVI: {sat.sentinel2_indices?.ndvi_mean ?? 'N/A'} • Veg: {sat.sentinel2_indices?.vegetation_cover_pct ?? 'N/A'}%</div>
                          <div className="text-slate-400 text-[9px]">Acquired: {sat.landsat_lst.acquisition_date}</div>
                        </div>
                      )}

                      {!sat && (
                        <div className="text-[9px] text-amber-400 italic">
                          Baseline Estimate • GEE Satellite Sync Pending
                        </div>
                      )}

                      <div className="text-[10px] text-slate-400">
                        Pop: {zone.population ? zone.population.toLocaleString() : 'N/A'}
                      </div>
                    </div>
                  </Tooltip>
                </Polygon>

                {/* Centroid Interactive Marker */}
                <Marker
                  position={zone.centroid}
                  icon={createCustomBadge(zone, isSelected)}
                  eventHandlers={{
                    click: () => onSelectZone(zone.id)
                  }}
                />
              </React.Fragment>
            );
          })}
        </MapContainer>

        {/* Legend Overlay */}
        <div className="absolute bottom-3 left-3 z-[1000] bg-slate-900/90 backdrop-blur border border-slate-800 rounded-lg p-2.5 text-[11px] shadow-lg max-w-[320px]">
          {activeSatelliteRaster === 'none' ? (
            <>
              <div className="font-semibold text-slate-300 mb-1.5 flex items-center justify-between">
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-rose-500"></span>
                  <span>{activeLayer.toUpperCase()} SCALE</span>
                </span>
                <span className="text-[9px] text-slate-500 font-mono">0 - 100</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="flex items-center gap-1 text-slate-400">
                  <span className="w-2.5 h-2.5 rounded-sm bg-rose-600 inline-block"></span> Critical (&gt;75)
                </span>
                <span className="flex items-center gap-1 text-slate-400">
                  <span className="w-2.5 h-2.5 rounded-sm bg-orange-500 inline-block"></span> High
                </span>
                <span className="flex items-center gap-1 text-slate-400">
                  <span className="w-2.5 h-2.5 rounded-sm bg-yellow-500 inline-block"></span> Mod
                </span>
                <span className="flex items-center gap-1 text-slate-400">
                  <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500 inline-block"></span> Low
                </span>
              </div>
            </>
          ) : activeSatelliteRaster === 'lst' ? (
            <>
              <div className="font-semibold text-cyan-300 mb-1 flex items-center gap-1.5">
                <Satellite className="w-3 h-3 text-cyan-400" />
                <span>LANDSAT 8/9 LST (°C)</span>
              </div>
              <div className="h-2 w-full rounded-full bg-gradient-to-r from-blue-600 via-yellow-400 to-red-600 my-1"></div>
              <div className="flex justify-between text-[10px] font-mono text-slate-400">
                <span>20°C (Cooler)</span>
                <span>35°C</span>
                <span>50°C (Thermal Peak)</span>
              </div>
            </>
          ) : activeSatelliteRaster === 'ndvi' ? (
            <>
              <div className="font-semibold text-emerald-300 mb-1 flex items-center gap-1.5">
                <Satellite className="w-3 h-3 text-emerald-400" />
                <span>SENTINEL-2 NDVI (Vegetation)</span>
              </div>
              <div className="h-2 w-full rounded-full bg-gradient-to-r from-[#8B4513] via-[#90EE90] to-[#006400] my-1"></div>
              <div className="flex justify-between text-[10px] font-mono text-slate-400">
                <span>-0.1 (Impervious/Water)</span>
                <span>0.35 (Canopy)</span>
                <span>0.75+ (Dense Forest)</span>
              </div>
            </>
          ) : activeSatelliteRaster === 'ndwi' ? (
            <>
              <div className="font-semibold text-blue-300 mb-1 flex items-center gap-1.5">
                <Satellite className="w-3 h-3 text-blue-400" />
                <span>SENTINEL-2 NDWI (Water / Moisture)</span>
              </div>
              <div className="h-2 w-full rounded-full bg-gradient-to-r from-slate-200 via-sky-400 to-blue-800 my-1"></div>
              <div className="flex justify-between text-[10px] font-mono text-slate-400">
                <span>-0.4 (Dry Built)</span>
                <span>0.0</span>
                <span>+0.4 (Water Bodies)</span>
              </div>
            </>
          ) : (
            <>
              <div className="font-semibold text-amber-300 mb-1 flex items-center gap-1.5">
                <Satellite className="w-3 h-3 text-amber-400" />
                <span>SENTINEL-2 NDBI (Built-Up Index)</span>
              </div>
              <div className="h-2 w-full rounded-full bg-gradient-to-r from-emerald-600 via-yellow-400 to-red-700 my-1"></div>
              <div className="flex justify-between text-[10px] font-mono text-slate-400">
                <span>-0.3 (Vegetation)</span>
                <span>0.0</span>
                <span>+0.4 (Dense Built Fabric)</span>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
