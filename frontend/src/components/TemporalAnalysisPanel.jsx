import React, { useState, useEffect } from 'react';
import { 
  Clock, 
  Calendar, 
  TrendingUp, 
  TrendingDown, 
  Sun, 
  Thermometer, 
  AlertTriangle, 
  Activity, 
  Layers, 
  ExternalLink,
  ChevronRight,
  Info,
  RefreshCw,
  Sparkles,
  Compass,
  ArrowRight
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend, 
  CartesianGrid 
} from 'recharts';
import { 
  fetchTemporalPast, 
  fetchTemporalPresent, 
  fetchTemporalFuture, 
  fetchTemporalClimate, 
  fetchTemporalComparison 
} from '../api';

export default function TemporalAnalysisPanel({ city, weather, zones, activeZoneId, onSelectZone }) {
  const [temporalMode, setTemporalMode] = useState('present'); // 'past', 'present', 'future', 'climate', 'compare'
  
  // Historical State
  const [startDate, setStartDate] = useState('2024-05-15');
  const [endDate, setEndDate] = useState('2024-05-22');
  const [histData, setHistData] = useState(null);
  const [histLoading, setHistLoading] = useState(false);
  const [histError, setHistError] = useState(null);

  // Forecast State
  const [forecastDays, setForecastDays] = useState(7);
  const [foreData, setForeData] = useState(null);
  const [foreLoading, setForeLoading] = useState(false);
  const [foreError, setForeError] = useState(null);

  // Climate Projection State
  const [climateModel, setClimateModel] = useState('EC_Earth3P_HR');
  const [climateData, setClimateData] = useState(null);
  const [climateLoading, setClimateLoading] = useState(false);

  // Comparison State
  const [compareData, setCompareData] = useState(null);
  const [compareLoading, setCompareLoading] = useState(false);

  // Load data based on mode
  useEffect(() => {
    if (!city || !city.latitude) return;

    if (temporalMode === 'past') {
      loadHistoricalData();
    } else if (temporalMode === 'future') {
      loadForecastData();
    } else if (temporalMode === 'climate') {
      loadClimateData();
    } else if (temporalMode === 'compare') {
      loadComparisonData();
    }
  }, [temporalMode, city, startDate, endDate, forecastDays, climateModel]);

  const loadHistoricalData = async () => {
    setHistLoading(true);
    setHistError(null);
    try {
      const res = await fetchTemporalPast(city.name, city.latitude, city.longitude, startDate, endDate);
      setHistData(res);
    } catch (err) {
      console.error('Past weather load error:', err);
      setHistError(err.message || 'Failed to retrieve historical reanalysis data.');
    } finally {
      setHistLoading(false);
    }
  };

  const loadForecastData = async () => {
    setForeLoading(true);
    setForeError(null);
    try {
      const res = await fetchTemporalFuture(city.name, city.latitude, city.longitude, forecastDays);
      setForeData(res);
    } catch (err) {
      console.error('Forecast weather load error:', err);
      setForeError(err.message || 'Failed to retrieve forecast data.');
    } finally {
      setForeLoading(false);
    }
  };

  const loadClimateData = async () => {
    setClimateLoading(true);
    try {
      const res = await fetchTemporalClimate(city.name, city.latitude, city.longitude, climateModel);
      setClimateData(res);
    } catch (err) {
      console.error('Climate load error:', err);
    } finally {
      setClimateLoading(false);
    }
  };

  const loadComparisonData = async () => {
    setCompareLoading(true);
    try {
      const res = await fetchTemporalComparison(city.name, city.latitude, city.longitude);
      setCompareData(res);
    } catch (err) {
      console.error('Comparison load error:', err);
    } finally {
      setCompareLoading(false);
    }
  };

  // Quick preset dates for historical mode
  const applyPreset = (s, e) => {
    setStartDate(s);
    setEndDate(e);
  };

  const ZONE_COLORS = {
    zone_1: '#f43f5e',
    zone_2: '#f97316',
    zone_3: '#e11d48',
    zone_4: '#06b6d4',
    zone_5: '#8b5cf6'
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5 sm:p-5 shadow-lg space-y-4">
      {/* Top Temporal Mode Selector Strip */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400">
            <Clock className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <span>Temporal Heat-Risk Horizon</span>
              <span className="text-xs font-mono font-normal text-slate-400">
                • {city?.name || 'Selected City'}
              </span>
            </h3>
            <p className="text-[11px] text-slate-400">
              Analyze thermal hazard trajectories across historical reanalysis, current telemetry, and future horizons
            </p>
          </div>
        </div>

        {/* Mode Buttons */}
        <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs w-full sm:w-auto overflow-x-auto">
          {[
            { id: 'past', label: 'Past (Historical)', icon: Calendar, badge: 'ERA5' },
            { id: 'present', label: 'Present (Live)', icon: Activity, badge: 'Live WMO' },
            { id: 'future', label: 'Future (Forecast)', icon: TrendingUp, badge: '7-14 Day' },
            { id: 'climate', label: 'Climate 2050', icon: Sun, badge: 'CMIP6' },
            { id: 'compare', label: 'Multi-Horizon', icon: Layers, badge: 'Compare' }
          ].map(m => {
            const Icon = m.icon;
            const isSelected = temporalMode === m.id;
            return (
              <button
                key={m.id}
                onClick={() => setTemporalMode(m.id)}
                className={`px-2.5 py-1.5 rounded-md font-bold flex items-center gap-1.5 transition whitespace-nowrap ${
                  isSelected
                    ? 'bg-rose-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{m.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* =========================================================================
          MODE 1: PAST (HISTORICAL REANALYSIS)
      ========================================================================= */}
      {temporalMode === 'past' && (
        <div className="space-y-3.5">
          {/* Controls Bar */}
          <div className="flex flex-wrap items-center justify-between gap-2.5 bg-slate-950/70 p-2.5 rounded-lg border border-slate-800 text-xs">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-slate-400 font-semibold">Historical Date Range:</span>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                max="2024-12-31"
                className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-slate-200 text-xs font-mono focus:outline-none focus:border-rose-500"
              />
              <span className="text-slate-500">to</span>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                max="2024-12-31"
                className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-slate-200 text-xs font-mono focus:outline-none focus:border-rose-500"
              />
            </div>

            {/* Quick Presets */}
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="text-slate-500 text-[10px] uppercase font-bold">Presets:</span>
              <button
                onClick={() => applyPreset('2024-05-15', '2024-05-25')}
                className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] border border-slate-700 font-medium transition"
              >
                May 2024 Heatwave
              </button>
              <button
                onClick={() => applyPreset('2023-06-01', '2023-06-15')}
                className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] border border-slate-700 font-medium transition"
              >
                June 2023 Summer
              </button>
              <button
                onClick={() => applyPreset('2022-04-20', '2022-04-30')}
                className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] border border-slate-700 font-medium transition"
              >
                April 2022 Peak
              </button>
            </div>
          </div>

          {histLoading && (
            <div className="py-12 text-center text-slate-400 text-xs flex flex-col items-center justify-center gap-2">
              <div className="w-6 h-6 border-2 border-rose-500 border-t-transparent rounded-full animate-spin"></div>
              <span>Querying Open-Meteo ERA5 Reanalysis Archive for {city.name}...</span>
            </div>
          )}

          {histError && !histLoading && (
            <div className="p-4 rounded-lg bg-rose-950/20 border border-rose-500/30 text-rose-300 text-xs">
              <AlertTriangle className="w-4 h-4 inline mr-1 text-rose-400" />
              {histError}
            </div>
          )}

          {histData && !histLoading && (
            <div className="space-y-3.5">
              {/* Summary Metric Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800 font-mono">
                  <span className="text-slate-400 block text-[10px]">HISTORICAL PEAK AIR TEMP</span>
                  <span className="text-base font-bold text-rose-400">{histData.peak_temperature_c}°C</span>
                  <span className="text-slate-500 block text-[9px] mt-0.5">ERA5 2m reanalysis</span>
                </div>

                <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800 font-mono">
                  <span className="text-slate-400 block text-[10px]">PEAK COMPOSITE RISK</span>
                  <span className="text-base font-bold text-amber-400">{histData.peak_risk_score} / 100</span>
                  <span className="text-slate-500 block text-[9px] mt-0.5">Recorded: {histData.peak_risk_date}</span>
                </div>

                <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800 font-mono">
                  <span className="text-slate-400 block text-[10px]">ANALYSIS OBSERVATIONS</span>
                  <span className="text-base font-bold text-cyan-300">{histData.days_count} Daily Records</span>
                  <span className="text-slate-500 block text-[9px] mt-0.5">{startDate} to {endDate}</span>
                </div>

                <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800 font-mono">
                  <span className="text-slate-400 block text-[10px]">REUSE FORMULA</span>
                  <span className="text-xs font-bold text-emerald-400">0.35H + 0.30E + 0.35V</span>
                  <span className="text-slate-500 block text-[9px] mt-0.5">Constant IPCC weights</span>
                </div>
              </div>

              {/* Historical Trend Chart */}
              <div className="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 space-y-2">
                <div className="flex items-center justify-between text-xs text-slate-300">
                  <span className="font-bold flex items-center gap-1.5">
                    <Activity className="w-3.5 h-3.5 text-rose-400" />
                    <span>Daily Heat Risk Progression Across All 5 Analysis Sectors</span>
                  </span>
                  <span className="text-[10px] font-mono text-slate-400">Source: Open-Meteo ERA5 Reanalysis</span>
                </div>

                <div className="h-56 w-full pt-2">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={histData.daily_timeline}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.4} />
                      <XAxis dataKey="date" stroke="#94a3b8" fontSize={10} tickLine={false} />
                      <YAxis stroke="#94a3b8" fontSize={10} domain={[10, 100]} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }}
                      />
                      <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '4px' }} />
                      <Line type="monotone" dataKey="average_city_risk" name="City Avg Risk" stroke="#ffffff" strokeWidth={2.5} dot={{ r: 3 }} />
                      {zones.map((z, idx) => {
                        const colors = ['#f43f5e', '#f97316', '#e11d48', '#06b6d4', '#8b5cf6'];
                        return (
                          <Line
                            key={z.id}
                            type="monotone"
                            dataKey={`zone_risks.${z.id}`}
                            name={z.short_name || z.name}
                            stroke={colors[idx % colors.length]}
                            strokeWidth={1.5}
                            dot={false}
                          />
                        );
                      })}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* =========================================================================
          MODE 2: PRESENT (REAL-TIME LIVE TELEMETRY)
      ========================================================================= */}
      {temporalMode === 'present' && (
        <div className="space-y-3.5">
          <div className="bg-slate-950/70 p-3.5 rounded-lg border border-emerald-500/30 flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="font-bold text-white">Live Real-Time Telemetry Active</span>
              <span className="text-slate-500">|</span>
              <span className="text-slate-300 font-mono text-[11px]">
                Updated: {weather?.timestamp || 'Latest WMO Station Sync'}
              </span>
            </div>

            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              OPERATIONAL WEATHER STREAM
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
            <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800 font-mono">
              <span className="text-slate-400 block text-[10px]">CURRENT AIR TEMP</span>
              <span className="text-lg font-bold text-white">{weather?.air_temperature_c ?? 30.0}°C</span>
              <span className="text-slate-500 block text-[9px] mt-0.5">WMO 2m sensor standard</span>
            </div>

            <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800 font-mono">
              <span className="text-slate-400 block text-[10px]">FEELS LIKE (HEAT INDEX)</span>
              <span className="text-lg font-bold text-rose-400">{weather?.apparent_temperature_c ?? 34.0}°C</span>
              <span className="text-slate-500 block text-[9px] mt-0.5">Steadman formula calculation</span>
            </div>

            <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800 font-mono">
              <span className="text-slate-400 block text-[10px]">RELATIVE HUMIDITY</span>
              <span className="text-lg font-bold text-cyan-300">{weather?.relative_humidity_pct ?? 65}%</span>
              <span className="text-slate-500 block text-[9px] mt-0.5">Ambient vapor pressure</span>
            </div>

            <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800 font-mono">
              <span className="text-slate-400 block text-[10px]">ACTIVE ANALYSIS SECTORS</span>
              <span className="text-lg font-bold text-amber-400">{zones.length} Sectors</span>
              <span className="text-slate-500 block text-[9px] mt-0.5">Synchronized with interactive twin</span>
            </div>
          </div>

          <div className="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-300">
              <span className="font-bold">Current Baseline Risk Distribution by Sector</span>
              <span className="text-[10px] font-mono text-slate-400">Formula: R = 0.35H + 0.30E + 0.35V - Adaptive</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-5 gap-2 pt-1 font-mono text-xs">
              {zones.map(z => (
                <div
                  key={z.id}
                  onClick={() => onSelectZone(z.id)}
                  className={`p-2 rounded border cursor-pointer transition ${
                    activeZoneId === z.id
                      ? 'bg-rose-950/40 border-rose-500 text-white'
                      : 'bg-slate-900 border-slate-800 hover:border-slate-700 text-slate-300'
                  }`}
                >
                  <div className="text-[10px] text-slate-400 truncate">{z.short_name || z.name}</div>
                  <div className="text-base font-bold text-rose-400 mt-1">{z.baseline_risk}</div>
                  <div className="text-[9px] text-slate-500">Risk Score / 100</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          MODE 3: FUTURE (7-14 DAY NUMERICAL WEATHER FORECAST)
      ========================================================================= */}
      {temporalMode === 'future' && (
        <div className="space-y-3.5">
          {/* Horizon Selector */}
          <div className="flex flex-wrap items-center justify-between gap-2.5 bg-slate-950/70 p-2.5 rounded-lg border border-slate-800 text-xs">
            <div className="flex items-center gap-2">
              <span className="text-slate-400 font-semibold">Forecast Horizon:</span>
              {[
                { days: 3, label: 'Next 3 Days' },
                { days: 7, label: '7-Day Outlook' },
                { days: 14, label: '14-Day Medium Range' }
              ].map(h => (
                <button
                  key={h.days}
                  onClick={() => setForecastDays(h.days)}
                  className={`px-2.5 py-1 rounded transition text-xs ${
                    forecastDays === h.days
                      ? 'bg-rose-600 text-white font-bold'
                      : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  {h.label}
                </button>
              ))}
            </div>

            <span className="text-[10px] font-mono text-slate-400">
              Model: ECMWF IFS / GFS Seamless
            </span>
          </div>

          {foreLoading && (
            <div className="py-12 text-center text-slate-400 text-xs flex flex-col items-center justify-center gap-2">
              <div className="w-6 h-6 border-2 border-rose-500 border-t-transparent rounded-full animate-spin"></div>
              <span>Querying Open-Meteo Numerical Prediction Engine for {city.name}...</span>
            </div>
          )}

          {foreData && !foreLoading && (
            <div className="space-y-3.5">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800 font-mono">
                  <span className="text-slate-400 block text-[10px]">FORECAST PEAK TEMP</span>
                  <span className="text-base font-bold text-rose-400">{foreData.peak_temperature_c}°C</span>
                  <span className="text-slate-500 block text-[9px] mt-0.5">Projected maximum</span>
                </div>

                <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800 font-mono">
                  <span className="text-slate-400 block text-[10px]">PROJECTED PEAK RISK</span>
                  <span className="text-base font-bold text-amber-400">{foreData.peak_risk_score} / 100</span>
                  <span className="text-slate-500 block text-[9px] mt-0.5">Escalation date: {foreData.peak_risk_date}</span>
                </div>

                <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800 font-mono">
                  <span className="text-slate-400 block text-[10px]">FORECAST WINDOW</span>
                  <span className="text-base font-bold text-cyan-300">{foreData.forecast_horizon_days} Days Ahead</span>
                  <span className="text-slate-500 block text-[9px] mt-0.5">{foreData.start_date} to {foreData.end_date}</span>
                </div>

                <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800 font-mono">
                  <span className="text-slate-400 block text-[10px]">NUMERICAL PREDICTION</span>
                  <span className="text-xs font-bold text-emerald-400">Atmospheric Physics</span>
                  <span className="text-slate-500 block text-[9px] mt-0.5">Distinct from policy simulations</span>
                </div>
              </div>

              {/* Forecast Progression Chart */}
              <div className="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 space-y-2">
                <div className="flex items-center justify-between text-xs text-slate-300">
                  <span className="font-bold flex items-center gap-1.5">
                    <TrendingUp className="w-3.5 h-3.5 text-rose-400" />
                    <span>Projected Daily Heat-Risk Trend (Next {forecastDays} Days)</span>
                  </span>
                  <span className="text-[10px] font-mono text-slate-400">Weather Forecast Model</span>
                </div>

                <div className="h-56 w-full pt-2">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={foreData.daily_timeline}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.4} />
                      <XAxis dataKey="date" stroke="#94a3b8" fontSize={10} tickLine={false} />
                      <YAxis stroke="#94a3b8" fontSize={10} domain={[10, 100]} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }}
                      />
                      <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '4px' }} />
                      <Line type="monotone" dataKey="average_city_risk" name="Projected Avg Risk" stroke="#ffffff" strokeWidth={2.5} dot={{ r: 3 }} />
                      {zones.map((z, idx) => {
                        const colors = ['#f43f5e', '#f97316', '#e11d48', '#06b6d4', '#8b5cf6'];
                        return (
                          <Line
                            key={z.id}
                            type="monotone"
                            dataKey={`zone_risks.${z.id}`}
                            name={z.short_name || z.name}
                            stroke={colors[idx % colors.length]}
                            strokeWidth={1.5}
                            dot={false}
                          />
                        );
                      })}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* 24-Hour Diurnal Curve */}
              {foreData.hourly_diurnal_24h && foreData.hourly_diurnal_24h.length > 0 && (
                <div className="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between text-xs text-slate-300">
                    <span className="font-bold">24-Hour Diurnal Thermal Cycle & Hourly Risk Curve</span>
                    <span className="text-[10px] font-mono text-slate-400">Hourly resolution</span>
                  </div>
                  <div className="h-40 w-full pt-1">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={foreData.hourly_diurnal_24h}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
                        <XAxis 
                          dataKey="time" 
                          stroke="#94a3b8" 
                          fontSize={9} 
                          tickFormatter={(t) => t.split('T')[1] || t} 
                        />
                        <YAxis stroke="#94a3b8" fontSize={10} />
                        <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '10px' }} />
                        <Line type="monotone" dataKey="air_temp_c" name="Air Temp (°C)" stroke="#fbbf24" strokeWidth={2} dot={false} />
                        <Line type="monotone" dataKey="apparent_temp_c" name="Heat Index (°C)" stroke="#f43f5e" strokeWidth={2} dot={false} />
                        <Line type="monotone" dataKey="composite_risk" name="Risk Score (/100)" stroke="#38bdf8" strokeWidth={2} dot={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* =========================================================================
          MODE 4: CLIMATE PROJECTIONS THROUGH 2050 (CMIP6 HIGHRESMIP)
      ========================================================================= */}
      {temporalMode === 'climate' && (
        <div className="space-y-3.5">
          {/* Model Selector */}
          <div className="flex flex-wrap items-center justify-between gap-2.5 bg-slate-950/70 p-2.5 rounded-lg border border-slate-800 text-xs">
            <div className="flex items-center gap-2">
              <span className="text-slate-400 font-semibold">CMIP6 Climate Model:</span>
              {[
                { id: 'EC_Earth3P_HR', label: 'EC-Earth3P-HR (High Resolution)' },
                { id: 'MRI_AGCM3_2_S', label: 'MRI-AGCM3-2-S (Atmospheric GCM)' },
                { id: 'MPI_ESM1_2_XR', label: 'MPI-ESM1-2-XR (Max Planck Earth System)' }
              ].map(m => (
                <button
                  key={m.id}
                  onClick={() => setClimateModel(m.id)}
                  className={`px-2.5 py-1 rounded transition text-xs ${
                    climateModel === m.id
                      ? 'bg-rose-600 text-white font-bold'
                      : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  {m.label}
                </button>
              ))}
            </div>

            <span className="text-[10px] font-mono text-cyan-300">
              Horizon: 2025 to 2050 Decadal Trajectory
            </span>
          </div>

          <div className="bg-amber-950/20 border border-amber-500/30 rounded-lg p-3 text-xs text-amber-300 flex items-start gap-2">
            <Info className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <div className="leading-relaxed text-[11px]">
              <strong>Scientific Protocol Notice:</strong> Climate projections reflect multi-decadal Earth System model simulations driven by greenhouse gas emission trajectories (SSP scenarios). These outputs are probabilistic thermal drifts, <em>not</em> day-to-day weather forecasts.
            </div>
          </div>

          {climateLoading && (
            <div className="py-12 text-center text-slate-400 text-xs flex flex-col items-center justify-center gap-2">
              <div className="w-6 h-6 border-2 border-rose-500 border-t-transparent rounded-full animate-spin"></div>
              <span>Querying Open-Meteo Climate API (CMIP6 Multi-Model Projections)...</span>
            </div>
          )}

          {climateData && !climateLoading && (
            <div className="space-y-3.5">
              {/* Decadal Progression Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                {climateData.decadal_projections.map(dec => (
                  <div key={dec.year} className="bg-slate-950/80 p-3 rounded-lg border border-slate-800 font-mono space-y-1">
                    <div className="flex items-center justify-between text-slate-400 text-[10px]">
                      <span>YEAR {dec.year}</span>
                      <span className="text-cyan-400">{dec.sample_period}</span>
                    </div>
                    <div className="text-base font-bold text-rose-400">
                      {dec.projected_mean_summer_max_c}°C
                      <span className="text-[10px] font-normal text-slate-400 ml-1">avg summer max</span>
                    </div>
                    <div className="text-xs text-amber-400">
                      Projected Risk: <strong>{dec.projected_city_average_risk}</strong> / 100
                    </div>
                  </div>
                ))}
              </div>

              {/* Climate Progression Chart */}
              <div className="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 space-y-2">
                <div className="flex items-center justify-between text-xs text-slate-300">
                  <span className="font-bold">Projected Summer Peak Temperatures & City Average Risk to 2050</span>
                  <span className="text-[10px] font-mono text-slate-400">Model: {climateModel}</span>
                </div>

                <div className="h-56 w-full pt-2">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={climateData.decadal_projections}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.4} />
                      <XAxis dataKey="year" stroke="#94a3b8" fontSize={11} />
                      <YAxis stroke="#94a3b8" fontSize={11} domain={[20, 100]} />
                      <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '11px' }} />
                      <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '4px' }} />
                      <Bar dataKey="projected_mean_summer_max_c" name="Summer Mean Max (°C)" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="projected_city_average_risk" name="Projected Risk Score (/100)" fill="#f43f5e" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* =========================================================================
          MODE 5: MULTI-HORIZON COMPARATIVE TIMELINE
      ========================================================================= */}
      {temporalMode === 'compare' && (
        <div className="space-y-3.5">
          {compareLoading && (
            <div className="py-12 text-center text-slate-400 text-xs flex flex-col items-center justify-center gap-2">
              <div className="w-6 h-6 border-2 border-rose-500 border-t-transparent rounded-full animate-spin"></div>
              <span>Synthesizing multi-horizon comparison across Past, Present, Future, and 2050...</span>
            </div>
          )}

          {compareData && !compareLoading && (
            <div className="space-y-3.5">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                {/* Past Card */}
                <div className="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between text-xs border-b border-slate-800 pb-1.5">
                    <span className="font-bold text-amber-400 flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5" /> 1. PAST REANALYSIS
                    </span>
                    <span className="text-[9px] font-mono text-slate-500">ERA5</span>
                  </div>
                  <div className="space-y-1 font-mono text-xs">
                    <div className="text-slate-400 text-[11px]">{compareData.past_heatwave.period}</div>
                    <div className="text-lg font-bold text-white mt-1">
                      {compareData.past_heatwave.peak_air_temp_c}°C
                    </div>
                    <div className="text-xs text-amber-400">
                      Risk Score: <strong>{compareData.past_heatwave.city_risk_score}</strong>
                    </div>
                  </div>
                  <p className="text-[10px] text-slate-500 pt-1 border-t border-slate-900">
                    Baseline historical heatwave anchor.
                  </p>
                </div>

                {/* Present Card */}
                <div className="bg-slate-950/80 p-3.5 rounded-xl border border-emerald-500/40 space-y-2">
                  <div className="flex items-center justify-between text-xs border-b border-slate-800 pb-1.5">
                    <span className="font-bold text-emerald-400 flex items-center gap-1">
                      <Activity className="w-3.5 h-3.5" /> 2. PRESENT LIVE
                    </span>
                    <span className="text-[9px] font-mono text-emerald-400">ACTIVE</span>
                  </div>
                  <div className="space-y-1 font-mono text-xs">
                    <div className="text-slate-400 text-[11px]">{compareData.present_live.timestamp}</div>
                    <div className="text-lg font-bold text-white mt-1">
                      {compareData.present_live.current_air_temp_c}°C
                    </div>
                    <div className="text-xs text-emerald-400">
                      Risk Score: <strong>{compareData.present_live.city_risk_score}</strong>
                    </div>
                  </div>
                  <p className="text-[10px] text-slate-500 pt-1 border-t border-slate-900">
                    Live operational meteorological readings right now.
                  </p>
                </div>

                {/* Future Card */}
                <div className="bg-slate-950/80 p-3.5 rounded-xl border border-rose-500/40 space-y-2">
                  <div className="flex items-center justify-between text-xs border-b border-slate-800 pb-1.5">
                    <span className="font-bold text-rose-400 flex items-center gap-1">
                      <TrendingUp className="w-3.5 h-3.5" /> 3. FUTURE 7-DAY
                    </span>
                    <span className="text-[9px] font-mono text-rose-400">ECMWF</span>
                  </div>
                  <div className="space-y-1 font-mono text-xs">
                    <div className="text-slate-400 text-[11px]">Peak date: {compareData.future_forecast.peak_date}</div>
                    <div className="text-lg font-bold text-white mt-1">
                      {compareData.future_forecast.peak_air_temp_c}°C
                    </div>
                    <div className="text-xs text-rose-400">
                      Peak Risk: <strong>{compareData.future_forecast.peak_risk_score}</strong>
                    </div>
                  </div>
                  <p className="text-[10px] text-slate-500 pt-1 border-t border-slate-900">
                    Numerical weather prediction horizon.
                  </p>
                </div>

                {/* Climate 2050 Card */}
                <div className="bg-slate-950/80 p-3.5 rounded-xl border border-purple-500/40 space-y-2">
                  <div className="flex items-center justify-between text-xs border-b border-slate-800 pb-1.5">
                    <span className="font-bold text-purple-400 flex items-center gap-1">
                      <Sun className="w-3.5 h-3.5" /> 4. CLIMATE 2050
                    </span>
                    <span className="text-[9px] font-mono text-purple-400">CMIP6</span>
                  </div>
                  <div className="space-y-1 font-mono text-xs">
                    <div className="text-slate-400 text-[11px]">{compareData.climate_2050.scenario}</div>
                    <div className="text-lg font-bold text-white mt-1">
                      {compareData.climate_2050.projected_summer_max_c}°C
                    </div>
                    <div className="text-xs text-purple-400">
                      Projected Risk: <strong>{compareData.climate_2050.projected_city_risk}</strong>
                    </div>
                  </div>
                  <p className="text-[10px] text-slate-500 pt-1 border-t border-slate-900">
                    Multi-decadal climate model projection.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

