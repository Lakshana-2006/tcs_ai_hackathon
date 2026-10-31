export const DEFAULT_INTERVENTIONS_CATALOG = [
  {
    id: "tree_planting",
    name: "Urban Canopy & Reforestation",
    category: "Green Infrastructure",
    unit: "% canopy expansion",
    min_intensity: 0.0,
    default_intensity: 25.0,
    max_intensity: 50.0,
    step: 0.5,
    cost_per_unit_usd: 18000,
    cooling_mechanism: "Direct shade interception & continuous evapotranspiration",
    lst_reduction_per_unit_c: 0.055,
    hazard_reduction_multiplier: 0.28,
    exposure_reduction_multiplier: 0.08,
    vulnerability_reduction_multiplier: 0.25,
    uncertainty_sigma: 0.16,
    reduces_surface_temp: true,
    description: "Planting climate-hardy native shade trees in medians, parks, and residential streets. Long-term cooling benefits with biological lag."
  },
  {
    id: "cool_roofs",
    name: "Cool Roofs & High-Albedo Coatings",
    category: "Reflective Infrastructure",
    unit: "% roof area retrofitted",
    min_intensity: 0.0,
    default_intensity: 30.0,
    max_intensity: 70.0,
    step: 0.5,
    cost_per_unit_usd: 12500,
    cooling_mechanism: "High solar reflectance (albedo >= 0.75) and thermal emittance",
    lst_reduction_per_unit_c: 0.045,
    hazard_reduction_multiplier: 0.24,
    exposure_reduction_multiplier: 0.04,
    vulnerability_reduction_multiplier: 0.10,
    uncertainty_sigma: 0.12,
    reduces_surface_temp: true,
    description: "Applying high-albedo elastomeric coating membranes on commercial flat roofs and residential buildings to reflect incoming solar radiation."
  },
  {
    id: "cooling_centers",
    name: "Emergency Resilient Cooling Hubs",
    category: "Social & Health Defense",
    unit: "operational hubs",
    min_intensity: 0.0,
    default_intensity: 4.0,
    max_intensity: 10.0,
    step: 1.0,
    cost_per_unit_usd: 95000,
    cooling_mechanism: "Safe indoor thermal haven, medical monitoring, cold hydration & clean air filtration",
    lst_reduction_per_unit_c: 0.0,
    hazard_reduction_multiplier: 0.0,
    exposure_reduction_multiplier: 0.40,
    vulnerability_reduction_multiplier: 0.35,
    uncertainty_sigma: 0.10,
    reduces_surface_temp: false,
    description: "Equipping community centers, libraries, and schools with auxiliary microgrid power, high-volume HVAC, and medical triage for high-risk populations."
  },
  {
    id: "permeable_pavements",
    name: "High-Albedo Permeable Pavements",
    category: "Surface Modification",
    unit: "% pavement area replaced",
    min_intensity: 0.0,
    default_intensity: 20.0,
    max_intensity: 60.0,
    step: 0.5,
    cost_per_unit_usd: 14000,
    cooling_mechanism: "Interlocking porous pavers with increased albedo and subsurface stormwater retention",
    lst_reduction_per_unit_c: 0.032,
    hazard_reduction_multiplier: 0.16,
    exposure_reduction_multiplier: 0.05,
    vulnerability_reduction_multiplier: 0.05,
    uncertainty_sigma: 0.18,
    reduces_surface_temp: true,
    description: "Replacing heat-absorbing black asphalt on secondary roadways, parking lots, and alleys with reflective porous interlocking pavers."
  },
  {
    id: "green_corridors",
    name: "Green Corridors & Micro-Misting Shelters",
    category: "Pedestrian Protection",
    unit: "km shaded transit corridor",
    min_intensity: 0.0,
    default_intensity: 5.0,
    max_intensity: 15.0,
    step: 0.5,
    cost_per_unit_usd: 48000,
    cooling_mechanism: "Linear vegetated bioswales, tensile fabric shading, and smart evaporative micro-misting",
    lst_reduction_per_unit_c: 0.08,
    hazard_reduction_multiplier: 0.14,
    exposure_reduction_multiplier: 0.22,
    vulnerability_reduction_multiplier: 0.15,
    uncertainty_sigma: 0.15,
    reduces_surface_temp: true,
    description: "Continuous shaded walking corridors linking transit nodes to residential hubs, featuring solar-powered fine evaporative misting during peak heat."
  }
];

