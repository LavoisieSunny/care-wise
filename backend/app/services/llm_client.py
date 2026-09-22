import json
import re
from typing import Optional, Dict, Any, List
import httpx

from app.core.config import settings
from app.core.logging import logger

EXTRACTION_SYSTEM_PROMPT = """You are an expert health insurance policy analyst.
Your task is to parse the extracted policy text and return a structured JSON representation of the key insurance coverage parameters.

Return ONLY a valid JSON object matching this exact schema:
{
  "sum_insured": 500000.0,
  "room_limit": {
    "capped_amount_per_day": 5000.0,
    "percentage_of_sum_insured": 1.0,
    "no_room_rent_capping": false,
    "allowed_room_category": "Standard Single Room",
    "proportionate_deduction_applies": true,
    "page": 1,
    "quote": "Room rent is limited to 1% of Sum Insured per day...",
    "confidence": 0.95
  },
  "icu_limit_per_day": 10000.0,
  "copay": {
    "standard_percentage": 0.0,
    "senior_citizen_percentage": 20.0,
    "zone_based_copay": 0.0,
    "page": 2,
    "quote": "Co-payment of 20% applies for senior citizens...",
    "confidence": 0.95
  },
  "pre_auth": {
    "emergency_window_hours": 24,
    "planned_window_hours": 48,
    "page": 3,
    "quote": "Emergency admission pre-auth must be submitted within 24 hours...",
    "confidence": 0.95
  },
  "has_consumables_rider": false,
  "empanelled_tpas": ["Medi Assist", "Vidal Health"],
  "waiting_periods": [
    {
      "type": "Initial Waiting Period",
      "duration": "30 Days",
      "description": "General illness covered after 30 days.",
      "page": 1,
      "confidence": 0.9
    }
  ],
  "key_exclusions": [
    "Non-medical disposable items",
    "Cosmetic treatments"
  ]
}

CRITICAL RULES:
1. For every clause field (room_limit, copay, pre_auth, waiting_periods), you MUST return the exact page number (1-indexed, derived from '--- Page X ---' headers) and the exact quoted sentence from the text.
2. If a field is not found, provide best standard estimates and indicate confidence < 0.70.
3. Return ONLY the raw JSON object, without commentary or markdown code blocks if possible.
"""

GROUNDED_CHAT_SYSTEM_PROMPT = """You are CareWise AI, an expert, objective health insurance assistant helping a patient or caregiver.
Answer the user's question STRICTLY and ONLY using the provided excerpts from their insurance policy.

RULES:
1. Every statement or condition you mention MUST cite the exact page number (e.g. Page 1, Page 2).
2. If the excerpts do not contain the answer, state clearly: "This is not specified in the extracted policy document."
3. Highlight caregiver risks clearly (such as proportionate deduction penalties if room tariff is breached).
4. Return your output in JSON format:
{
  "answer": "Clear, grounded markdown explanation citing Page numbers...",
  "cited_pages": [1, 2],
  "confidence": 0.92,
  "suggested_actions": ["Action 1", "Action 2"]
}
"""

def clean_json_response(raw_text: str) -> Optional[Dict[str, Any]]:
    """Clean markdown code blocks and parse JSON."""
    try:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_text)
        cleaned = match.group(1).strip() if match else raw_text.strip()
        first_brace = cleaned.find("{")
        last_brace = cleaned.rfind("}")
        if first_brace != -1 and last_brace != -1:
            cleaned = cleaned[first_brace:last_brace + 1]
        return json.loads(cleaned)
    except Exception as e:
        logger.warning(f"Failed to parse LLM response as JSON: {e}. Raw: {raw_text[:200]}")
        return None

