import React, { useState, useEffect } from 'react';
import { 
  Cpu, 
  DollarSign, 
  Scale, 
  Sparkles, 
  ArrowRight, 
  Target, 
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { optimizeBudget } from '../api';

export default function BudgetOptimizer({
  city,
  zones,
  currentBudget,
  onUpdateBudget,
  onApplyPlanToSimulator,
  onSelectZone
}) {
  const sym = city?.currency?.symbol || '$';
  const currCode = city?.currency?.code || 'USD';
  const rate = city?.currency?.rate_per_usd || 1.0;
  const defaultBudget = city?.currency?.default_budget || 3500000;

  const [budgetSlider, setBudgetSlider] = useState(currentBudget || defaultBudget);
  const [equityWeighting, setEquityWeighting] = useState(true);
  const [focusObjective, setFocusObjective] = useState('balanced');
  const [loading, setLoading] = useState(false);
  const [optimizationResult, setOptimizationResult] = useState(null);
  const [error, setError] = useState(null);

  // Sync budget if city changes
  useEffect(() => {
    if (city?.currency?.default_budget) {
      setBudgetSlider(city.currency.default_budget);
      setOptimizationResult(null); // Clear previous city result so new city data is pure
    }
  }, [city?.name]);

  const handleRunOptimization = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await optimizeBudget({
        budgetLocal: budgetSlider,
        equityWeighting,
        focusObjective,
        cityContext: city,
        zones: zones || []
      });
      setOptimizationResult(res);
      onUpdateBudget(budgetSlider);
    } catch (err) {
      setError(err.message || 'Optimization failed');
    } finally {
      setLoading(false);
    }
  };

  // Determine reasonable slider range based on currency
  const getSliderMinMax = () => {
    if (currCode === 'INR') {
      return { min: 2000000, max: 100000000, step: 2000000 }; // 20 Lakh to 10 Crore
    }
    if (currCode === 'JPY') {
      return { min: 50000000, max: 2000000000, step: 50000000 }; // 50M to 2B JPY
    }
    if (currCode === 'AED') {
      return { min: 1000000, max: 40000000, step: 1000000 };
    }
    if (currCode === 'GBP' || currCode === 'EUR') {
      return { min: 300000, max: 15000000, step: 250000 };
    }
    return { min: 500000, max: 20000000, step: 250000 }; // USD default
  };

  const { min: sliderMin, max: sliderMax, step: sliderStep } = getSliderMinMax();

  const formatCurrency = (val) => {
    if (!val && val !== 0) return '0';
    if (sym === '₹') {
      if (val >= 10000000) return `${(val / 10000000).toFixed(2)} Cr`;
      if (val >= 100000) return `${(val / 100000).toFixed(1)} Lakh`;
      return `${(val / 1000).toFixed(0)}k`;
    }
    if (sym === '¥') {
      if (val >= 100000000) return `${(val / 100000000).toFixed(1)} 億`;
      return `${(val / 1000000).toFixed(0)}M`;
    }
    if (val >= 1000000) return `${(val / 1000000).toFixed(2)}M`;
    return `${(val / 1000).toFixed(0)}k`;
  };

  return (
    <div className="glass-panel rounded-xl p-4 flex flex-col gap-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <span>AI Budget Optimizer & Policy Strategic Allocator</span>
            <span className="text-[10px] text-slate-400 font-mono bg-slate-800 px-2 py-0.5 rounded">
              {city?.name || 'City'} • {currCode}
            </span>
          </h3>
          <p className="text-xs text-slate-400">
            Currency-aware multi-criteria optimization maximizing life safety and heat risk reduction per {sym} invested.
          </p>
        </div>

        <button
          onClick={handleRunOptimization}
          disabled={loading}
          className="px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-500/20 transition flex items-center gap-2 disabled:opacity-50"
        >
          {loading ? (
            <span className="flex items-center gap-1.5">
              <span className="w-3.5 h-3.5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></span>
              Optimizing Portfolio...
            </span>
          ) : (
            <>
              <Sparkles className="w-3.5 h-3.5" />
              <span>Compute Optimal Portfolio</span>
            </>
          )}
        </button>
      </div>

      {/* Control Levers Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 bg-slate-900/60 p-3 rounded-lg border border-slate-800">
        {/* Budget Slider */}
        <div className="space-y-1">
          <div className="flex justify-between items-baseline text-xs">
            <span className="text-slate-400 font-medium">Budget Cap ({currCode}):</span>
            <span className="font-bold font-mono text-emerald-400 text-sm">
              {sym}{formatCurrency(budgetSlider)}
            </span>
          </div>
          <input
            type="range"
            min={sliderMin}
            max={sliderMax}
            step={sliderStep}
            value={budgetSlider}
            onChange={(e) => setBudgetSlider(Number(e.target.value))}
            className="w-full accent-emerald-500 cursor-pointer h-1.5 bg-slate-800 rounded"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono">
            <span>{sym}{formatCurrency(sliderMin)}</span>
            <span>{sym}{formatCurrency((sliderMin + sliderMax) / 2)}</span>
            <span>{sym}{formatCurrency(sliderMax)}</span>
          </div>
        </div>

        {/* Equity Weighting Toggle */}
        <div className="flex flex-col justify-center space-y-1">
          <div className="text-xs text-slate-400 font-medium flex items-center gap-1">
            <Scale className="w-3.5 h-3.5 text-indigo-400" />
            <span>Social Equity & SVI Weighting</span>
          </div>
          <label className="flex items-center gap-2 cursor-pointer mt-1">
            <input
              type="checkbox"
              checked={equityWeighting}
              onChange={(e) => setEquityWeighting(e.target.checked)}
              className="accent-indigo-500 w-4 h-4 rounded cursor-pointer"
            />
            <span className="text-xs text-slate-300">
              Boost allocations to high-SVI senior/low-AC neighborhoods
            </span>
          </label>
        </div>

        {/* Objective Strategy */}
        <div className="space-y-1">
          <div className="text-xs text-slate-400 font-medium flex items-center gap-1">
            <Target className="w-3.5 h-3.5 text-amber-400" />
            <span>Strategic Optimization Focus</span>
          </div>
          <div className="grid grid-cols-3 gap-1 pt-0.5">
            {[
              { id: 'balanced', label: 'Balanced' },
              { id: 'max_people', label: 'Max People' },
              { id: 'max_cooling', label: 'Max LST Drop' }
            ].map(opt => (
              <button
                key={opt.id}
                onClick={() => setFocusObjective(opt.id)}
                className={`text-[11px] py-1 rounded border text-center transition ${
                  focusObjective === opt.id
                    ? 'bg-amber-500/20 border-amber-500 text-amber-300 font-semibold'
                    : 'bg-slate-800/80 border-slate-700 text-slate-400 hover:text-slate-200'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {error && (
        <div className="text-xs text-rose-400 bg-rose-950/30 p-2.5 rounded border border-rose-500/30">
          {error}
        </div>
      )}

      {/* Results View */}
      {optimizationResult && (
        <div className="space-y-4 pt-1">
          {/* Summary Strip */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
            <div className="bg-slate-900/90 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase font-bold">Budget Utilized</span>
              <div className="text-base font-bold font-mono text-emerald-400">
                {sym}{formatCurrency(optimizationResult.budget_utilized_local)}
              </div>
              <div className="text-[10px] text-slate-400 font-mono">
                {sym}{formatCurrency(optimizationResult.budget_remaining_local)} reserve
              </div>
            </div>

            <div className="bg-slate-900/90 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase font-bold">People Protected</span>
              <div className="text-base font-bold font-mono text-cyan-400">
                ~{optimizationResult.total_people_protected.toLocaleString()}
              </div>
              <div className="text-[10px] text-slate-400">
                Across {city?.name || 'city'} zones
              </div>
            </div>

            <div className="bg-slate-900/90 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-500 uppercase font-bold">City-Wide Risk</span>
              <div className="text-base font-bold font-mono text-rose-400 flex items-center gap-1">
                <span>{optimizationResult.city_average_risk_before}</span>
                <ArrowRight className="w-3 h-3 text-slate-500" />
                <span className="text-emerald-400">{optimizationResult.city_average_risk_after}</span>
              </div>
              <div className="text-[10px] text-emerald-400 font-mono">
                -{optimizationResult.risk_reduction_pct}% reduction
              </div>
            </div>

            <div className="bg-slate-900/90 p-2.5 rounded-lg border border-slate-800 flex flex-col justify-between">
              <span className="text-[10px] text-slate-500 uppercase font-bold">Sync to Twin</span>
              <button
                onClick={() => onApplyPlanToSimulator(optimizationResult)}
                className="text-xs px-2.5 py-1 rounded bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold flex items-center justify-center gap-1 transition"
              >
                <span>Push Plan to Map</span>
              </button>
              <span className="text-[9px] text-slate-500 text-center">Syncs to active simulator</span>
            </div>
          </div>

          {/* Explainable Prioritization Rationale */}
          <div className="bg-slate-900/90 rounded-lg p-3.5 border border-slate-800 space-y-2">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-300">
              <Sparkles className="w-4 h-4 text-amber-400" />
              <span>Prioritization Rationale: Why Each Zone & Intervention Was Chosen</span>
            </div>
            <div className="space-y-1.5">
              {optimizationResult.prioritization_rationale.map((r, i) => (
                <div key={i} className="text-xs text-slate-300 bg-slate-950/60 p-2 rounded border border-slate-800/80 flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mt-1.5 shrink-0"></span>
                  <span>{r}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Zone Allocation Breakdown Cards */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              Allocated Resilience Portfolio for {city?.name || 'City'}
            </h4>
            <div className="space-y-2">
              {optimizationResult.zone_summaries.map(zs => {
                const zoneAllocations = optimizationResult.allocations_by_zone[zs.zone_id] || [];

                return (
                  <div
                    key={zs.zone_id}
                    className="bg-slate-900/60 rounded-lg p-3 border border-slate-800 hover:border-slate-700 transition"
                  >
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-white">{zs.zone_name}</span>
                        <span className="text-[10px] text-slate-400 font-mono">
                          Allocated: {sym}{formatCurrency(zs.cost_allocated_local)}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 text-xs font-mono">
                        <span className="text-slate-400">
                          Risk: {zs.baseline_risk} &rarr; <span className="text-emerald-400 font-bold">{zs.simulated_risk}</span>
                        </span>
                        <span className="text-cyan-400">
                          ~{zs.people_protected.toLocaleString()} sheltered
                        </span>
                      </div>
                    </div>

                    {zoneAllocations.length === 0 ? (
                      <div className="text-[11px] text-slate-500 italic pl-2">
                        No capital allocated (baseline resilience or lower benefit/cost priority).
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-1">
                        {zoneAllocations.map((alloc, idx) => (
                          <div key={idx} className="bg-slate-950/60 rounded p-2 text-xs border border-slate-800/80">
                            <div className="flex justify-between items-baseline font-medium text-slate-200">
                              <span>{alloc.intervention_name}</span>
                              <span className="font-mono text-emerald-400">{sym}{formatCurrency(alloc.cost_local)}</span>
                            </div>
                            <div className="text-[11px] text-slate-400 mt-0.5">
                              Quantity: <span className="font-mono text-slate-300">{alloc.intensity} {alloc.unit}</span>
                            </div>
                            <div className="text-[10px] text-slate-400 mt-1 italic border-t border-slate-800/80 pt-1">
                              {alloc.why_prioritized}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
