import os
import json
import logging
from typing import Dict, Any, List, Optional
import httpx
from app.models import ChatRequest, ChatResponse, ChatMessage

logger = logging.getLogger(__name__)


def build_system_context_prompt(context: Optional[Any]) -> str:
    """
    Constructs a detailed, ground-truth context block from the live dashboard telemetry.
    Ensures the assistant has exact data for city, weather, 5 zones, active zone,
    and current simulation results.
    """
    if not context:
        return "No real-time dashboard context was provided. State that city/zone telemetry is not loaded."

    ctx_dict = context if isinstance(context, dict) else context.model_dump()

    city = ctx_dict.get("city") or {}
    weather = ctx_dict.get("weather") or {}
    zones = ctx_dict.get("zones") or []
    selected_zone = ctx_dict.get("selected_zone") or {}
    selected_interventions = ctx_dict.get("selected_interventions") or {}
    sim_result = ctx_dict.get("simulation_result") or {}

    city_name = city.get("name", "Unknown City")
    country = city.get("country", "")
    curr_sym = city.get("currency", {}).get("symbol", "$")
    curr_code = city.get("currency", {}).get("code", "USD")

    # Format Weather
    air_temp = weather.get("air_temperature_c", "N/A")
    app_temp = weather.get("apparent_temperature_c", "N/A")
    humidity = weather.get("relative_humidity_pct", "N/A")
    condition = weather.get("condition", "N/A")
    weather_source = weather.get("data_source", "Open-Meteo")

    # Format 5 Zones
    zones_summary = []
    highest_risk_zone = None
    max_risk = -1.0

    for z in zones:
        z_name = z.get("name", "Zone")
        z_risk = z.get("baseline_risk", 0.0)
        z_pop = z.get("population", 0)
        b_haz = z.get("baseline_hazard", {}).get("hazard_score", "N/A")
        b_exp = z.get("baseline_exposure", {}).get("exposure_score", "N/A")
        b_vul = z.get("baseline_vulnerability", {}).get("vulnerability_score", "N/A")
        zones_summary.append(
            f"  - {z_name} (ID: {z.get('id')}): Composite Risk = {z_risk}/100 | "
            f"Hazard = {b_haz}, Exposure = {b_exp}, Vulnerability = {b_vul} | Population: {z_pop:,}"
        )
        if isinstance(z_risk, (int, float)) and z_risk > max_risk:
            max_risk = z_risk
            highest_risk_zone = z_name

    zones_text = "\n".join(zones_summary) if zones_summary else "  No zone details available."

    # Format Selected Active Zone
    sel_name = selected_zone.get("name", "None selected")
    sel_risk = selected_zone.get("baseline_risk", "N/A")
    sel_pop = selected_zone.get("population", "N/A")
    sel_desc = selected_zone.get("description", "")
    sel_priorities = selected_zone.get("recommended_priorities", [])
    
    b_haz_sel = selected_zone.get("baseline_hazard", {})
    b_exp_sel = selected_zone.get("baseline_exposure", {})
    b_vul_sel = selected_zone.get("baseline_vulnerability", {})

    # Format Simulation
    sim_text = "No interventions currently simulated."
    if sim_result and sim_result.get("risk_delta", 0) > 0:
        sim_text = (
            f"Active Simulation on {sim_result.get('zone_name', sel_name)}:\n"
            f"  - Risk Delta: -{sim_result.get('risk_delta')} pts ({sim_result.get('risk_reduction_pct')}% reduction)\n"
            f"  - Surface Cooling (LST): -{sim_result.get('lst_reduction_c')}°C drop\n"
            f"  - People Protected: {sim_result.get('people_protected', 0):,}\n"
            f"  - Estimated Cost: {curr_sym}{sim_result.get('estimated_cost_local', 0):,.0f} ({curr_code}) / "
            f"${sim_result.get('estimated_cost_usd', 0):,.0f} USD\n"
            f"  - 90% Confidence Interval: Low: -{sim_result.get('uncertainty', {}).get('low', 'N/A')} pts, "
            f"Expected: -{sim_result.get('uncertainty', {}).get('expected', 'N/A')} pts, "
            f"High: -{sim_result.get('uncertainty', {}).get('high', 'N/A')} pts"
        )
    elif selected_interventions and any(v > 0 for v in selected_interventions.values()):
        active_levers = [f"{k}: {v}" for k, v in selected_interventions.items() if v > 0]
        sim_text = f"Configured Levers: {', '.join(active_levers)}"

    prompt = f"""You are the HEATSHIELD AI Assistant, an expert urban climate resilience advisor for the HEATSHIELD AI Digital Twin.
You help municipal planners, emergency managers, urban resilience officers, and citizens understand urban heat islands, interpret IPCC risk scores, and evaluate climate interventions.

CURRENT LIVE DASHBOARD TELEMETRY:
==================================
City Context:
• City: {city_name}, {country}
• Currency: {curr_code} ({curr_sym})
• Live Weather ({weather_source}): Air Temp: {air_temp}°C | Apparent/Heat Index: {app_temp}°C | Humidity: {humidity}% | Condition: {condition}

City's 5 Analysis Zones:
• Highest Risk Zone: {highest_risk_zone} (Risk: {max_risk}/100)
{zones_text}

Currently Selected Zone:
• Name: {sel_name}
• Composite Baseline Risk: {sel_risk}/100
• Population: {sel_pop}
• Hazard Breakdown: Score {b_haz_sel.get('hazard_score', 'N/A')} | LST Anomaly: +{b_haz_sel.get('lst_anomaly_c', 'N/A')}°C | Tree Canopy: {b_haz_sel.get('tree_canopy_pct', 'N/A')}% | Impervious Surface: {b_haz_sel.get('impervious_surface_pct', 'N/A')}%
• Exposure Breakdown: Score {b_exp_sel.get('exposure_score', 'N/A')} | Pop Density: {b_exp_sel.get('pop_density_per_km2', 'N/A')}/km² | Outdoor Workers: {b_exp_sel.get('outdoor_labor_ratio', 'N/A')}%
• Vulnerability Breakdown: Score {b_vul_sel.get('vulnerability_score', 'N/A')} | SVI: {b_vul_sel.get('social_vulnerability_index', 'N/A')} | AC Deficit: {b_vul_sel.get('lack_of_ac_pct', 'N/A')}% | Seniors (65+): {b_vul_sel.get('elderly_pct', 'N/A')}%
• Context: {sel_desc}
• Tailored Priorities: {', '.join(sel_priorities) if sel_priorities else 'General heat mitigation'}

Current What-If Intervention Simulator Results:
{sim_text}

MANDATORY RESPONSE GUIDELINES:
1. Ground every claim directly in the telemetry above. NEVER invent temperatures, populations, risk scores, or intervention outputs.
2. If the user asks about something not present in the data, state clearly that the specific information is unavailable in the current telemetry snapshot.
3. Observe biophysical reality strictly: Emergency Resilient Cooling Hubs shelter people and reduce exposure/vulnerability hours (preventing heat stroke); they do NOT alter outdoor Land Surface Temperature (LST). Cool Roofs and Urban Canopy (tree planting) reduce physical surface LST and meteorological hazard.
4. Keep responses structured, concise, friendly, and actionable for decision-makers. Use clear markdown formatting (bolding, bullet points).
"""
    return prompt


