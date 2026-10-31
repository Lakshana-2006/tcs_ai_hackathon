import React, { useState, useEffect, useRef } from 'react';
import { 
  ShieldAlert, 
  Search, 
  MapPin, 
  RotateCcw, 
  Cpu, 
  Thermometer, 
  Droplets, 
  CloudSun, 
  Check, 
  Loader2,
  Globe2,
  ExternalLink,
  Database
} from 'lucide-react';
import { searchCities } from '../api';

const FEATURED_CITIES = [
  { name: 'Chennai', country: 'India', country_code: 'IN', admin1: 'Tamil Nadu', latitude: 13.0827, longitude: 80.2707 },
  { name: 'Mumbai', country: 'India', country_code: 'IN', admin1: 'Maharashtra', latitude: 19.0760, longitude: 72.8777 },
  { name: 'Tokyo', country: 'Japan', country_code: 'JP', admin1: 'Tokyo', latitude: 35.6762, longitude: 139.6503 },
  { name: 'London', country: 'United Kingdom', country_code: 'GB', admin1: 'England', latitude: 51.5074, longitude: -0.1278 },
  { name: 'Dubai', country: 'United Arab Emirates', country_code: 'AE', admin1: 'Dubai', latitude: 25.2048, longitude: 55.2708 },
  { name: 'New York', country: 'United States', country_code: 'US', admin1: 'New York', latitude: 40.7128, longitude: -74.0060 }
];

