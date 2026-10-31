import React, { useState } from 'react';
import { Satellite, AlertTriangle, CheckCircle2, Info, X, ExternalLink } from 'lucide-react';

export default function DisclaimerBanner({ satelliteStatus }) {
  const [dismissed, setDismissed] = useState(false);
  const [showSetupModal, setShowSetupModal] = useState(false);

  if (dismissed) return null;

  const isEeAuth = satelliteStatus?.authenticated;

  return (
    <>
      <div className={`border-b px-4 py-2 text-xs transition-colors ${
        isEeAuth 
          ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-200' 
          : 'bg-slate-900/90 border-amber-500/30 text-slate-300'
      }`}>
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="flex items-center gap-1.5 font-bold font-mono text-[11px] px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-cyan-400 shrink-0">
              <Satellite className="w-3.5 h-3.5 text-cyan-400" />
              <span>GEE Satellite Pipeline</span>
            </span>

            {isEeAuth ? (
              <span className="flex items-center gap-1 text-emerald-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>
                  <strong>Earth Engine Authenticated:</strong> Streaming Landsat 8/9 LST (ST_B10 30m), Sentinel-2 MSI (10m), and MODIS MOD11A1 (1km).
                </span>
              </span>
            ) : (
              <span className="flex items-center gap-1.5 text-amber-200">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                <span>
                  <strong>Satellite Pipeline Configuration:</strong> Google Earth Engine Python API is integrated. To enable live satellite queries, provide service account credentials in <code className="bg-slate-950 px-1 py-0.2 rounded font-mono text-amber-300">backend/.env</code>.
                </span>
                <button
                  type="button"
                  onClick={() => setShowSetupModal(true)}
                  className="underline text-amber-300 hover:text-white font-medium ml-1 cursor-pointer"
                >
                  View Setup Guide
                </button>
              </span>
            )}
          </div>

          <div className="flex items-center gap-3 shrink-0 text-[11px] text-slate-400">
            <span className="hidden md:inline font-mono">
              Sources: Satellite • Open-Meteo • Municipal Census
            </span>
            <button
              onClick={() => setDismissed(true)}
              className="text-slate-400 hover:text-slate-200 p-0.5"
              aria-label="Dismiss banner"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Setup Guide Modal */}
      {showSetupModal && (
        <div className="fixed inset-0 z-[100] bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-lg w-full p-5 shadow-2xl space-y-4 text-xs text-slate-300">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Satellite className="w-4 h-4 text-cyan-400" />
                <h4 className="font-bold text-white text-sm">Google Earth Engine Setup Guide</h4>
              </div>
              <button 
                onClick={() => setShowSetupModal(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="leading-relaxed text-slate-300">
              The HEATSHIELD AI backend includes a complete Earth Engine processing pipeline for:
            </p>

            <ul className="list-disc pl-5 space-y-1 text-slate-400 font-mono text-[11px]">
              <li><strong>LANDSAT/LC08/C02/T1_L2 & LC09:</strong> Scaled Surface Temperature (<code className="text-emerald-400">ST_B10</code>) with QA_PIXEL cloud masking</li>
              <li><strong>COPERNICUS/S2_SR_HARMONIZED:</strong> Surface reflectance NDVI, NDWI, NDBI & vegetation cover %</li>
              <li><strong>MODIS/061/MOD11A1:</strong> 1km regional baseline LST</li>
            </ul>

            <div className="space-y-1.5">
              <span className="font-semibold text-slate-200 block">Required Configuration in <code className="text-emerald-400">backend/.env</code>:</span>
              <pre className="bg-slate-950 p-3 rounded-lg border border-slate-800 font-mono text-[11px] text-cyan-300 overflow-x-auto">
{`# Google Earth Engine Service Account
EE_PROJECT_ID=your-gcp-project-id
EE_SERVICE_ACCOUNT=your-sa@project.iam.gserviceaccount.com
EE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n"
# Or provide the file path:
# EE_KEY_FILE=path/to/key.json`}
              </pre>
            </div>

            <div className="flex justify-end pt-2 border-t border-slate-800">
              <button
                onClick={() => setShowSetupModal(false)}
                className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium transition"
              >
                Got It
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