def generate_unconfigured_response(context: Optional[Any]) -> ChatResponse:
    """
    Returns a friendly setup response when no AI API key is configured in the environment.
    Does NOT pretend an LLM response was generated.
    """
    ctx_dict = context if isinstance(context, dict) else (context.model_dump() if context else {})
    city_name = ctx_dict.get("city", {}).get("name", "the selected city")
    weather = ctx_dict.get("weather", {})
    air_temp = weather.get("air_temperature_c")
    sel_zone = ctx_dict.get("selected_zone", {})
    zone_name = sel_zone.get("name", "selected zone")
    zone_risk = sel_zone.get("baseline_risk", "N/A")
    sim = ctx_dict.get("simulation_result") or {}

    weather_str = f" ({air_temp}°C live weather)" if air_temp is not None else ""
    sim_str = (
        f"-{sim.get('risk_delta')} pts risk reduction modeled"
        if sim.get("risk_delta", 0) > 0
        else "no active interventions"
    )

    reply = (
        "### ⚠️ AI Provider Setup Required\n\n"
        "The **HEATSHIELD AI Assistant** backend is fully operational and connected to live digital twin telemetry, "
        "but no AI API key was found in the server environment.\n\n"
        "#### Quick Setup Steps:\n"
        "1. Open or create the `.env` file in the `backend/` directory.\n"
        "2. Add your preferred AI provider API key:\n"
        "   ```bash\n"
        "   # Google Gemini API Key (Recommended)\n"
        "   GEMINI_API_KEY=your_gemini_api_key_here\n\n"
        "   # Or OpenAI API Key\n"
        "   OPENAI_API_KEY=your_openai_api_key_here\n"
        "   ```\n"
        "3. Restart the backend server.\n\n"
        f"#### Current Live Telemetry Context (Ready):\n"
        f"• **Active City**: {city_name}{weather_str}\n"
        f"• **Selected Zone**: {zone_name} (Composite Risk: **{zone_risk}/100**)\n"
        f"• **Intervention Simulator**: {sim_str}\n\n"
        "_Once an API key is provided, the assistant will immediately provide real-time, data-grounded insights, "
        "biophysical recommendations, and zone risk explainability._"
    )

    setup_instructions = (
        "Create backend/.env with GEMINI_API_KEY=your_key or OPENAI_API_KEY=your_key and restart the server."
    )

    return ChatResponse(
        reply=reply,
        is_configured=False,
        provider=None,
        setup_instructions=setup_instructions,
        context_used={
            "city": city_name,
            "zone": zone_name,
            "risk_score": zone_risk
        }
    )


