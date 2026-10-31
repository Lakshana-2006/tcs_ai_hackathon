import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import DisclaimerBanner from './components/DisclaimerBanner';
import KpiBar from './components/KpiBar';
import HeatMap from './components/HeatMap';
import ZoneDetails from './components/ZoneDetails';
import InterventionSimulator from './components/InterventionSimulator';
import BudgetOptimizer from './components/BudgetOptimizer';
import ExplainabilityModal from './components/ExplainabilityModal';
import DatasetSourcesModal from './components/DatasetSourcesModal';
import TemporalAnalysisPanel from './components/TemporalAnalysisPanel';
import ChatAssistant from './components/ChatAssistant';
import { 
  fetchCityData, 
  fetchInterventionsCatalog, 
  simulateInterventions 
} from './api';
import { simulateZoneLocally, DEFAULT_INTERVENTIONS_CATALOG } from './utils/simulationEngine';
import { Map, Cpu, RefreshCw, AlertCircle, Globe } from 'lucide-react';

const DEFAULT_CITY = {
  name: 'Chennai',
  country: 'India',
  country_code: 'IN',
  latitude: 13.0827,
  longitude: 80.2707,
  currency: { code: 'INR', symbol: '₹', name: 'Indian Rupee', rate_per_usd: 83.5, default_budget: 25000000 }
};

