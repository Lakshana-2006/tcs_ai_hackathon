from typing import Dict, Any, List
from app.data import ZONES_DATA, INTERVENTIONS_CATALOG, WEIGHTS
from app.models import OptimizeRequest, OptimizationResponse, AllocatedIntervention
from app.simulation import simulate_zone_interventions, calculate_composite_risk


def optimize_budget_allocation(request: OptimizeRequest) -> OptimizationResponse:
    """
    Greedy marginal cost-effectiveness multi-criteria optimizer with equity constraints.
    Currency-aware and dynamic zone compatible for any global city.
    """
    rate = request.currency_rate if request.currency_rate > 0 else 1.0
    budget_local = request.total_budget_local
    budget_usd = budget_local / rate
    use_equity = request.equity_weighting
    objective = request.focus_objective
    curr_sym = request.currency_symbol

    # Use dynamic zones if provided, otherwise default fallback zones
    zones_list = request.zones if request.zones and len(request.zones) > 0 else list(ZONES_DATA.values())
    zones_dict = {z["id"]: z for z in zones_list}

    candidates: List[Dict[str, Any]] = []

    for zone in zones_list:
        zid = zone["id"]
        svi = zone["baseline_vulnerability"]["svi_score"]
        pop = zone["population"]

        # Equity weighting multiplier: up to 1.85x boost for high SVI/elderly zones
        equity_mult = 1.0 + (svi / 100.0) * 0.85 if use_equity else 1.0
        priorities = zone.get("recommended_priorities", ["cool_roofs", "tree_planting", "cooling_centers"])

        for item_id in priorities:
            if item_id not in INTERVENTIONS_CATALOG:
                continue
            item = INTERVENTIONS_CATALOG[item_id]
            cost_per_unit_usd = item["cost_per_unit_usd"]

            if item_id == "cooling_centers":
                slices = [2.0, 4.0, 6.0]
            elif item_id == "green_corridors":
                slices = [3.0, 6.0, 10.0]
            else:
                slices = [15.0, 30.0, 45.0]

            for intensity in slices:
                cost_usd = cost_per_unit_usd * intensity
                cost_local = cost_usd * rate
                if cost_usd > budget_usd:
                    continue

                # Estimate simulated impact for this single slice
                test_sim = simulate_zone_interventions(
                    zone_id=zid,
                    interventions={item_id: intensity},
                    zone_data=zone,
                    city_name=request.city_name,
                    currency_symbol=curr_sym,
                    currency_rate=rate
                )
                risk_reduction = test_sim.risk_delta
                protected = test_sim.people_protected
                lst_mitigation = test_sim.lst_reduction_c

                if objective == "max_people":
                    raw_benefit = protected
                elif objective == "max_cooling":
                    raw_benefit = lst_mitigation * pop * 0.05 + risk_reduction * 500
                else: # balanced
                    raw_benefit = (risk_reduction * 1000) + (protected * 0.08)

                weighted_benefit = raw_benefit * equity_mult
                benefit_per_dollar = weighted_benefit / (cost_usd + 1e-4)

                why_text = (
                    f"Selected for {zone.get('short_name', zone['name'])}: "
                    f"{'Equity-boosted (SVI ' + str(svi) + ') ' if use_equity and svi > 60 else ''}"
                    f"Reduces composite risk by -{risk_reduction:.1f} pts, protecting ~{protected:,} citizens "
                    f"at {curr_sym}{cost_local:,.0f}."
                )

                candidates.append({
                    "zone_id": zid,
                    "zone_name": zone["name"],
                    "short_name": zone.get("short_name", zone["name"]),
                    "intervention_id": item_id,
                    "intervention_name": item["name"],
                    "intensity": intensity,
                    "unit": item["unit"],
                    "cost_usd": cost_usd,
                    "cost_local": cost_local,
                    "risk_reduction": risk_reduction,
                    "people_protected": protected,
                    "lst_mitigation": lst_mitigation,
                    "efficiency": benefit_per_dollar,
                    "why_text": why_text,
                    "svi": svi
                })

    candidates.sort(key=lambda x: x["efficiency"], reverse=True)

    allocated_by_zone: Dict[str, List[AllocatedIntervention]] = {z["id"]: [] for z in zones_list}
    zone_chosen_types: Dict[str, set] = {z["id"]: set() for z in zones_list}
    zone_final_interventions: Dict[str, Dict[str, float]] = {z["id"]: {} for z in zones_list}

    spent_usd = 0.0
    for cand in candidates:
        zid = cand["zone_id"]
        iid = cand["intervention_id"]

        if iid in zone_chosen_types[zid]:
            continue
        if spent_usd + cand["cost_usd"] > budget_usd:
            continue

        spent_usd += cand["cost_usd"]
        zone_chosen_types[zid].add(iid)
        zone_final_interventions[zid][iid] = cand["intensity"]

        allocated_by_zone[zid].append(AllocatedIntervention(
            zone_id=zid,
            zone_name=cand["zone_name"],
            intervention_id=iid,
            intervention_name=cand["intervention_name"],
            intensity=cand["intensity"],
            unit=cand["unit"],
            cost_local=round(cand["cost_local"], 2),
            cost_usd=round(cand["cost_usd"], 2),
            risk_reduction_points=cand["risk_reduction"],
            people_protected=cand["people_protected"],
            why_prioritized=cand["why_text"]
        ))

    zone_summaries: List[Dict[str, Any]] = []
    total_protected = 0
    before_risk_sum = 0.0
    after_risk_sum = 0.0

    for zone in zones_list:
        zid = zone["id"]
        sim_res = simulate_zone_interventions(
            zone_id=zid,
            interventions=zone_final_interventions[zid],
            zone_data=zone,
            city_name=request.city_name,
            currency_symbol=curr_sym,
            currency_rate=rate
        )
        total_protected += sim_res.people_protected
        before_risk_sum += sim_res.baseline.composite_risk
        after_risk_sum += sim_res.simulated.composite_risk

        zone_summaries.append({
            "zone_id": zid,
            "zone_name": zone["name"],
            "short_name": zone.get("short_name", zone["name"]),
            "baseline_risk": sim_res.baseline.composite_risk,
            "simulated_risk": sim_res.simulated.composite_risk,
            "risk_reduction_pct": sim_res.risk_reduction_pct,
            "lst_reduction_c": sim_res.lst_reduction_c,
            "people_protected": sim_res.people_protected,
            "cost_allocated_local": sim_res.estimated_cost_local,
            "cost_allocated_usd": sim_res.estimated_cost_usd,
            "interventions_count": len(allocated_by_zone[zid]),
            "uncertainty": sim_res.uncertainty.model_dump()
        })

    count = len(zones_list)
    avg_before_risk = round(before_risk_sum / count, 1) if count else 0.0
    avg_after_risk = round(after_risk_sum / count, 1) if count else 0.0
    avg_reduction_pct = round(((avg_before_risk - avg_after_risk) / avg_before_risk * 100.0) if avg_before_risk > 0 else 0.0, 1)

    spent_local = spent_usd * rate

    prioritization_rationale = [
        f"1. {request.city_name} Historic/High-Vulnerability districts received front-line investment based on Social Vulnerability Index and lack of mechanical AC.",
        f"2. Emergency Cooling Hubs were deployed to provide immediate thermal haven for seniors and outdoor laborers without unscientific claims of altering outdoor satellite LST.",
        f"3. Industrial corridors received cool roof reflective coatings to counteract daytime solar storage and night-time heat trapping.",
        f"4. Pedestrian corridors and transit stops were prioritized for shaded canopy and misting networks along primary commuter routes.",
        f"5. Low-vulnerability suburban/greenbelt zones received minimal capital outlay, preserving funds for high-hazard frontline neighborhoods."
    ]

    return OptimizationResponse(
        city_name=request.city_name,
        currency_code=request.currency_code,
        currency_symbol=curr_sym,
        total_budget_local=round(budget_local, 2),
        budget_utilized_local=round(spent_local, 2),
        budget_remaining_local=round(budget_local - spent_local, 2),
        total_budget_usd=round(budget_usd, 2),
        budget_utilized_usd=round(spent_usd, 2),
        equity_weighting_applied=use_equity,
        total_people_protected=total_protected,
        city_average_risk_before=avg_before_risk,
        city_average_risk_after=avg_after_risk,
        risk_reduction_pct=avg_reduction_pct,
        allocations_by_zone=allocated_by_zone,
        zone_summaries=zone_summaries,
        prioritization_rationale=prioritization_rationale,
        synthetic_notice="DEMO PROTOTYPE ONLY: Costs, allocations, and impact metrics are illustrative synthetic models for hackathon prototype decision-support."
    )
