import React from 'react';
import { Flame, Users, ThermometerSun, DollarSign, TrendingDown, ShieldCheck } from 'lucide-react';

export default function KpiBar({ kpis, budget, currencySymbol = "$", onEditBudget, simulationResult }) {
  if (!kpis) return null;

  const hasSim = Boolean(simulationResult && simulationResult.risk_delta > 0);
  const sym = currencySymbol || kpis.currency_symbol || "$";

  // Format budget for local currency
  const formatBudget = (val) => {
    if (sym === '₹') {
      // In Crores / Lakhs
      if (val >= 10000000) return `${(val / 10000000).toFixed(2)} Cr`;
      return `${(val / 100000).toFixed(0)} Lakh`;
    }
    if (sym === '¥') {
      if (val >= 100000000) return `${(val / 100000000).toFixed(1)} 億`;
      return `${(val / 1000000).toFixed(0)}M`;
    }
    if (val >= 1000000) return `${(val / 1000000).toFixed(2)}M`;
    return `${(val / 1000).toFixed(0)}k`;
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3">
      {/* KPI 1: High Risk Zones */}
      <div className="glass-panel rounded-xl p-3.5 flex flex-col justify-between relative overflow-hidden group">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs font-medium uppercase tracking-wider">High-Risk Zones</span>
          <Flame className="w-4 h-4 text-rose-500" />
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold text-white tracking-tight">
            {kpis.high_risk_zones_count}
          </span>
          <span className="text-xs text-slate-400">of {kpis.total_zones} zones</span>
        </div>
        <div className="mt-2 text-[11px] text-rose-400/90 font-medium flex items-center gap-1">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-rose-500 animate-ping"></span>
          Risk score &gt; 65 threshold
        </div>
      </div>

      {/* KPI 2: Exposed Population */}
      <div className="glass-panel rounded-xl p-3.5 flex flex-col justify-between group">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs font-medium uppercase tracking-wider">Exposed Pop.</span>
          <Users className="w-4 h-4 text-amber-400" />
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold text-white tracking-tight">
            {kpis.exposed_population ? kpis.exposed_population.toLocaleString() : 'N/A'}
          </span>
        </div>
        <div className="mt-2 text-[11px] text-amber-300/80 font-medium">
          Residents in elevated risk areas
        </div>
      </div>

      {/* KPI 3: Peak Heat Anomaly */}
      <div className="glass-panel rounded-xl p-3.5 flex flex-col justify-between group">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs font-medium uppercase tracking-wider">Peak Heat Anomaly</span>
          <ThermometerSun className="w-4 h-4 text-orange-400" />
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold text-orange-400 tracking-tight">
            +{kpis.max_lst_anomaly_c}°C
          </span>
          <span className="text-xs text-slate-400 font-mono">({kpis.peak_surface_temp_c}°C surface)</span>
        </div>
        <div className="mt-2 text-[11px] text-orange-400/80 font-medium">
          Max urban heat island anomaly
        </div>
      </div>

      {/* KPI 4: Available Intervention Budget */}
      <div className="glass-panel rounded-xl p-3.5 flex flex-col justify-between group border-emerald-500/20">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs font-medium uppercase tracking-wider">Local Budget</span>
          <span className="font-mono text-emerald-400 font-bold text-xs">{sym}</span>
        </div>
        <div className="flex items-baseline justify-between">
          <span className="text-2xl font-bold text-emerald-400 tracking-tight font-mono">
            {sym}{formatBudget(budget)}
          </span>
          <button
            onClick={onEditBudget}
            className="text-[10px] text-emerald-300 hover:text-emerald-200 underline font-medium"
          >
            Adjust
          </button>
        </div>
        <div className="mt-2 text-[11px] text-slate-400 flex items-center justify-between">
          <span>Resilience Cap ({kpis.currency_code || 'USD'})</span>
        </div>
      </div>

      {/* KPI 5: Simulated Resilience Impact */}
      <div className={`glass-panel rounded-xl p-3.5 flex flex-col justify-between col-span-2 md:col-span-4 lg:col-span-1 transition ${
        hasSim ? 'border-emerald-500/50 bg-emerald-950/20' : 'border-slate-800'
      }`}>
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs font-medium uppercase tracking-wider">Simulation Delta</span>
          {hasSim ? (
            <ShieldCheck className="w-4 h-4 text-emerald-400 animate-bounce" />
          ) : (
            <TrendingDown className="w-4 h-4 text-slate-500" />
          )}
        </div>
        <div className="flex items-baseline gap-2">
          {hasSim ? (
            <>
              <span className="text-2xl font-bold text-emerald-400 tracking-tight">
                -{simulationResult.risk_reduction_pct}%
              </span>
              <span className="text-xs text-emerald-300 font-mono">
                (-{simulationResult.risk_delta} pts)
              </span>
            </>
          ) : (
            <span className="text-lg font-medium text-slate-500">
              Awaiting Action
            </span>
          )}
        </div>
        <div className="mt-2 text-[11px] text-slate-400 truncate">
          {hasSim ? (
            <span className="text-emerald-400 font-medium">
              ~{simulationResult.people_protected.toLocaleString()} people sheltered
            </span>
          ) : (
            'Select interventions below'
          )}
        </div>
      </div>
    </div>
  );
}
