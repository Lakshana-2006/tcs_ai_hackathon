import React, { useState, useMemo } from 'react';
import { 
  Sliders, 
  Sparkles, 
  RotateCcw, 
  DollarSign, 
  Users, 
  Thermometer, 
  ShieldCheck, 
  AlertTriangle,
  Info,
  TrendingDown,
  Layers,
  CheckCircle,
  Plus,
  Minus
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip as RechartsTooltip, 
  ResponsiveContainer, 
  Legend,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';
import { simulateZoneLocally, DEFAULT_INTERVENTIONS_CATALOG } from '../utils/simulationEngine';

export default function InterventionSimulator({
  zone,
  city,
  interventionsCatalog,
  selectedInterventions = {},
  onChangeIntervention,
  onResetInterventions,
  simulationResult,
  loadingSim
}) {
  const [chartView, setChartView] = useState('radar'); // 'radar' or 'bar'

  // Resolve active catalog
  const catalog = useMemo(() => {
    return (interventionsCatalog && interventionsCatalog.length > 0)
      ? interventionsCatalog
      : DEFAULT_INTERVENTIONS_CATALOG;
  }, [interventionsCatalog]);

  // Selected intervention id for dedicated dynamic slider focus
  const [selectedInterventionId, setSelectedInterventionId] = useState(() => {
    return catalog[0]?.id || 'tree_planting';
  });

  // Keep selectedInterventionId valid if catalog changes
  const activeIntervention = useMemo(() => {
    const found = catalog.find(item => item.id === selectedInterventionId);
    return found || catalog[0] || DEFAULT_INTERVENTIONS_CATALOG[0];
  }, [catalog, selectedInterventionId]);

  if (!zone) {
    return (
      <div className="glass-panel rounded-xl p-6 text-center text-slate-500">
        Please select a zone above to simulate climate interventions.
      </div>
    );
  }

  const sym = city?.currency?.symbol || '$';
  const rate = city?.currency?.rate_per_usd || 1.0;

  // Format currency helper
  const formatCost = (valUsd) => {
    const valLocal = valUsd * rate;
    if (sym === '₹') {
      if (valLocal >= 10000000) return `${(valLocal / 10000000).toFixed(2)} Cr`;
      if (valLocal >= 100000) return `${(valLocal / 100000).toFixed(1)} Lakh`;
      return `${(valLocal / 1000).toFixed(0)}k`;
    }
    if (sym === '¥') {
      if (valLocal >= 100000000) return `${(valLocal / 100000000).toFixed(1)} 億`;
      return `${(valLocal / 1000000).toFixed(1)}M`;
    }
    if (valLocal >= 1000000) return `${(valLocal / 1000000).toFixed(2)}M`;
    return `${(valLocal / 1000).toFixed(0)}k`;
  };

  // Immediate local simulation result fallback ensures zero latency / glitch on drag
  const effectiveResult = useMemo(() => {
    if (simulationResult) return simulationResult;
    return simulateZoneLocally(zone, selectedInterventions, catalog, city);
  }, [simulationResult, zone, selectedInterventions, catalog, city]);

  const handleApplyPreset = (presetName) => {
    if (presetName === 'cooling_haven') {
      onChangeIntervention('cooling_centers', 6);
      onChangeIntervention('tree_planting', 20);
      onChangeIntervention('cool_roofs', 35);
    } else if (presetName === 'green_canopy') {
      onChangeIntervention('tree_planting', 40);
      onChangeIntervention('green_corridors', 8);
      onChangeIntervention('permeable_pavements', 30);
    } else if (presetName === 'rapid_shield') {
      onChangeIntervention('cooling_centers', 8);
      onChangeIntervention('cool_roofs', 45);
      onChangeIntervention('green_corridors', 5);
    }
  };

  // Active intervention parameters
  const activeMin = activeIntervention?.min_intensity !== undefined ? activeIntervention.min_intensity : 0;
  const activeMax = activeIntervention?.max_intensity !== undefined ? activeIntervention.max_intensity : 100;
  const isCoolingCenterActive = activeIntervention?.id === 'cooling_centers';
  const activeStep = activeIntervention?.step !== undefined 
    ? activeIntervention.step 
    : (isCoolingCenterActive ? 1 : 0.5);
  const activeValue = selectedInterventions[activeIntervention?.id] !== undefined
    ? Number(selectedInterventions[activeIntervention.id])
    : 0;

  const handleSliderChange = (itemId, rawVal) => {
    const num = parseFloat(rawVal);
    const valid = isNaN(num) ? 0 : Math.max(0, num);
    onChangeIntervention(itemId, valid);
  };

  const handleStepAdjust = (delta) => {
    if (!activeIntervention) return;
    const current = activeValue;
    const next = Math.max(activeMin, Math.min(activeMax, current + delta));
    const rounded = Math.round(next * 10) / 10;
    onChangeIntervention(activeIntervention.id, rounded);
  };

  const chartData = [
    {
      factor: 'Hazard (LST)',
      Baseline: effectiveResult ? effectiveResult.baseline.hazard_score : (zone.baseline_hazard?.hazard_score || 50),
      Simulated: effectiveResult ? effectiveResult.simulated.hazard_score : (zone.baseline_hazard?.hazard_score || 50),
      fullMark: 100
    },
    {
      factor: 'Exposure',
      Baseline: effectiveResult ? effectiveResult.baseline.exposure_score : (zone.baseline_exposure?.exposure_score || 50),
      Simulated: effectiveResult ? effectiveResult.simulated.exposure_score : (zone.baseline_exposure?.exposure_score || 50),
      fullMark: 100
    },
    {
      factor: 'Vulnerability',
      Baseline: effectiveResult ? effectiveResult.baseline.vulnerability_score : (zone.baseline_vulnerability?.vulnerability_score || 50),
      Simulated: effectiveResult ? effectiveResult.simulated.vulnerability_score : (zone.baseline_vulnerability?.vulnerability_score || 50),
      fullMark: 100
    },
    {
      factor: 'Composite Risk',
      Baseline: effectiveResult ? effectiveResult.baseline.composite_risk : (zone.baseline_risk || 50),
      Simulated: effectiveResult ? effectiveResult.simulated.composite_risk : (zone.baseline_risk || 50),
      fullMark: 100
    }
  ];

  const hasInterventions = Object.values(selectedInterventions).some(v => v > 0);

  return (
    <div className="glass-panel rounded-xl p-4 flex flex-col gap-4">
      {/* Title & Presets */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Sliders className="w-4 h-4 text-emerald-400" />
            <span>What-If Intervention Simulator</span>
            <span className="text-[10px] text-slate-400 font-mono bg-slate-800 px-2 py-0.5 rounded">
              {zone.name}
            </span>
          </h3>
          <p className="text-xs text-slate-400">
            Model real-time cooling, human exposure shielding, and uncertainty bounds in {city?.currency?.code || 'local currency'}.
          </p>
        </div>

        {/* Quick Presets */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-[11px] text-slate-500 font-medium mr-1">Presets:</span>
          <button
            type="button"
            onClick={() => handleApplyPreset('cooling_haven')}
            className="text-[11px] px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
          >
            Cooling Haven
          </button>
          <button
            type="button"
            onClick={() => handleApplyPreset('green_canopy')}
            className="text-[11px] px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
          >
            Green Canopy
          </button>
          <button
            type="button"
            onClick={() => handleApplyPreset('rapid_shield')}
            className="text-[11px] px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
          >
            Rapid Shield
          </button>
          {hasInterventions && (
            <button
              type="button"
              onClick={onResetInterventions}
              className="text-[11px] px-2 py-1 rounded bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 transition flex items-center gap-1"
            >
              <RotateCcw className="w-3 h-3" /> Clear
            </button>
          )}
        </div>
      </div>

      {/* Main Grid: Controls Left (7 cols), Outcomes Right (5 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* Controls Column */}
        <div className="lg:col-span-7 space-y-4">
          
          {/* 1. Dynamic Intervention Selector Pills */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-emerald-400" />
                <span>Select Intervention to Control:</span>
              </span>
              <span className="text-[10px] text-slate-400">
                Click any pill or card below to adjust its range
              </span>
            </div>
            
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5">
              {catalog.map(item => {
                const isSelected = item.id === selectedInterventionId;
                const val = selectedInterventions[item.id] || 0;
                
                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setSelectedInterventionId(item.id)}
                    className={`text-left p-2 rounded-lg border text-xs transition flex flex-col justify-between ${
                      isSelected 
                        ? 'border-emerald-500 bg-emerald-950/30 shadow-sm shadow-emerald-950 text-white' 
                        : 'border-slate-800 bg-slate-900/60 hover:bg-slate-800/80 text-slate-300'
                    }`}
                  >
                    <div className="flex items-center justify-between w-full">
                      <span className="font-medium truncate mr-1">{item.name.split('&')[0].trim()}</span>
                      {isSelected && (
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0"></span>
                      )}
                    </div>
                    <div className="flex items-center justify-between text-[10px] mt-1 text-slate-400 font-mono">
                      <span>Max: {item.max_intensity}</span>
                      <span className={val > 0 ? 'text-emerald-400 font-bold' : 'text-slate-500'}>
                        {val % 1 === 0 ? val : val.toFixed(1)} {item.unit.split(' ')[0]}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* 2. Focused Dynamic Intensity Slider for Selected Intervention */}
          {activeIntervention && (
            <div className="bg-slate-900/90 rounded-xl p-3.5 border-2 border-emerald-500/50 shadow-lg shadow-emerald-950/20 space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-2.5">
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-bold text-white">
                      {activeIntervention.name}
                    </span>
                    <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                      {activeIntervention.category}
                    </span>
                    {isCoolingCenterActive ? (
                      <span className="text-[9px] font-bold px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                        Human Exposure Sanctuary
                      </span>
                    ) : (
                      <span className="text-[9px] font-medium px-1.5 py-0.2 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                        LST Mitigator
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">
                    {activeIntervention.description}
                  </p>
                </div>

                <div className="text-left sm:text-right shrink-0 bg-slate-950/60 sm:bg-transparent p-2 sm:p-0 rounded border border-slate-800/80 sm:border-0">
                  <div className="text-sm font-mono font-bold text-emerald-400">
                    {activeValue % 1 === 0 ? activeValue : activeValue.toFixed(1)} {activeIntervention.unit}
                  </div>
                  <div className="text-[11px] text-slate-400 font-mono">
                    Est. Cost: <span className="text-slate-200">~{sym}{formatCost(activeValue * activeIntervention.cost_per_unit_usd)}</span>
                  </div>
                </div>
              </div>

              {/* Slider Controller with Continuous Movement & Range Sync */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs font-medium text-slate-400">
                  <span className="flex items-center gap-1 text-[11px]">
                    Intensity Level:
                    <span className="font-mono text-emerald-400 font-bold">
                      {activeValue % 1 === 0 ? activeValue : activeValue.toFixed(1)} / {activeMax} {activeIntervention.unit}
                    </span>
                  </span>
                  
                  {/* Step Adjustment Buttons */}
                  <div className="flex items-center gap-1">
                    <button
                      type="button"
                      onClick={() => handleStepAdjust(-activeStep)}
                      disabled={activeValue <= activeMin}
                      className="p-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300 border border-slate-700 transition"
                      title="Decrease intensity"
                    >
                      <Minus className="w-3 h-3" />
                    </button>
                    <button
                      type="button"
                      onClick={() => handleStepAdjust(activeStep)}
                      disabled={activeValue >= activeMax}
                      className="p-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300 border border-slate-700 transition"
                      title="Increase intensity"
                    >
                      <Plus className="w-3 h-3" />
                    </button>
                  </div>
                </div>

                {/* Continuous Slider Track */}
                <div className="flex items-center gap-3">
                  <span className="text-[11px] text-slate-500 font-mono w-10 text-left shrink-0">
                    {activeMin}
                  </span>
                  <input
                    type="range"
                    min={activeMin}
                    max={activeMax}
                    step={activeStep}
                    value={activeValue}
                    onChange={(e) => handleSliderChange(activeIntervention.id, e.target.value)}
                    className="w-full accent-emerald-500 cursor-pointer h-2 bg-slate-800 rounded-lg appearance-none"
                    aria-label={`Adjust ${activeIntervention.name} intensity`}
                  />
                  <span className="text-[11px] text-slate-500 font-mono w-10 text-right shrink-0">
                    {activeMax}
                  </span>
                </div>

                <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono">
                  <span>Range: {activeMin} to {activeMax} {activeIntervention.unit}</span>
                  <span>Step: {activeStep}</span>
                </div>
              </div>

              {/* Explicit Biophysical Law Banner for Cooling Centers */}
              {isCoolingCenterActive && (
                <div className="text-[10px] bg-amber-950/30 border border-amber-500/30 rounded-lg p-2 text-amber-200/90 flex items-start gap-2">
                  <Info className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                  <span>
                    Crucial Biophysical Rule: Cooling centres directly reduce <strong>human exposure & vulnerability hours</strong> (preventing heat stroke); they do <strong>not</strong> claim to reduce outdoor land-surface temperature.
                  </span>
                </div>
              )}
            </div>
          )}

          {/* 3. All Intervention Levers Quick Overview */}
          <div className="space-y-2">
            <div className="text-xs font-semibold text-slate-400 flex items-center justify-between">
              <span>All Available Interventions ({catalog.length})</span>
              <span className="text-[10px] text-slate-500 font-normal">Adjust any slider directly or click to focus</span>
            </div>

            <div className="space-y-2">
              {catalog.map(item => {
                const val = selectedInterventions[item.id] !== undefined ? Number(selectedInterventions[item.id]) : 0;
                const isSelected = item.id === selectedInterventionId;
                const isCoolingCenter = item.id === 'cooling_centers';
                const itemMin = item.min_intensity !== undefined ? item.min_intensity : 0;
                const itemMax = item.max_intensity !== undefined ? item.max_intensity : 100;
                const itemStep = item.step !== undefined ? item.step : (isCoolingCenter ? 1 : 0.5);

                return (
                  <div 
                    key={item.id}
                    onClick={() => setSelectedInterventionId(item.id)}
                    className={`rounded-lg p-2.5 border transition cursor-pointer ${
                      isSelected
                        ? 'border-emerald-500/80 bg-slate-900/95 ring-1 ring-emerald-500/30'
                        : val > 0 
                          ? 'border-slate-700 bg-slate-900/80' 
                          : 'border-slate-800/80 bg-slate-950/60 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2 mb-1.5">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className={`text-xs font-semibold ${isSelected ? 'text-emerald-300' : 'text-slate-200'}`}>
                            {item.name}
                          </span>
                          {isSelected && (
                            <span className="text-[9px] font-bold px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                              Active Focus
                            </span>
                          )}
                        </div>
                        <p className="text-[10px] text-slate-400 line-clamp-1">{item.cooling_mechanism || item.description}</p>
                      </div>

                      <div className="text-right shrink-0">
                        <span className="text-xs font-bold font-mono text-emerald-400">
                          {val % 1 === 0 ? val : val.toFixed(1)} {item.unit}
                        </span>
                        <div className="text-[10px] text-slate-500 font-mono">
                          ~{sym}{formatCost(val * item.cost_per_unit_usd)}
                        </div>
                      </div>
                    </div>

                    {/* Interactive Slider on Row */}
                    <div 
                      className="flex items-center gap-3 pt-0.5" 
                      onClick={(e) => e.stopPropagation()}
                    >
                      <input
                        type="range"
                        min={itemMin}
                        max={itemMax}
                        step={itemStep}
                        value={val}
                        onChange={(e) => {
                          setSelectedInterventionId(item.id);
                          handleSliderChange(item.id, e.target.value);
                        }}
                        className="w-full accent-emerald-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg appearance-none"
                        aria-label={`${item.name} slider`}
                      />
                      <span className="text-[10px] text-slate-500 font-mono w-10 text-right shrink-0">
                        {itemMax}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="text-[10px] text-slate-500 italic pl-1">
            * Intervention costs are illustrative estimates in {city?.currency?.name || 'local currency'}; not official municipal tender bids.
          </div>
        </div>

        {/* Outcomes & Charts Column */}
        <div className="lg:col-span-5 flex flex-col gap-3">
          <div className="bg-slate-900/90 rounded-lg p-3.5 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between text-xs font-bold text-slate-300">
              <span className="flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-emerald-400" /> Projected Impact
              </span>
              <div className="flex items-center gap-1 text-[10px] font-normal">
                <button
                  type="button"
                  onClick={() => setChartView('radar')}
                  className={`px-2 py-0.5 rounded transition ${chartView === 'radar' ? 'bg-slate-700 text-white font-medium' : 'text-slate-400 hover:text-slate-200'}`}
                >
                  Radar
                </button>
                <button
                  type="button"
                  onClick={() => setChartView('bar')}
                  className={`px-2 py-0.5 rounded transition ${chartView === 'bar' ? 'bg-slate-700 text-white font-medium' : 'text-slate-400 hover:text-slate-200'}`}
                >
                  Bars
                </button>
              </div>
            </div>

            {/* Metrics 2x2 Grid */}
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="bg-slate-950/60 p-2.5 rounded border border-slate-800/80">
                <div className="text-[10px] text-slate-500 uppercase font-semibold">Risk Delta</div>
                <div className="text-base font-bold font-mono text-emerald-400 mt-0.5">
                  {effectiveResult ? `-${effectiveResult.risk_delta} pts` : '0.0 pts'}
                </div>
                <div className="text-[10px] text-slate-400">
                  {effectiveResult ? `${effectiveResult.risk_reduction_pct}% reduction` : 'No change'}
                </div>
              </div>

              <div className="bg-slate-950/60 p-2.5 rounded border border-slate-800/80">
                <div className="text-[10px] text-slate-500 uppercase font-semibold">Surface Cooling</div>
                <div className="text-base font-bold font-mono text-cyan-400 mt-0.5">
                  {effectiveResult ? `-${effectiveResult.lst_reduction_c}°C` : '0.0°C'}
                </div>
                <div className="text-[10px] text-slate-400">
                  LST anomaly drop
                </div>
              </div>

              <div className="bg-slate-950/60 p-2.5 rounded border border-slate-800/80">
                <div className="text-[10px] text-slate-500 uppercase font-semibold">People Protected</div>
                <div className="text-base font-bold font-mono text-amber-400 mt-0.5">
                  {effectiveResult ? effectiveResult.people_protected.toLocaleString() : '0'}
                </div>
                <div className="text-[10px] text-slate-400">
                  Heat stress sheltered
                </div>
              </div>

              <div className="bg-slate-950/60 p-2.5 rounded border border-slate-800/80">
                <div className="text-[10px] text-slate-500 uppercase font-semibold">Estimated Cost</div>
                <div className="text-base font-bold font-mono text-emerald-400 mt-0.5">
                  {sym}{effectiveResult ? formatCost(effectiveResult.estimated_cost_usd) : '0'}
                </div>
                <div className="text-[10px] text-slate-400 font-mono">
                  ({city?.currency?.code || 'USD'})
                </div>
              </div>
            </div>

            {/* Uncertainty Bounds Display (90% CI) */}
            {effectiveResult && effectiveResult.risk_delta > 0 && (
              <div className="bg-slate-950/70 p-2.5 rounded border border-slate-800 text-[11px]">
                <div className="flex items-center justify-between text-slate-400 mb-1">
                  <span className="font-semibold text-slate-300">Uncertainty ({effectiveResult.uncertainty?.confidence_level || '90% CI'})</span>
                </div>
                <div className="flex items-center justify-between font-mono text-xs">
                  <span className="text-slate-400">Low: -{effectiveResult.uncertainty?.low ?? 0} pts</span>
                  <span className="font-bold text-emerald-400">Expected: -{effectiveResult.uncertainty?.expected ?? 0} pts</span>
                  <span className="text-slate-400">High: -{effectiveResult.uncertainty?.high ?? 0} pts</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full mt-1.5 overflow-hidden flex">
                  <div className="bg-slate-600 h-full" style={{ width: '25%' }}></div>
                  <div className="bg-emerald-500 h-full" style={{ width: '50%' }}></div>
                  <div className="bg-slate-600 h-full" style={{ width: '25%' }}></div>
                </div>
              </div>
            )}

            {/* Recharts Visualization */}
            <div className="h-[200px] w-full pt-1">
              <ResponsiveContainer width="100%" height="100%">
                {chartView === 'radar' ? (
                  <RadarChart cx="50%" cy="50%" outerRadius="70%" data={chartData}>
                    <PolarGrid stroke="#334155" />
                    <PolarAngleAxis dataKey="factor" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 9 }} />
                    <Radar name="Baseline" dataKey="Baseline" stroke="#f43f5e" fill="#f43f5e" fillOpacity={0.35} />
                    <Radar name="Simulated" dataKey="Simulated" stroke="#10b981" fill="#10b981" fillOpacity={0.45} />
                    <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '4px' }} />
                  </RadarChart>
                ) : (
                  <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <XAxis dataKey="factor" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                    <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 10 }} />
                    <RechartsTooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '11px' }} />
                    <Legend wrapperStyle={{ fontSize: '11px' }} />
                    <Bar dataKey="Baseline" fill="#f43f5e" radius={[2, 2, 0, 0]} />
                    <Bar dataKey="Simulated" fill="#10b981" radius={[2, 2, 0, 0]} />
                  </BarChart>
                )}
              </ResponsiveContainer>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