export default function Header({ 
  selectedCity, 
  onSelectCity, 
  weather, 
  onOpenExplain, 
  onOpenDatasets,
  onReset, 
  simulatedActive 
}) {
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown on click outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Debounced search
  useEffect(() => {
    if (!query || query.trim().length < 2) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }

    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        const results = await searchCities(query);
        setSearchResults(results);
        setDropdownOpen(true);
      } catch (err) {
        console.error('City search failed:', err);
      } finally {
        setIsSearching(false);
      }
    }, 350);

    return () => clearTimeout(timer);
  }, [query]);

  const handlePickCity = (city) => {
    onSelectCity(city);
    setQuery('');
    setDropdownOpen(false);
  };

  return (
    <header className="border-b border-slate-800 bg-slate-900/95 backdrop-blur sticky top-0 z-40 px-3 sm:px-6 py-2.5">
      <div className="max-w-7xl mx-auto flex flex-col gap-2.5">
        {/* Top Row: Brand, Global Search Bar, Action Buttons */}
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
          {/* Brand */}
          <div className="flex items-center gap-2.5 shrink-0">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-rose-500 via-amber-500 to-emerald-500 p-0.5 shadow-lg shadow-rose-500/20">
              <div className="h-full w-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <ShieldAlert className="h-5 w-5 text-rose-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-extrabold text-base sm:text-lg tracking-tight" style={{ color: '#00D4FF' }}>
                  HEATSHIELD AI
                </h1>
                <span className="text-[9px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  Global Digital Twin
                </span>
              </div>
              <p className="text-[11px] text-slate-400 flex items-center gap-1.5 font-medium">
                <Globe2 className="w-3 h-3 text-cyan-400" />
                <span>Worldwide Urban Microclimate Resilience</span>
              </p>
            </div>
          </div>

          {/* Prominent Global City Search Input */}
          <div className="relative flex-1 max-w-xl" ref={dropdownRef}>
            <div className="relative flex items-center">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 pointer-events-none" />
              <input
                type="text"
                placeholder="Search any global city (e.g. Chennai, Tokyo, London, Dubai, Paris)..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onFocus={() => { if (searchResults.length > 0) setDropdownOpen(true); }}
                className="w-full bg-slate-950/90 border border-slate-700/80 focus:border-rose-500 text-xs text-white rounded-xl pl-9 pr-9 py-2 focus:outline-none focus:ring-1 focus:ring-rose-500 transition shadow-inner placeholder:text-slate-500"
              />
              {isSearching && (
                <Loader2 className="w-3.5 h-3.5 text-rose-400 absolute right-3 animate-spin" />
              )}
            </div>

            {/* Autocomplete Dropdown */}
            {dropdownOpen && searchResults.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-1.5 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl overflow-hidden z-50 max-h-72 overflow-y-auto">
                <div className="px-3 py-1.5 text-[10px] uppercase font-bold text-slate-500 border-b border-slate-800 bg-slate-950/50">
                  Global Geocoded Results
                </div>
                {searchResults.map((city, idx) => (
                  <button
                    key={`${city.latitude}_${city.longitude}_${idx}`}
                    onClick={() => handlePickCity(city)}
                    className="w-full text-left px-3 py-2 text-xs hover:bg-slate-800/80 transition flex items-center justify-between border-b border-slate-800/50 last:border-0 group"
                  >
                    <div className="flex items-center gap-2">
                      <MapPin className="w-3.5 h-3.5 text-rose-400 shrink-0 group-hover:scale-110 transition" />
                      <div>
                        <span className="font-semibold text-white">{city.name}</span>
                        <span className="text-slate-400 ml-1.5 text-[11px]">
                          {city.admin1 ? `${city.admin1}, ` : ''}{city.country}
                        </span>
                      </div>
                    </div>
                    <div className="text-[10px] text-slate-500 font-mono">
                      {city.latitude > 0 ? `${city.latitude}°N` : `${Math.abs(city.latitude)}°S`},{' '}
                      {city.longitude > 0 ? `${city.longitude}°E` : `${Math.abs(city.longitude)}°W`}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2 justify-end shrink-0">
            {simulatedActive && (
              <button
                onClick={onReset}
                className="text-xs flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
                title="Reset simulation parameters to baseline"
              >
                <RotateCcw className="w-3.5 h-3.5 text-slate-400" />
                <span className="hidden sm:inline">Reset Baseline</span>
              </button>
            )}

            <button
              onClick={onOpenDatasets}
              className="text-xs flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 transition font-medium"
            >
              <Database className="w-3.5 h-3.5 text-cyan-400" />
              <span className="hidden sm:inline">Dataset Registry & Provenance</span>
              <span className="sm:hidden">Datasets</span>
            </button>

            <button
              onClick={onOpenExplain}
              className="text-xs flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 transition font-medium"
            >
              <Cpu className="w-3.5 h-3.5 text-indigo-400" />
              <span>Model Logic & Weights</span>
            </button>
          </div>
        </div>

        {/* Bottom Row: Selected City Display & Live Open-Meteo Weather Bar */}
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-2 pt-1 border-t border-slate-800/60">
          {/* Quick City Presets */}
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mr-1">
              Quick Cities:
            </span>
            {FEATURED_CITIES.map((c) => {
              const isActive = selectedCity && selectedCity.name === c.name;
              return (
                <button
                  key={c.name}
                  onClick={() => handlePickCity(c)}
                  className={`text-[11px] px-2.5 py-0.5 rounded-full font-medium transition flex items-center gap-1 ${
                    isActive
                      ? 'bg-rose-500 text-white shadow-sm'
                      : 'bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700/60'
                  }`}
                >
                  {isActive && <Check className="w-2.5 h-2.5" />}
                  <span>{c.name}</span>
                </button>
              );
            })}
          </div>

          {/* Currently Selected City & Live Weather Card */}
          {selectedCity && (
            <div className="flex items-center gap-3 text-xs bg-slate-950/70 border border-slate-800 rounded-lg px-3 py-1 text-slate-300 flex-wrap">
              <div className="flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                <span className="font-bold text-white text-xs">{selectedCity.name}</span>
                <span className="text-[10px] text-slate-400">({selectedCity.country})</span>
              </div>

              {weather && weather.air_temperature_c !== undefined && (
                <>
                  <span className="text-slate-700">•</span>
                  <div className="flex items-center gap-1 text-amber-300 font-mono font-medium">
                    <Thermometer className="w-3 h-3 text-amber-400" />
                    <span>{weather.air_temperature_c}°C</span>
                    <span className="text-[10px] text-slate-400 font-sans">(air @2m)</span>
                  </div>

                  <span className="text-slate-700">•</span>
                  <div className="flex items-center gap-1 text-rose-300 font-mono font-medium">
                    <span className="text-[10px] text-slate-400 font-sans">Feels:</span>
                    <span>{weather.apparent_temperature_c}°C</span>
                  </div>

                  <span className="text-slate-700">•</span>
                  <div className="flex items-center gap-1 text-cyan-300 font-mono text-[11px]">
                    <Droplets className="w-3 h-3 text-cyan-400" />
                    <span>{weather.relative_humidity_pct}% RH</span>
                  </div>

                  <span className="text-slate-700 hidden sm:inline">•</span>
                  <span className="text-[10px] text-slate-400 hidden sm:inline">
                    Source: <strong className="text-slate-300 font-mono">Open-Meteo API</strong>
                  </span>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