class LLMClient:
    def __init__(self):
        self.timeout = settings.LLM_TIMEOUT_SECONDS

    def _call_claude(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        if not settings.ANTHROPIC_API_KEY:
            return None
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": settings.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 2048,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}]
        }
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(url, headers=headers, json=payload)
            if res.status_code == 200:
                data = res.json()
                return data["content"][0]["text"]
            logger.warning(f"Claude API returned status {res.status_code}: {res.text}")
            return None

    def _call_openai(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        if not settings.OPENAI_API_KEY:
            return None
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1
        }
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(url, headers=headers, json=payload)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"]
            logger.warning(f"OpenAI API returned status {res.status_code}: {res.text}")
            return None

    def _call_gemini(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        if not settings.GEMINI_API_KEY:
            return None
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.1
            }
        }
        with httpx.Client(timeout=self.timeout) as client:
            res = client.post(url, headers=headers, json=payload)
            if res.status_code == 200:
                data = res.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            logger.warning(f"Gemini API returned status {res.status_code}: {res.text}")
            return None

    def _call_ollama(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        if not settings.OLLAMA_BASE_URL:
            return None
        url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate"
        payload = {
            "model": "llama3:latest",
            "prompt": f"{system_prompt}\n\nTask:\n{user_prompt}",
            "format": "json",
            "stream": False
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data.get("response")
        except Exception:
            return None
        return None

    def _execute_llm(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        if settings.ANTHROPIC_API_KEY:
            try:
                res = self._call_claude(system_prompt, user_prompt)
                if res:
                    return res
            except Exception as e:
                logger.warning(f"Claude call failed: {e}")

        if settings.OPENAI_API_KEY:
            try:
                res = self._call_openai(system_prompt, user_prompt)
                if res:
                    return res
            except Exception as e:
                logger.warning(f"OpenAI call failed: {e}")

        if settings.GEMINI_API_KEY:
            try:
                res = self._call_gemini(system_prompt, user_prompt)
                if res:
                    return res
            except Exception as e:
                logger.warning(f"Gemini call failed: {e}")

        try:
            res = self._call_ollama(system_prompt, user_prompt)
            if res:
                return res
        except Exception as e:
            logger.debug(f"Ollama call not available: {e}")

        return None

    def extract_policy_fields(self, full_text: str) -> Optional[Dict[str, Any]]:
        trimmed_text = full_text[:28000]
        prompt = f"Policy Document Excerpt:\n\n{trimmed_text}\n\nExtract all insurance fields matching the requested JSON schema."
        
        try:
            response_text = self._execute_llm(EXTRACTION_SYSTEM_PROMPT, prompt)
            if response_text:
                data = clean_json_response(response_text)
                if data and "sum_insured" in data:
                    logger.info("Successfully extracted policy fields via LLM.")
                    return data
        except Exception as e:
            logger.warning(f"LLM field extraction failed, falling back to heuristics: {e}")
        return None

    def answer_grounded_query(
        self,
        chunks: List[Dict[str, Any]],
        query: str,
        policy_name: str,
        language: str = "en"
    ) -> Optional[Dict[str, Any]]:
        context_parts = []
        for c in chunks:
            context_parts.append(f"--- Excerpt (Page {c['page_number']}) ---\n{c['text']}")
        context_str = "\n\n".join(context_parts)

        lang_instruction = ""
        if language == "hi":
            lang_instruction = (
                "\n\nCRITICAL LANGUAGE INSTRUCTION: The caregiver requested the explanation in Hindi. "
                "Provide the 'answer' field and 'suggested_actions' in fluent, natural Hindi (Devanagari script), "
                "while citing exact page numbers (e.g. पृष्ठ 1, पृष्ठ 2) and keeping insurance terms clear."
            )

        prompt = f"Policy Name: {policy_name}\n\nRetrieved Grounded Excerpts:\n{context_str}\n\nCaregiver Question: {query}{lang_instruction}"

        try:
            response_text = self._execute_llm(GROUNDED_CHAT_SYSTEM_PROMPT, prompt)
            if response_text:
                data = clean_json_response(response_text)
                if data and "answer" in data:
                    return data
        except Exception as e:
            logger.warning(f"LLM grounded query answering failed: {e}")
        return None

llm_client = LLMClient()
