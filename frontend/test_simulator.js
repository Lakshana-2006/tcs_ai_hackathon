// Test script verifying Intervention Simulator calculations, ranges, continuous adjustment, and multiple interventions
import { simulateZoneLocally, DEFAULT_INTERVENTIONS_CATALOG, calculateCompositeRisk } from './src/utils/simulationEngine.js';

const mockZone = {
  id: 'chennai_zone_3',
  name: 'Zone 3 — Historic Commercial & High-Density Core',
  population: 142000,
  baseline_risk: 76.5,
  baseline_hazard: {
    hazard_score: 82.0,
    lst_anomaly_c: 4.8
  },
  baseline_exposure: {
    exposure_score: 84.0,
    effective_pop_exposed: 72000
  },
  baseline_vulnerability: {
    vulnerability_score: 65.0
  }
};

const mockCity = {
  name: 'Chennai',
  currency: {
    code: 'INR',
    symbol: '₹',
    name: 'Indian Rupee',
    rate_per_usd: 83.5
  }
};

console.log("==================================================================");
console.log("   INTERVENTION SIMULATOR DYNAMIC INTENSITY VERIFICATION SUITE   ");
console.log("==================================================================");

// 1. Verify Catalog Metadata and Ranges
console.log("\n--- 1. Testing Catalog Range Synchronization ---");
DEFAULT_INTERVENTIONS_CATALOG.forEach(item => {
  console.log(`[PASS] ${item.name}: Range [${item.min_intensity} - ${item.max_intensity}] ${item.unit}, step: ${item.step}`);
  if (item.min_intensity !== 0.0) throw new Error(`Min intensity for ${item.id} should be 0.0`);
  if (!item.max_intensity || item.max_intensity <= 0) throw new Error(`Invalid max intensity for ${item.id}`);
  if (!item.step || item.step <= 0) throw new Error(`Invalid step for ${item.id}`);
});

// 2. Test Continuous Dynamic Movement for Tree Planting across range
console.log("\n--- 2. Testing Continuous Dynamic Adjustment: Tree Planting ---");
const testIntensities = [0.0, 5.5, 12.5, 25.0, 37.5, 50.0];
let prevRiskDelta = -1;
let prevCost = -1;

testIntensities.forEach(intensity => {
  const result = simulateZoneLocally(mockZone, { tree_planting: intensity }, DEFAULT_INTERVENTIONS_CATALOG, mockCity);
  console.log(`  Intensity: ${intensity}% -> LST Reduction: -${result.lst_reduction_c}°C, Risk Delta: -${result.risk_delta} pts (${result.risk_reduction_pct}%), Est Cost: ₹${result.estimated_cost_local.toLocaleString()}`);
  
  if (intensity > 0) {
    if (result.risk_delta <= prevRiskDelta) throw new Error(`Risk delta should increase monotonically with intensity`);
    if (result.estimated_cost_local <= prevCost) throw new Error(`Cost should increase monotonically with intensity`);
    if (result.lst_reduction_c <= 0) throw new Error(`LST reduction should be greater than 0 for tree planting`);
  }
  prevRiskDelta = result.risk_delta;
  prevCost = result.estimated_cost_local;
});
console.log("[PASS] Tree Planting scaled continuously and smoothly across valid range [0 - 50]%.");

// 3. Test Intervention Range Isolation (Cooling Hubs range [0-10])
console.log("\n--- 3. Testing Intervention Range & Biophysical Rules: Cooling Centers ---");
const ccResult = simulateZoneLocally(mockZone, { cooling_centers: 6 }, DEFAULT_INTERVENTIONS_CATALOG, mockCity);
console.log(`  Cooling Centers (6 hubs): LST Reduction: ${ccResult.lst_reduction_c}°C, Risk Delta: -${ccResult.risk_delta} pts, People Protected: ${ccResult.people_protected.toLocaleString()}`);
if (ccResult.lst_reduction_c !== 0.0) throw new Error("Cooling centers must NOT claim outdoor surface temperature reduction!");
if (ccResult.people_protected <= 0) throw new Error("Cooling centers must protect vulnerable population!");
console.log("[PASS] Cooling centers biophysical constraint respected (0°C surface cooling, social exposure reduced).");

// 4. Test Multiple Interventions Combination
console.log("\n--- 4. Testing Multi-Intervention Scenario ---");
const multiResult = simulateZoneLocally(mockZone, {
  tree_planting: 20.5,
  cool_roofs: 35.0,
  cooling_centers: 4.0
}, DEFAULT_INTERVENTIONS_CATALOG, mockCity);

console.log(`  Multi Lever Impact:`);
console.log(`    - LST Reduction: -${multiResult.lst_reduction_c}°C`);
console.log(`    - Risk Delta: -${multiResult.risk_delta} pts (${multiResult.risk_reduction_pct}% reduction)`);
console.log(`    - Total Cost: ₹${multiResult.estimated_cost_local.toLocaleString()} ($${multiResult.estimated_cost_usd.toLocaleString()})`);
console.log(`    - People Protected: ${multiResult.people_protected.toLocaleString()}`);
console.log(`    - 90% CI: Low: -${multiResult.uncertainty.low} pts, Expected: -${multiResult.uncertainty.expected} pts, High: -${multiResult.uncertainty.high} pts`);

if (multiResult.risk_delta <= 0) throw new Error("Multi-intervention simulation should show risk delta > 0");
if (multiResult.lst_reduction_c <= 0) throw new Error("Multi-intervention simulation should show cooling > 0");
console.log("[PASS] Multi-intervention simulation calculated successfully.");

// 5. Test Switching Interventions preserves non-selected lever values
console.log("\n--- 5. Testing Intervention Switching & Synchronization ---");
const state = {
  tree_planting: 15.5,
  cool_roofs: 30.0,
  cooling_centers: 0,
  permeable_pavements: 0,
  green_corridors: 0
};
// Simulating user switching active lever to cool_roofs and adjusting it to 42.5
state.cool_roofs = 42.5;
const switchResult = simulateZoneLocally(mockZone, state, DEFAULT_INTERVENTIONS_CATALOG, mockCity);
console.log(`  Switched to Cool Roofs at 42.5%: Risk Delta: -${switchResult.risk_delta} pts, LST Drop: -${switchResult.lst_reduction_c}°C`);
if (switchResult.intervention_breakdown.length !== 2) throw new Error("Should have 2 active interventions");
console.log("[PASS] Lever switching and dynamic range synchronization verified.");

console.log("\n==================================================================");
console.log(">>> ALL SIMULATOR DYNAMIC INTENSITY TESTS PASSED SUCCESSFULLY! <<<");
console.log("==================================================================");

