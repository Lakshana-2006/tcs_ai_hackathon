import math
from typing import Dict, Any, List, Optional
from app.data import ZONES_DATA, INTERVENTIONS_CATALOG, WEIGHTS
from app.models import FactorBreakdown, SimulationResult, UncertaintyBounds


def calculate_composite_risk(hazard: float, exposure: float, vulnerability: float) -> float:
    """
    Explainable baseline risk score formula:
    Risk = w_hazard * Hazard + w_exposure * Exposure + w_vulnerability * Vulnerability
    Where weights are:
      w_hazard = 0.35
      w_exposure = 0.30
      w_vulnerability = 0.35
    Normalized between 0.0 and 100.0.
    """
    raw_risk = (
        WEIGHTS["w_hazard"] * hazard +
        WEIGHTS["w_exposure"] * exposure +
        WEIGHTS["w_vulnerability"] * vulnerability
    )
    return round(max(0.0, min(100.0, raw_risk)), 1)


def simulate_zone_interventions(
    zone_id: str,
    interventions: Dict[str, float],
    zone_data: Optional[Dict[str, Any]] = None,
    city_name: str = "Global Metro",
    currency_symbol: str = "$",
    currency_rate: float = 1.0
) -> SimulationResult:
    """
    Simulates the physical, social, and demographic impact of selected interventions on a specific zone.
    Strictly observes domain mechanics:
    - Cooling Centers ONLY mitigate human exposure and social vulnerability,
      having ZERO claim on Land Surface Temperature (LST).
    - Cool roofs and tree planting reduce LST and hazard scores.
    """
    # Prefer dynamically provided zone data, fallback to static cache
    zone = zone_data or ZONES_DATA.get(zone_id)
    if not zone:
        raise ValueError(f"Zone '{zone_id}' not found in active city digital twin.")

    b_haz = zone["baseline_hazard"]
    b_exp = zone["baseline_exposure"]
    b_vul = zone["baseline_vulnerability"]

    baseline_hazard_score = b_haz["hazard_score"]
    baseline_exposure_score = b_exp["exposure_score"]
    baseline_vuln_score = b_vul["vulnerability_score"]
    baseline_risk = calculate_composite_risk(baseline_hazard_score, baseline_exposure_score, baseline_vuln_score)
    baseline_lst = b_haz["lst_anomaly_c"]
    total_pop = zone["population"]

    # Initialize simulation accumulators
    sim_hazard_score = baseline_hazard_score
    sim_exposure_score = baseline_exposure_score
    sim_vuln_score = baseline_vuln_score
    sim_lst_anomaly = baseline_lst

    total_cost_usd = 0.0
    intervention_breakdown: List[Dict[str, Any]] = []
    explanation_notes: List[str] = []

    variance_accum = 0.0
    cooling_center_protected = 0
    direct_cooling_protected = 0

    for item_id, intensity in interventions.items():
        if intensity <= 0.0 or item_id not in INTERVENTIONS_CATALOG:
            continue

        item = INTERVENTIONS_CATALOG[item_id]
        unit_cost_usd = item["cost_per_unit_usd"]
        item_cost_usd = unit_cost_usd * intensity
        total_cost_usd += item_cost_usd

        item_cost_local = item_cost_usd * currency_rate

        # Specific Logic for Cooling Centers
        if item_id == "cooling_centers":
            # Rule: ZERO effect on Land Surface Temperature (LST) and Meteorological Hazard
            lst_drop = 0.0
            haz_reduction = 0.0

            # Direct reduction in Human Exposure and AC Vulnerability Deficit
            exp_factor = 1.0 - math.exp(-0.06 * intensity)
            exp_drop = baseline_exposure_score * item["exposure_reduction_multiplier"] * exp_factor
            vuln_drop = baseline_vuln_score * item["vulnerability_reduction_multiplier"] * exp_factor

            sim_exposure_score = max(10.0, sim_exposure_score - exp_drop)
            sim_vuln_score = max(10.0, sim_vuln_score - vuln_drop)

            people_capacity = int(intensity * 3200) # Each hub shelters/protects ~3,200 vulnerable individuals
            cooling_center_protected += people_capacity

            explanation_notes.append(
                f"Cooling Hubs ({intensity:.0f} units): Reduced human exposure hours by ~{exp_drop:.1f} pts "
                f"and vulnerable population shielding by {vuln_drop:.1f} pts. "
                f"[NOTE: Zero impact on outdoor surface temperature; serves strictly as an exposure refuge]."
            )
        else:
            # Physical interventions that attenuate surface thermal radiation
            lst_drop = item["lst_reduction_per_unit_c"] * intensity
            lst_drop = min(4.5, lst_drop) # Cap maximum physical cooling

            # Hazard reduction scales with LST drop
            haz_drop = baseline_hazard_score * item["hazard_reduction_multiplier"] * (intensity / 100.0)
            exp_drop = baseline_exposure_score * item["exposure_reduction_multiplier"] * (intensity / 100.0)
            vuln_drop = baseline_vuln_score * item["vulnerability_reduction_multiplier"] * (intensity / 100.0)

            sim_lst_anomaly = max(0.5, sim_lst_anomaly - lst_drop)
            sim_hazard_score = max(12.0, sim_hazard_score - haz_drop)
            sim_exposure_score = max(12.0, sim_exposure_score - exp_drop)
            sim_vuln_score = max(12.0, sim_vuln_score - vuln_drop)

            sheltered_pop = int(total_pop * (intensity / 100.0) * 0.45)
            direct_cooling_protected += sheltered_pop

            explanation_notes.append(
                f"{item['name']} ({intensity:.1f} {item['unit']}): Mitigated land surface temp anomaly by "
                f"-{lst_drop:.2f}°C, lowering zone hazard index by {haz_drop:.1f} pts."
            )

        # Variance accumulation for 90% confidence interval
        sigma = item["uncertainty_sigma"]
        variance_accum += (sigma * item_cost_usd) ** 2

        intervention_breakdown.append({
            "id": item_id,
            "name": item["name"],
            "intensity": intensity,
            "unit": item["unit"],
            "cost_usd": round(item_cost_usd, 2),
            "cost_local": round(item_cost_local, 2),
            "currency_symbol": currency_symbol,
            "lst_delta_c": -round(lst_drop, 2) if item_id != "cooling_centers" else 0.0,
            "reduces_surface_temp": item["reduces_surface_temp"]
        })

    # Final simulated scores
    sim_hazard_score = round(sim_hazard_score, 1)
    sim_exposure_score = round(sim_exposure_score, 1)
    sim_vuln_score = round(sim_vuln_score, 1)
    sim_lst_anomaly = round(sim_lst_anomaly, 2)

    sim_risk = calculate_composite_risk(sim_hazard_score, sim_exposure_score, sim_vuln_score)
    risk_delta = round(baseline_risk - sim_risk, 1)
    risk_reduction_pct = round((risk_delta / baseline_risk * 100.0) if baseline_risk > 0 else 0.0, 1)
    lst_reduction_c = round(baseline_lst - sim_lst_anomaly, 2)

    combined_protected = int(min(total_pop, direct_cooling_protected + cooling_center_protected))
    if risk_delta <= 0:
        combined_protected = 0

    # Uncertainty calculations (90% Confidence Interval)
    rel_std = math.sqrt(variance_accum) / (total_cost_usd + 1e-6) if total_cost_usd > 0 else 0.15
    rel_std = max(0.10, min(0.28, rel_std))
    low_delta = round(max(0.0, risk_delta * (1.0 - 1.645 * rel_std)), 1)
    high_delta = round(risk_delta * (1.0 + 1.645 * rel_std), 1)

    uncertainty = UncertaintyBounds(
        low=low_delta,
        expected=risk_delta,
        high=high_delta,
        confidence_level="90% Confidence Interval (±1.645σ)"
    )

    baseline_breakdown = FactorBreakdown(
        hazard_score=baseline_hazard_score,
        exposure_score=baseline_exposure_score,
        vulnerability_score=baseline_vuln_score,
        composite_risk=baseline_risk,
        lst_anomaly_c=baseline_lst,
        effective_exposure_pop=int(total_pop * (baseline_exposure_score / 100.0))
    )

    simulated_breakdown = FactorBreakdown(
        hazard_score=sim_hazard_score,
        exposure_score=sim_exposure_score,
        vulnerability_score=sim_vuln_score,
        composite_risk=sim_risk,
        lst_anomaly_c=sim_lst_anomaly,
        effective_exposure_pop=int(total_pop * (sim_exposure_score / 100.0))
    )

    if not explanation_notes:
        explanation_notes.append("No active interventions configured for this scenario. Showing unmitigated baseline.")

    total_cost_local = total_cost_usd * currency_rate

    return SimulationResult(
        zone_id=zone_id,
        zone_name=zone["name"],
        city_name=city_name,
        currency_symbol=currency_symbol,
        baseline=baseline_breakdown,
        simulated=simulated_breakdown,
        risk_delta=risk_delta,
        risk_reduction_pct=risk_reduction_pct,
        lst_reduction_c=lst_reduction_c,
        people_protected=combined_protected,
        estimated_cost_usd=round(total_cost_usd, 2),
        estimated_cost_local=round(total_cost_local, 2),
        uncertainty=uncertainty,
        intervention_breakdown=intervention_breakdown,
        explanation_notes=explanation_notes
    )