export default function App() {
  const [city, setCity] = useState(DEFAULT_CITY);
  const [weather, setWeather] = useState(null);
  const [kpis, setKpis] = useState(null);
  const [zones, setZones] = useState([]);
  const [catalog, setCatalog] = useState(DEFAULT_INTERVENTIONS_CATALOG);
  const [selectedZoneId, setSelectedZoneId] = useState(null);
  const [budget, setBudget] = useState(25000000);
  const [selectedInterventions, setSelectedInterventions] = useState({
    tree_planting: 0,
    cool_roofs: 0,
    cooling_centers: 0,
    permeable_pavements: 0,
    green_corridors: 0
  });
  const [simulationResult, setSimulationResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingSim, setLoadingSim] = useState(false);
  const [error, setError] = useState(null);
  const [explainModalOpen, setExplainModalOpen] = useState(false);
  const [datasetModalOpen, setDatasetModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('twin'); // 'twin' or 'optimizer'
  const [satelliteStatus, setSatelliteStatus] = useState(null);
  const [satelliteLayers, setSatelliteLayers] = useState({});

  // Load city telemetry, zones, and weather
  const loadCityData = async (targetCity) => {
    setLoading(true);
    setError(null);
    try {
      const [cityData, catalogData] = await Promise.all([
        fetchCityData(
          targetCity.name,
          targetCity.country,
          targetCity.country_code,
          targetCity.latitude,
          targetCity.longitude
        ),
        fetchInterventionsCatalog()
      ]);

      const loadedCity = cityData.city;
      setCity(loadedCity);
      setWeather(cityData.weather);
      setKpis(cityData.kpis);
      setZones(cityData.zones || []);
      if (cityData.earth_engine_status) {
        setSatelliteStatus(cityData.earth_engine_status);
      }
      if (cityData.satellite_layers) {
        setSatelliteLayers(cityData.satellite_layers);
      }
      const resolvedCatalog = (catalogData && catalogData.interventions && catalogData.interventions.length > 0)
        ? catalogData.interventions
        : DEFAULT_INTERVENTIONS_CATALOG;
      setCatalog(resolvedCatalog);

      // Default budget in local currency
      const defaultBudg = loadedCity.currency?.default_budget || 3500000;
      setBudget(defaultBudg);

      // Select high vulnerability zone (e.g. Zone 3 Historic Eastside)
      if (cityData.zones && cityData.zones.length > 0) {
        const highVuln = cityData.zones.find(z => z.id.endsWith('zone_3')) || cityData.zones[0];
        setSelectedZoneId(highVuln.id);
      }

      // Reset interventions so old city simulation values never linger
      const initialInterventions = {
        tree_planting: 0,
        cool_roofs: 0,
        cooling_centers: 0,
        permeable_pavements: 0,
        green_corridors: 0
      };
      setSelectedInterventions(initialInterventions);
      setSimulationResult(null);

    } catch (err) {
      console.error('Failed to load city data:', err);
      setError(`Could not retrieve digital twin for ${targetCity.name}. Please ensure the backend is running.`);
    } finally {
      setLoading(false);
    }
  };

  // Initial mount load
  useEffect(() => {
    loadCityData(DEFAULT_CITY);
  }, []);

  // When user selects a new city from search or quick pills
  const handleSelectCity = (newCity) => {
    loadCityData(newCity);
  };

  const activeZone = zones.find(z => z.id === selectedZoneId) || zones[0];

  // Run simulation whenever zone or interventions change
  const runSim = useCallback(async (zoneId, interventions, currentZones, currentCity) => {
    if (!zoneId || !currentZones || currentZones.length === 0) return;
    const activeZ = currentZones.find(z => z.id === zoneId);
    if (!activeZ) return;

    // Immediately calculate locally so simulation results update synchronously on every frame
    const localRes = simulateZoneLocally(activeZ, interventions, catalog, currentCity);
    if (localRes) {
      setSimulationResult(localRes);
    }

    setLoadingSim(true);
    try {
      const res = await simulateInterventions(zoneId, interventions, activeZ, currentCity);
      if (res && res.zone_result) {
        setSimulationResult(res.zone_result);
      }
    } catch (err) {
      console.warn('Simulation backend fallback to local calculations:', err.message);
    } finally {
      setLoadingSim(false);
    }
  }, [catalog]);

  useEffect(() => {
    if (selectedZoneId && zones.length > 0) {
      runSim(selectedZoneId, selectedInterventions, zones, city);
    }
  }, [selectedZoneId, selectedInterventions, zones, city, runSim]);

  const handleSelectZone = (zoneId) => {
    setSelectedZoneId(zoneId);
  };

  const handleChangeIntervention = (itemId, intensity) => {
    setSelectedInterventions(prev => {
      const next = {
        ...prev,
        [itemId]: intensity
      };
      if (activeZone) {
        const localSim = simulateZoneLocally(activeZone, next, catalog, city);
        if (localSim) {
          setSimulationResult(localSim);
        }
      }
      return next;
    });
  };

  const handleResetInterventions = () => {
    const cleared = {
      tree_planting: 0,
      cool_roofs: 0,
      cooling_centers: 0,
      permeable_pavements: 0,
      green_corridors: 0
    };
    setSelectedInterventions(cleared);
    if (activeZone) {
      const localSim = simulateZoneLocally(activeZone, cleared, catalog, city);
      if (localSim) {
        setSimulationResult(localSim);
      }
    }
  };

  const handleApplyOptimizerPlan = (optimizerPlan) => {
    const zoneAllocations = optimizerPlan.allocations_by_zone[selectedZoneId] || [];
    const newInterventions = {
      tree_planting: 0,
      cool_roofs: 0,
      cooling_centers: 0,
      permeable_pavements: 0,
      green_corridors: 0
    };

    zoneAllocations.forEach(a => {
      newInterventions[a.intervention_id] = a.intensity;
    });

    setSelectedInterventions(newInterventions);
    if (activeZone) {
      const localSim = simulateZoneLocally(activeZone, newInterventions, catalog, city);
      if (localSim) {
        setSimulationResult(localSim);
      }
    }
    setActiveTab('twin');
  };

  const hasActiveInterventions = Object.values(selectedInterventions).some(v => v > 0);

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col font-sans selection:bg-rose-500 selection:text-white">
      {/* Header with Prominent City Search & Live Weather Bar */}
      <Header
        selectedCity={city}
        onSelectCity={handleSelectCity}
        weather={weather}
        onOpenExplain={() => setExplainModalOpen(true)}
        onOpenDatasets={() => setDatasetModalOpen(true)}
        onReset={handleResetInterventions}
        simulatedActive={hasActiveInterventions}
      />

      {/* Earth Engine Satellite & Data Provenance Banner */}
      <DisclaimerBanner satelliteStatus={satelliteStatus} />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-3 sm:p-4 lg:p-6 space-y-4">
        {/* Loading / Error States */}
        {loading && (
          <div className="glass-panel rounded-xl p-12 text-center text-slate-400 flex flex-col items-center justify-center gap-3">
            <div className="w-8 h-8 border-3 border-rose-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="font-semibold text-white">
              Connecting to Global Climate Twin for {city.name}...
            </p>
            <p className="text-xs text-slate-500">
              Fetching real-time Open-Meteo telemetry and generating 5 microclimate analysis zones
            </p>
          </div>
        )}

        {error && !loading && (
          <div className="glass-panel border-rose-500/40 bg-rose-950/20 rounded-xl p-6 text-center text-rose-300 flex flex-col items-center gap-3">
            <AlertCircle className="w-8 h-8 text-rose-400" />
            <p className="font-bold text-white">Digital Twin Connection Issue</p>
            <p className="text-xs max-w-md text-rose-300/80">{error}</p>
            <button
              onClick={() => loadCityData(city)}
              className="mt-2 text-xs px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg font-medium flex items-center gap-1.5 transition"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Retry City Telemetry
            </button>
          </div>
        )}

        {!loading && !error && (
          <>
            {/* Top KPI Metric Cards (Currency-Aware) */}
            <KpiBar
              kpis={kpis}
              budget={budget}
              currencySymbol={city?.currency?.symbol}
              onEditBudget={() => setActiveTab('optimizer')}
              simulationResult={simulationResult}
            />

            {/* Navigation Tabs */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-2 pt-1">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setActiveTab('twin')}
                  className={`px-3.5 py-1.5 rounded-lg text-xs font-bold flex items-center gap-2 transition ${
                    activeTab === 'twin'
                      ? 'bg-rose-500 text-white shadow-md shadow-rose-500/20'
                      : 'text-slate-400 hover:text-white hover:bg-slate-900'
                  }`}
                >
                  <Map className="w-3.5 h-3.5" />
                  <span>Interactive Twin & What-If Simulator</span>
                </button>

                <button
                  onClick={() => setActiveTab('optimizer')}
                  className={`px-3.5 py-1.5 rounded-lg text-xs font-bold flex items-center gap-2 transition ${
                    activeTab === 'optimizer'
                      ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                      : 'text-slate-400 hover:text-white hover:bg-slate-900'
                  }`}
                >
                  <Cpu className="w-3.5 h-3.5" />
                  <span>AI Budget Optimizer & Policy Rationale</span>
                </button>
              </div>

              {/* Zone Quick Selector Dropdown for Currently Selected City */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500 hidden sm:inline">Active Zone:</span>
                <select
                  value={selectedZoneId || ''}
                  onChange={(e) => handleSelectZone(e.target.value)}
                  className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-rose-500 font-medium cursor-pointer max-w-[220px] truncate"
                >
                  {zones.map(z => (
                    <option key={z.id} value={z.id}>
                      {z.name} (Risk: {z.baseline_risk})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Tab 1: Interactive Twin & Simulator */}
            {activeTab === 'twin' && (
              <div className="space-y-4">
                {/* Past / Present / Future / Climate 2050 Temporal Analysis Panel */}
                <TemporalAnalysisPanel
                  city={city}
                  weather={weather}
                  zones={zones}
                  activeZoneId={selectedZoneId}
                  onSelectZone={handleSelectZone}
                />

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
                  <div className="lg:col-span-7">
                    <HeatMap
                      city={city}
                      zones={zones}
                      selectedZoneId={selectedZoneId}
                      onSelectZone={handleSelectZone}
                      simulationResult={simulationResult}
                      satelliteLayers={satelliteLayers}
                      satelliteStatus={satelliteStatus}
                    />
                  </div>

                  <div className="lg:col-span-5">
                    <ZoneDetails
                      zone={activeZone}
                      city={city}
                      simulationResult={simulationResult}
                      satelliteStatus={satelliteStatus}
                    />
                  </div>
                </div>

                <InterventionSimulator
                  zone={activeZone}
                  city={city}
                  interventionsCatalog={catalog}
                  selectedInterventions={selectedInterventions}
                  onChangeIntervention={handleChangeIntervention}
                  onResetInterventions={handleResetInterventions}
                  simulationResult={simulationResult}
                  loadingSim={loadingSim}
                />
              </div>
            )}

            {/* Tab 2: Budget Optimizer */}
            {activeTab === 'optimizer' && (
              <BudgetOptimizer
                city={city}
                zones={zones}
                currentBudget={budget}
                onUpdateBudget={(b) => setBudget(b)}
                onApplyPlanToSimulator={handleApplyOptimizerPlan}
                onSelectZone={handleSelectZone}
              />
            )}
          </>
        )}
      </main>

      {/* Model Explainability Modal */}
      <ExplainabilityModal
        isOpen={explainModalOpen}
        onClose={() => setExplainModalOpen(false)}
      />

      {/* Dataset Sources & Provenance Registry Modal */}
      <DatasetSourcesModal
        isOpen={datasetModalOpen}
        onClose={() => setDatasetModalOpen(false)}
        selectedCity={city}
      />

      {/* Floating AI Chat Assistant */}
      <ChatAssistant
        city={city}
        weather={weather}
        zones={zones}
        selectedZone={activeZone}
        selectedInterventions={selectedInterventions}
        simulationResult={simulationResult}
      />

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/80 px-4 py-3 mt-8 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>HEATSHIELD AI — Global Urban Climate Resilience Digital Twin</span>
          <span className="font-mono text-[11px] text-slate-500">
            Open-Meteo Weather • Google Earth Engine (Landsat 8/9, Sentinel-2, MODIS) • Multi-Criteria Models
          </span>
        </div>
      </footer>
    </div>
  );
}