export const WEIGHTS = {
  w_hazard: 0.35,
  w_exposure: 0.30,
  w_vulnerability: 0.35
};

export function calculateCompositeRisk(hazard, exposure, vulnerability) {
  const rawRisk = (
    WEIGHTS.w_hazard * hazard +
    WEIGHTS.w_exposure * exposure +
    WEIGHTS.w_vulnerability * vulnerability
  );
  return Math.round(Math.max(0, Math.min(100, rawRisk)) * 10) / 10;
}

export function simulateZoneLocally(zone, interventions = {}, catalog = DEFAULT_INTERVENTIONS_CATALOG, city = null) {
  if (!zone) return null;

  const catalogMap = {};
  const activeCatalog = (catalog && catalog.length > 0) ? catalog : DEFAULT_INTERVENTIONS_CATALOG;
  activeCatalog.forEach(item => {
    catalogMap[item.id] = item;
  });

  const bHaz = zone.baseline_hazard || { hazard_score: 50, lst_anomaly_c: 3.0 };
  const bExp = zone.baseline_exposure || { exposure_score: 50, effective_pop_exposed: 10000 };
  const bVul = zone.baseline_vulnerability || { vulnerability_score: 50 };

  const baselineHazardScore = bHaz.hazard_score ?? 50.0;
  const baselineExposureScore = bExp.exposure_score ?? 50.0;
  const baselineVulnScore = bVul.vulnerability_score ?? 50.0;
  const baselineRisk = calculateCompositeRisk(baselineHazardScore, baselineExposureScore, baselineVulnScore);
  const baselineLst = bHaz.lst_anomaly_c ?? 3.0;
  const totalPop = zone.population || 50000;

  const currencyRate = city?.currency?.rate_per_usd || 1.0;
  const currencySymbol = city?.currency?.symbol || '$';

  let simHazardScore = baselineHazardScore;
  let simExposureScore = baselineExposureScore;
  let simVulnScore = baselineVulnScore;
  let simLstAnomaly = baselineLst;

  let totalCostUsd = 0.0;
  const interventionBreakdown = [];
  const explanationNotes = [];

  let varianceAccum = 0.0;
  let coolingCenterProtected = 0;
  let directCoolingProtected = 0;

  for (const [itemId, rawIntensity] of Object.entries(interventions)) {
    const intensity = Number(rawIntensity) || 0;
    if (intensity <= 0 || !catalogMap[itemId]) continue;

    const item = catalogMap[itemId];
    const unitCostUsd = item.cost_per_unit_usd || 0;
    const itemCostUsd = unitCostUsd * intensity;
    totalCostUsd += itemCostUsd;
    const itemCostLocal = itemCostUsd * currencyRate;

    let lstDrop = 0.0;
    if (itemId === 'cooling_centers') {
      lstDrop = 0.0;
      const expFactor = 1.0 - Math.exp(-0.06 * intensity);
      const expDrop = baselineExposureScore * (item.exposure_reduction_multiplier || 0.40) * expFactor;
      const vulnDrop = baselineVulnScore * (item.vulnerability_reduction_multiplier || 0.35) * expFactor;

      simExposureScore = Math.max(10.0, simExposureScore - expDrop);
      simVulnScore = Math.max(10.0, simVulnScore - vulnDrop);

      const peopleCapacity = Math.floor(intensity * 3200);
      coolingCenterProtected += peopleCapacity;

      explanationNotes.push(
        `Cooling Hubs (${intensity.toFixed(0)} units): Reduced human exposure hours by ~${expDrop.toFixed(1)} pts ` +
        `and vulnerable population shielding by ${vulnDrop.toFixed(1)} pts. ` +
        `[NOTE: Zero impact on outdoor surface temperature; serves strictly as an exposure refuge].`
      );
    } else {
      lstDrop = (item.lst_reduction_per_unit_c || 0.05) * intensity;
      lstDrop = Math.min(4.5, lstDrop);

      const hazDrop = baselineHazardScore * (item.hazard_reduction_multiplier || 0.2) * (intensity / 100.0);
      const expDrop = baselineExposureScore * (item.exposure_reduction_multiplier || 0.05) * (intensity / 100.0);
      const vulnDrop = baselineVulnScore * (item.vulnerability_reduction_multiplier || 0.1) * (intensity / 100.0);

      simLstAnomaly = Math.max(0.5, simLstAnomaly - lstDrop);
      simHazardScore = Math.max(12.0, simHazardScore - hazDrop);
      simExposureScore = Math.max(12.0, simExposureScore - expDrop);
      simVulnScore = Math.max(12.0, simVulnScore - vulnDrop);

      const shelteredPop = Math.floor(totalPop * (intensity / 100.0) * 0.45);
      directCoolingProtected += shelteredPop;

      explanationNotes.push(
        `${item.name} (${intensity.toFixed(1)} ${item.unit}): Mitigated land surface temp anomaly by ` +
        `-${lstDrop.toFixed(2)}°C, lowering zone hazard index by ${hazDrop.toFixed(1)} pts.`
      );
    }

    const sigma = item.uncertainty_sigma || 0.15;
    varianceAccum += Math.pow(sigma * itemCostUsd, 2);

    interventionBreakdown.push({
      id: itemId,
      name: item.name,
      intensity: intensity,
      unit: item.unit,
      cost_usd: Math.round(itemCostUsd * 100) / 100,
      cost_local: Math.round(itemCostLocal * 100) / 100,
      currency_symbol: currencySymbol,
      lst_delta_c: itemId !== 'cooling_centers' ? -Math.round(lstDrop * 100) / 100 : 0.0,
      reduces_surface_temp: item.reduces_surface_temp
    });
  }

  simHazardScore = Math.round(simHazardScore * 10) / 10;
  simExposureScore = Math.round(simExposureScore * 10) / 10;
  simVulnScore = Math.round(simVulnScore * 10) / 10;
  simLstAnomaly = Math.round(simLstAnomaly * 100) / 100;

  const simRisk = calculateCompositeRisk(simHazardScore, simExposureScore, simVulnScore);
  const riskDelta = Math.round((baselineRisk - simRisk) * 10) / 10;
  const riskReductionPct = baselineRisk > 0 ? Math.round((riskDelta / baselineRisk * 100.0) * 10) / 10 : 0.0;
  const lstReductionC = Math.round((baselineLst - simLstAnomaly) * 100) / 100;

  let combinedProtected = Math.floor(Math.min(totalPop, directCoolingProtected + coolingCenterProtected));
  if (riskDelta <= 0) {
    combinedProtected = 0;
  }

  let relStd = totalCostUsd > 0 ? Math.sqrt(varianceAccum) / (totalCostUsd + 1e-6) : 0.15;
  relStd = Math.max(0.10, Math.min(0.28, relStd));
  const lowDelta = Math.round(Math.max(0.0, riskDelta * (1.0 - 1.645 * relStd)) * 10) / 10;
  const highDelta = Math.round((riskDelta * (1.0 + 1.645 * relStd)) * 10) / 10;

  return {
    zone_id: zone.id,
    zone_name: zone.name,
    city_name: city?.name || "Global Metro",
    currency_symbol: currencySymbol,
    baseline: {
      hazard_score: baselineHazardScore,
      exposure_score: baselineExposureScore,
      vulnerability_score: baselineVulnScore,
      composite_risk: baselineRisk,
      lst_anomaly_c: baselineLst,
      effective_exposure_pop: bExp.effective_pop_exposed || Math.floor(totalPop * 0.4)
    },
    simulated: {
      hazard_score: simHazardScore,
      exposure_score: simExposureScore,
      vulnerability_score: simVulnScore,
      composite_risk: simRisk,
      lst_anomaly_c: simLstAnomaly,
      effective_exposure_pop: Math.max(0, (bExp.effective_pop_exposed || Math.floor(totalPop * 0.4)) - combinedProtected)
    },
    risk_delta: riskDelta,
    risk_reduction_pct: riskReductionPct,
    lst_reduction_c: lstReductionC,
    people_protected: combinedProtected,
    estimated_cost_local: Math.round(totalCostUsd * currencyRate * 100) / 100,
    estimated_cost_usd: Math.round(totalCostUsd * 100) / 100,
    uncertainty: {
      low: lowDelta,
      expected: riskDelta,
      high: highDelta,
      confidence_level: "90% CI"
    },
    intervention_breakdown: interventionBreakdown,
    explanation_notes: explanationNotes
  };
}

