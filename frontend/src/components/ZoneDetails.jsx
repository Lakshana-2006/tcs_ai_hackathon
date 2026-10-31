import React, { useState } from 'react';
import { 
  AlertCircle, 
  Thermometer, 
  Users, 
  Shield, 
  CheckCircle2, 
  TrendingDown, 
  Info, 
  Droplets, 
  Trees, 
  Building2, 
  Hospital, 
  Zap, 
  Waves, 
  HeartPulse, 
  Clock, 
  Layers, 
  ChevronDown, 
  ChevronUp, 
  Cpu,
  Satellite,
  Database,
  Calendar,
  Sparkles,
  Activity
} from 'lucide-react';

export default function ZoneDetails({ zone, city, simulationResult, satelliteStatus }) {
  const [activeTab, setActiveTab] = useState('all'); // 'all', 'satellite', 'environment', 'demographics', 'infrastructure', 'ipcc'

  if (!zone) {
    return (
      <div className="glass-panel rounded-xl p-6 text-center text-slate-500 flex flex-col items-center justify-center h-full min-h-[300px]">
        <Info className="w-8 h-8 text-slate-600 mb-2 animate-pulse" />
        <p className="text-sm font-medium">Select a spatial sector from the map or dropdown above</p>
        <p className="text-xs text-slate-600 mt-1">Explore satellite observations, microclimate hazards, exposure, vulnerability, and infrastructure telemetry</p>
      </div>
    );
  }

  const isSimulated = simulationResult && simulationResult.zone_id === zone.id;
  const currentRisk = isSimulated ? simulationResult.simulated.composite_risk : zone.baseline_risk;
  const baselineRisk = zone.baseline_risk;
  const deltaRisk = isSimulated ? simulationResult.risk_delta : 0;

  const getSeverityBadge = (score) => {
    if (score >= 78) return { label: 'CRITICAL HOTSPOT', bg: 'bg-rose-500/20 text-rose-400 border-rose-500/40' };
    if (score >= 65) return { label: 'ELEVATED RISK', bg: 'bg-orange-500/20 text-orange-400 border-orange-500/40' };
    if (score >= 45) return { label: 'MODERATE CONCERN', bg: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40' };
    return { label: 'CLIMATE RESILIENT', bg: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40' };
  };

  const badge = getSeverityBadge(currentRisk);

  // Helper to safely render values
  const renderVal = (val, suffix = '') => {
    if (val === null || val === undefined || val === '') {
      return <span className="text-slate-500 italic text-[11px]">Data unavailable</span>;
    }
    return <span>{val}{suffix}</span>;
  };

  const env = zone.heat_environmental || {};
  const pop = zone.population_vulnerability || {};
  const infra = zone.urban_infrastructure || {};
  const sat = zone.satellite_data;
  const isRealSatellite = zone.is_real_satellite && sat !== null && sat !== undefined;

  return (
    <div className="glass-panel rounded-xl p-4 flex flex-col gap-3.5">
      {/* Zone Header */}
      <div className="flex items-start justify-between gap-3 border-b border-slate-800 pb-3">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="text-base font-bold text-white">{zone.name}</h3>
            <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full border ${badge.bg}`}>
              {badge.label}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 flex items-center gap-2 flex-wrap">
            <span>{zone.type}</span>
            <span>•</span>
            <span>{zone.area_km2} km²</span>
            <span>•</span>
            <span className="font-mono text-slate-300">
              {pop.total_population ? pop.total_population.toLocaleString() : zone.population?.toLocaleString()} residents
            </span>
          </p>
        </div>

        {/* Risk Score Pill */}
        <div className="text-right shrink-0">
          <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Composite Risk</div>
          <div className="flex items-baseline justify-end gap-1.5">
            {isSimulated && deltaRisk > 0 && (
              <span className="text-xs text-slate-400 line-through font-mono">
                {baselineRisk}
              </span>
            )}
            <span className={`text-2xl font-black font-mono ${
              currentRisk >= 75 ? 'text-rose-400' : currentRisk >= 60 ? 'text-orange-400' : 'text-emerald-400'
            }`}>
              {currentRisk}
            </span>
            <span className="text-xs text-slate-500">/ 100</span>
          </div>
          {isSimulated && deltaRisk > 0 && (
            <div className="text-[10px] text-emerald-400 font-mono font-medium flex items-center justify-end gap-1">
              <TrendingDown className="w-3 h-3" /> -{deltaRisk} pts (-{simulationResult.risk_reduction_pct}%)
            </div>
          )}
        </div>
      </div>

      {/* Parameter Category Selector Tabs */}
      <div className="flex items-center gap-1 bg-slate-900/90 p-1 rounded-lg border border-slate-800 text-xs overflow-x-auto">
        {[
          { id: 'all', label: 'All Indicators' },
          { id: 'satellite', label: '🛰️ Satellite Observations' },
          { id: 'environment', label: 'Weather & Climate' },
          { id: 'demographics', label: 'Demographics' },
          { id: 'infrastructure', label: 'Infrastructure' },
          { id: 'ipcc', label: 'IPCC Framework' }
        ].map(tab => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`px-2.5 py-1 rounded text-xs font-medium whitespace-nowrap transition ${
              activeTab === tab.id
                ? 'bg-rose-500 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* SECTION 1: GENUINE GOOGLE EARTH ENGINE SATELLITE OBSERVATIONS */}
      {(activeTab === 'all' || activeTab === 'satellite') && (
        <div className="bg-slate-900/90 rounded-lg p-3 border border-cyan-500/30 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
            <span className="text-xs font-bold text-cyan-400 flex items-center gap-1.5">
              <Satellite className="w-4 h-4 text-cyan-400" />
              <span>Latest Available Satellite Observations (Google Earth Engine)</span>
            </span>
            <span className={`text-[9px] uppercase font-mono font-bold px-2 py-0.5 rounded border ${
              isRealSatellite 
                ? 'bg-emerald-950/80 text-emerald-400 border-emerald-500/40' 
                : 'bg-amber-950/60 text-amber-300 border-amber-500/40'
            }`}>
              {isRealSatellite ? 'SATELLITE-DERIVED' : 'PRE-AUTH SECTOR BASELINE'}
            </span>
          </div>

          {isRealSatellite && sat ? (
            <div className="space-y-2.5 text-xs">
              {/* Landsat 8/9 LST Thermal Stats */}
              <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800 space-y-1.5">
                <div className="flex items-center justify-between text-slate-300">
                  <span className="font-semibold text-rose-300">Landsat 8/9 Thermal Land Surface Temperature (LST)</span>
                  <span className="text-[10px] font-mono text-slate-400">Resolution: 30m • QA_PIXEL Masked</span>
                </div>
                <div className="grid grid-cols-3 gap-2 font-mono text-center pt-1">
                  <div className="bg-slate-900/80 p-1.5 rounded border border-slate-800">
                    <div className="text-[10px] text-slate-400">Mean LST</div>
                    <div className="text-sm font-bold text-rose-400">{sat.landsat_lst.mean_lst_c}°C</div>
                  </div>
                  <div className="bg-slate-900/80 p-1.5 rounded border border-slate-800">
                    <div className="text-[10px] text-slate-400">Min LST</div>
                    <div className="text-sm font-bold text-cyan-300">{sat.landsat_lst.min_lst_c}°C</div>
                  </div>
                  <div className="bg-slate-900/80 p-1.5 rounded border border-slate-800">
                    <div className="text-[10px] text-slate-400">Max LST</div>
                    <div className="text-sm font-bold text-amber-400">{sat.landsat_lst.max_lst_c}°C</div>
                  </div>
                </div>
                <div className="text-[10px] text-slate-400 flex items-center justify-between pt-0.5">
                  <span>Satellite: {sat.landsat_lst.satellite}</span>
                  <span>Acquired: {sat.landsat_lst.acquisition_date}</span>
                </div>
              </div>

              {/* Sentinel-2 Surface Reflectance Indices */}
              <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800 space-y-1.5">
                <div className="flex items-center justify-between text-slate-300">
                  <span className="font-semibold text-emerald-300">Sentinel-2 MSI Surface Reflectance (Level-2A)</span>
                  <span className="text-[10px] font-mono text-slate-400">Resolution: 10m - 20m</span>
                </div>
                <div className="grid grid-cols-3 gap-2 font-mono text-center pt-1">
                  <div className="bg-slate-900/80 p-1.5 rounded border border-slate-800">
                    <div className="text-[10px] text-slate-400">NDVI (Veg)</div>
                    <div className="text-sm font-bold text-emerald-400">{sat.sentinel2_indices.ndvi_mean ?? 'N/A'}</div>
                  </div>
                  <div className="bg-slate-900/80 p-1.5 rounded border border-slate-800">
                    <div className="text-[10px] text-slate-400">NDWI (Water)</div>
                    <div className="text-sm font-bold text-sky-300">{sat.sentinel2_indices.ndwi_mean ?? 'N/A'}</div>
                  </div>
                  <div className="bg-slate-900/80 p-1.5 rounded border border-slate-800">
                    <div className="text-[10px] text-slate-400">NDBI (Built)</div>
                    <div className="text-sm font-bold text-amber-400">{sat.sentinel2_indices.ndbi_mean ?? 'N/A'}</div>
                  </div>
                </div>
                <div className="text-[10px] text-slate-400 flex items-center justify-between pt-0.5">
                  <span>Vegetation Cover: {sat.sentinel2_indices.vegetation_cover_pct}%</span>
                  <span>Acquired: {sat.sentinel2_indices.acquisition_date}</span>
                </div>
                <div className="text-[9px] text-slate-500 italic">
                  * Note: Sentinel-2 provides multispectral surface reflectance; thermal LST is derived from Landsat 8/9 ST_B10 and MODIS.
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-slate-950/70 p-3 rounded-lg border border-amber-500/30 space-y-2 text-xs">
              <div className="flex items-center gap-2 text-amber-300 font-semibold">
                <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
                <span>Earth Engine Credentials Standby</span>
              </div>
              <p className="text-slate-300 leading-relaxed text-[11px]">
                The backend's Earth Engine Python integration (<code className="text-emerald-400">earthengine-api</code>) is installed and operational. To pull live Landsat 8/9 and Sentinel-2 zonal rasters for <strong>{city?.name || 'this city'}</strong>:
              </p>
              <div className="bg-slate-900 p-2 rounded border border-slate-800 font-mono text-[10px] text-cyan-300">
                Configure <span className="text-white">EE_PROJECT_ID</span> and <span className="text-white">EE_SERVICE_ACCOUNT</span> in <code className="text-amber-300">backend/.env</code>
              </div>
              <p className="text-[10px] text-slate-400">
                Current metrics below represent <strong>pre-authentication spatial sector estimates</strong> and Open-Meteo live weather data.
              </p>
            </div>
          )}
        </div>
      )}

      {/* SECTION 2: WEATHER AND AMBIENT HEAT (OPEN-METEO API) */}
      {(activeTab === 'all' || activeTab === 'environment') && (
        <div className="bg-slate-900/80 rounded-lg p-3 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-1.5">
            <span className="text-xs font-bold text-rose-400 flex items-center gap-1.5">
              <Thermometer className="w-3.5 h-3.5" /> Atmospheric Weather Conditions
            </span>
            <span className="text-[9px] uppercase font-mono font-bold px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              WEATHER API (OPEN-METEO)
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
            <div className="bg-slate-950/60 p-2 rounded border border-slate-800/70">
              <div className="text-[11px] text-slate-400">Air Temperature:</div>
              <div className="text-sm font-bold font-mono text-white mt-0.5">
                {renderVal(env.air_temperature_c, '°C')}
              </div>
              <div className="text-[10px] text-slate-500 flex items-center gap-1 mt-0.5">
                <Clock className="w-2.5 h-2.5" /> {env.timestamp || 'Open-Meteo Live API'}
              </div>
            </div>

            <div className="bg-slate-950/60 p-2 rounded border border-slate-800/70">
              <div className="text-[11px] text-slate-400">Relative Humidity:</div>
              <div className="text-sm font-bold font-mono text-cyan-300 mt-0.5">
                {renderVal(env.relative_humidity_pct, '%')}
              </div>
              <div className="text-[10px] text-slate-500 flex items-center gap-1 mt-0.5">
                <Droplets className="w-2.5 h-2.5" /> Feels like (Heat Index): {renderVal(env.apparent_temperature_c, '°C')}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* SECTION 3: POPULATION AND VULNERABILITY (MUNICIPAL / CENSUS DATASET) */}
      {(activeTab === 'all' || activeTab === 'demographics') && (
        <div className="bg-slate-900/80 rounded-lg p-3 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-1.5">
            <span className="text-xs font-bold text-amber-400 flex items-center gap-1.5">
              <Users className="w-3.5 h-3.5" /> Population & Demographic Vulnerability
            </span>
            <span className="text-[9px] uppercase font-mono font-bold px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
              DEMOGRAPHIC DATASET
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="bg-slate-950/60 p-2 rounded border border-slate-800/70">
              <div className="text-[11px] text-slate-400">Sector Population:</div>
              <div className="text-sm font-bold font-mono text-white mt-0.5">
                {pop.total_population ? pop.total_population.toLocaleString() : renderVal(zone.population)}
              </div>
              <div className="text-[10px] text-slate-500 font-mono">
                Density: {zone.baseline_exposure?.population_density_sqkm?.toLocaleString()}/km²
              </div>
            </div>

            <div className="bg-slate-950/60 p-2 rounded border border-slate-800/70">
              <div className="text-[11px] text-slate-400">Senior Residents (&gt;65):</div>
              <div className="text-sm font-bold font-mono text-indigo-300 mt-0.5">
                {pop.elderly_population?.count ? pop.elderly_population.count.toLocaleString() : renderVal(zone.baseline_vulnerability?.elderly_count)}
                <span className="text-xs text-slate-400 font-normal ml-1">
                  ({pop.elderly_population?.pct || zone.baseline_vulnerability?.elderly_pct}%)
                </span>
              </div>
              <div className="text-[10px] text-slate-500">
                Children (&lt;5): {pop.children_population?.pct || zone.baseline_vulnerability?.children_pct}%
              </div>
            </div>

            <div className="bg-slate-950/60 p-2 rounded border border-slate-800/70">
              <div className="text-[11px] text-slate-400">Outdoor Labor Ratio:</div>
              <div className="text-sm font-bold font-mono text-amber-400 mt-0.5">
                {renderVal(pop.outdoor_workers?.pct || zone.baseline_exposure?.outdoor_worker_pct, '%')}
              </div>
              <div className="text-[10px] text-slate-500 font-mono">
                Count: {pop.outdoor_workers?.count ? pop.outdoor_workers.count.toLocaleString() : renderVal(zone.baseline_exposure?.outdoor_worker_count)}
              </div>
            </div>

            <div className="bg-slate-950/60 p-2 rounded border border-slate-800/70">
              <div className="text-[11px] text-slate-400">Mechanical A/C Deficit:</div>
              <div className="text-sm font-bold font-mono text-rose-300 mt-0.5">
                {renderVal(pop.ac_access?.lacks_ac_pct || zone.baseline_vulnerability?.ac_deficit_pct, '%')}
              </div>
              <div className="text-[10px] text-slate-500">
                Lacks home climate control
              </div>
            </div>
          </div>
        </div>
      )}

      {/* SECTION 4: URBAN INFRASTRUCTURE (MUNICIPAL SURVEY) */}
      {(activeTab === 'all' || activeTab === 'infrastructure') && (
        <div className="bg-slate-900/80 rounded-lg p-3 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-1.5">
            <span className="text-xs font-bold text-sky-400 flex items-center gap-1.5">
              <Building2 className="w-3.5 h-3.5" /> Urban Infrastructure & Adaptive Capacity
            </span>
            <span className="text-[9px] uppercase font-mono font-bold px-1.5 py-0.5 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20">
              INFRASTRUCTURE SURVEY
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
            <div className="bg-slate-950/60 p-2 rounded border border-slate-800/70">
              <div className="text-[11px] text-slate-400 flex items-center gap-1">
                <Hospital className="w-3 h-3 text-rose-400" /> Hospital Availability:
              </div>
              <div className="text-xs font-semibold text-slate-200 mt-1">
                {renderVal(infra.hospital_availability)}
              </div>
            </div>

            <div className="bg-slate-950/60 p-2 rounded border border-slate-800/70">
              <div className="text-[11px] text-slate-400 flex items-center gap-1">
                <Shield className="w-3 h-3 text-amber-400" /> Cooling Hub Availability:
              </div>
              <div className="text-xs font-semibold text-slate-200 mt-1">
                {renderVal(infra.cooling_facilities)}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* SECTION 5: IPCC MULTI-CRITERIA RISK ESTIMATE */}
      {(activeTab === 'all' || activeTab === 'ipcc') && (
        <div className="bg-slate-900/80 rounded-lg p-3 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-1.5">
            <span className="text-xs font-bold text-purple-400 flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5" /> IPCC Multi-Criteria Risk Breakdown
            </span>
            <span className="text-[9px] uppercase font-mono font-bold px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">
              CALCULATED RISK ESTIMATE
            </span>
          </div>

          <div className="grid grid-cols-3 gap-2 font-mono text-center text-xs">
            <div className="bg-slate-950/60 p-2 rounded border border-slate-800">
              <div className="text-[10px] text-slate-400">Hazard Score</div>
              <div className="text-sm font-bold text-rose-400 mt-0.5">
                {zone.baseline_hazard?.hazard_score ?? 'N/A'}
              </div>
              <div className="text-[9px] text-slate-500 mt-0.5">Weight: 35%</div>
            </div>

            <div className="bg-slate-950/60 p-2 rounded border border-slate-800">
              <div className="text-[10px] text-slate-400">Exposure Score</div>
              <div className="text-sm font-bold text-amber-400 mt-0.5">
                {zone.baseline_exposure?.exposure_score ?? 'N/A'}
              </div>
              <div className="text-[9px] text-slate-500 mt-0.5">Weight: 30%</div>
            </div>

            <div className="bg-slate-950/60 p-2 rounded border border-slate-800">
              <div className="text-[10px] text-slate-400">Vulnerability</div>
              <div className="text-sm font-bold text-indigo-400 mt-0.5">
                {zone.baseline_vulnerability?.vulnerability_score ?? 'N/A'}
              </div>
              <div className="text-[9px] text-slate-500 mt-0.5">Weight: 35%</div>
            </div>
          </div>
        </div>
      )}

      {/* Tailored Priorities Notice */}
      <div>
        <div className="text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          <span>Tailored Intervention Priorities for {zone.short_name || zone.name}</span>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {zone.recommended_priorities && zone.recommended_priorities.map(p => {
            const labels = {
              tree_planting: 'Urban Tree Planting',
              cool_roofs: 'Cool Roof Retrofits',
              cooling_centers: 'Emergency Cooling Hubs',
              permeable_pavements: 'Reflective Permeable Pavement',
              green_corridors: 'Shaded Transit & Misting Stops'
            };
            return (
              <span
                key={p}
                className="text-xs font-medium px-2.5 py-1 rounded bg-slate-800 text-slate-200 border border-slate-700 flex items-center gap-1"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                {labels[p] || p}
              </span>
            );
          })}
        </div>
      </div>

      {/* Data Source Transparency Footer */}
      <div className="text-[10px] text-slate-500 italic border-t border-slate-800/60 pt-2 flex flex-col gap-1">
        <span>* <strong>Data Provenance:</strong> Satellite parameters (LST, NDVI, NDWI, NDBI) derived via Google Earth Engine; atmospheric weather via Open-Meteo; population and infrastructure metrics derived from municipal planning heuristics.</span>
      </div>
    </div>
  );
}
