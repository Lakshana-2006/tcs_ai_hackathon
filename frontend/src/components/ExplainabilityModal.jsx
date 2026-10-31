import React from 'react';
import { X, Cpu, Shield, Thermometer, Users, Scale, AlertTriangle, BookOpen } from 'lucide-react';

export default function ExplainabilityModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm overflow-y-auto">
      <div className="relative w-full max-w-3xl glass-panel bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl p-6 text-slate-200 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-lg bg-indigo-500/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">HEATSHIELD AI — Model Architecture & Decision Logic</h2>
              <p className="text-xs text-slate-400">IPCC AR6 Risk Framework, Illustrative Weights, and Biophysical Constraints</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Disclaimer Callout */}
        <div className="bg-amber-950/40 border border-amber-500/30 rounded-xl p-3.5 mb-5 text-xs text-amber-200">
          <div className="flex items-center gap-2 font-bold text-amber-300 mb-1">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
            <span>Prototype Disclosure & Academic Integrity</span>
          </div>
          <p>
            This software is an illustrative digital twin hackathon MVP. All metrics (Land Surface Temperature anomalies,
            population densities, and intervention response curves) are calibrated on synthetic assumptions. It is{' '}
            <strong>not scientifically validated</strong> or certified for real-world life-critical urban emergency management.
          </p>
        </div>

        {/* Section 1: The IPCC Tri-Factor Equation */}
        <div className="space-y-3 mb-6">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-emerald-400" />
            <span>1. Explainable Baseline Risk Score Formula</span>
          </h3>
          <p className="text-xs text-slate-300 leading-relaxed">
            Following the Intergovernmental Panel on Climate Change (IPCC) risk paradigm, risk emerges from the confluence
            of <strong>Hazard</strong>, <strong>Exposure</strong>, and <strong>Vulnerability</strong>:
          </p>
          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 font-mono text-xs text-emerald-400 text-center">
            Composite Risk = (0.35 × Hazard_Score) + (0.30 × Exposure_Score) + (0.35 × Vulnerability_Score)
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs mt-3">
            <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800">
              <span className="font-bold text-rose-400 flex items-center gap-1.5 mb-1">
                <Thermometer className="w-3.5 h-3.5" /> Hazard (35%)
              </span>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                Represents physical heat exposure: Land Surface Temperature anomaly (LST in °C), annual extreme heat days (&gt;38°C), and satellite Urban Heat Island (UHI) intensity index.
              </p>
            </div>
            <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800">
              <span className="font-bold text-amber-400 flex items-center gap-1.5 mb-1">
                <Users className="w-3.5 h-3.5" /> Exposure (30%)
              </span>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                Represents human presence: Residential population density (/km²), daytime commuter influx, and proportion of outdoor shift workers.
              </p>
            </div>
            <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800">
              <span className="font-bold text-indigo-400 flex items-center gap-1.5 mb-1">
                <Shield className="w-3.5 h-3.5" /> Vulnerability (35%)
              </span>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                Represents demographic sensitivity: Senior population % (&gt;65), child % (&lt;5), poverty rate %, tree canopy deficit %, and lack of central air conditioning.
              </p>
            </div>
          </div>
        </div>

        {/* Section 2: Cooling Center Physics Law */}
        <div className="space-y-2 mb-6 border-t border-slate-800 pt-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Thermometer className="w-4 h-4 text-cyan-400" />
            <span>2. Biophysical Law: Indoor Shelter vs Land Surface Temperature</span>
          </h3>
          <div className="bg-slate-950/70 p-3.5 rounded-lg border border-cyan-500/30 text-xs text-slate-300 space-y-2">
            <p>
              A common flaw in naive climate models is attributing outdoor thermal reduction to indoor shelters. In HEATSHIELD AI:
            </p>
            <ul className="list-disc list-inside space-y-1 text-slate-300 text-[11px]">
              <li>
                <strong className="text-cyan-300">Cooling Centers</strong> strictly reduce <em>Human Exposure</em> and <em>Vulnerability</em> by providing climate-controlled indoor sanctuaries for outdoor workers, seniors, and unhoused citizens. They have <strong>0.0°C impact on outdoor Land Surface Temperature (LST)</strong>.
              </li>
              <li>
                <strong className="text-emerald-300">Tree Planting & Cool Roofs</strong> physically lower surface temperature by increasing solar reflectance (albedo) and evapotranspirative cooling.
              </li>
            </ul>
          </div>
        </div>

        {/* Section 3: Equity Engine & Uncertainty */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 border-t border-slate-800 pt-4 text-xs">
          <div>
            <h4 className="font-bold text-slate-200 flex items-center gap-1.5 mb-1.5">
              <Scale className="w-4 h-4 text-indigo-400" />
              <span>Equity Weighting Engine</span>
            </h4>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Classical cost-benefit analyses often channel municipal capital into high-property-value districts. HEATSHIELD AI incorporates a Social Vulnerability Index (SVI) multiplier (up to 1.85x boost) ensuring low-income and senior neighborhoods receive first-line capital protection.
            </p>
          </div>

          <div>
            <h4 className="font-bold text-slate-200 flex items-center gap-1.5 mb-1.5">
              <Cpu className="w-4 h-4 text-amber-400" />
              <span>Uncertainty Bounds (90% CI)</span>
            </h4>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Every climate intervention carries real-world volatility (sapling mortality, cloud cover, compliance rate). The simulation computes Gaussian variance propagation across all active levers, presenting a 90% confidence interval [Low, Expected, High] for all projected risk reductions.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-6 pt-4 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold transition"
          >
            Close Documentation
          </button>
        </div>
      </div>
    </div>
  );
}