def call_gemini_api(api_key: str, system_prompt: str, history: List[ChatMessage], user_message: str) -> str:
    """
    Calls the Google Gemini REST API using httpx with the full dashboard context.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    # Build conversation contents
    contents = []

    # First turn includes system prompt and context
    first_user_text = f"{system_prompt}\n\n---\nUser Query: {user_message}" if not history else system_prompt

    if history:
        contents.append({"role": "user", "parts": [{"text": system_prompt}]})
        contents.append({"role": "model", "parts": [{"text": "Understood. I am initialized with the live HEATSHIELD AI dashboard telemetry. How can I assist you with urban heat resilience?"}]})
        
        for msg in history[-8:]:  # Keep recent context window
            role = "user" if msg.role == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg.content}]})

        contents.append({"role": "user", "parts": [{"text": user_message}]})
    else:
        contents.append({"role": "user", "parts": [{"text": first_user_text}]})

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1000
        }
    }

    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        data = response.json()
        
        candidates = data.get("candidates", [])
        if not candidates:
            return "I was unable to generate a response from the AI provider. Please try again."
        
        parts = candidates[0].get("content", {}).get("parts", [])
        if parts and "text" in parts[0]:
            return parts[0]["text"]
        
        return "Empty response received from AI model."


def call_openai_api(api_key: str, system_prompt: str, history: List[ChatMessage], user_message: str) -> str:
    """
    Calls the OpenAI Chat Completions API using httpx with the full dashboard context.
    """
    url = "https://api.openai.com/v1/chat/completions"

    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-8:]:
        role = "user" if msg.role == "user" else "assistant"
        messages.append({"role": role, "content": msg.content})
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 1000
    }

    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            url, 
            json=payload, 
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        )
        response.raise_for_status()
        data = response.json()
        choices = data.get("choices", [])
        if choices and "message" in choices[0]:
            return choices[0]["message"].get("content", "")
        return "No text received from OpenAI model."


def handle_chat_request(request: ChatRequest) -> ChatResponse:
    """
    Main entry point for processing AI chat assistant requests.
    Validates message, inspects API key presence, calls provider or returns setup instructions.
    """
    user_msg = request.message.strip() if request.message else ""
    if not user_msg:
        raise ValueError("Message cannot be empty.")

    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()

    # If no provider is configured, return the friendly setup message with real telemetry summary
    if not gemini_key and not openai_key:
        return generate_unconfigured_response(request.context)

    system_prompt = build_system_context_prompt(request.context)

    try:
        if gemini_key:
            reply = call_gemini_api(gemini_key, system_prompt, request.conversation_history, user_msg)
            provider = "gemini"
        elif openai_key:
            reply = call_openai_api(openai_key, system_prompt, request.conversation_history, user_msg)
            provider = "openai"
        else:
            return generate_unconfigured_response(request.context)

        return ChatResponse(
            reply=reply,
            is_configured=True,
            provider=provider,
            setup_instructions=None,
            context_used={
                "city": request.context.city.get("name") if request.context and request.context.city else None,
                "zone": request.context.selected_zone.get("name") if request.context and request.context.selected_zone else None
            }
        )
    except httpx.TimeoutException:
        logger.error("AI service timed out.")
        return ChatResponse(
            reply="The AI service request timed out while generating an answer. Please verify your network connection and try again.",
            is_configured=True,
            provider="unknown",
            setup_instructions="Check network latency to AI provider API endpoints."
        )
    except Exception as e:
        logger.error(f"AI API request failed: {e}", exc_info=True)
        return ChatResponse(
            reply=f"AI service encounter an issue: {str(e)}. Please check your backend API key configuration.",
            is_configured=True,
            provider="unknown",
            setup_instructions="Verify that your GEMINI_API_KEY or OPENAI_API_KEY is valid and has sufficient quota."
        )

