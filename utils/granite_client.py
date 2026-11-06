"""
IBM watsonx.ai / Granite LLM client wrapper.
Handles authentication (IAM token exchange) and text generation.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()


class GraniteClient:
    """Thin wrapper around the watsonx.ai Granite inference REST API."""

    IAM_URL = "https://iam.cloud.ibm.com/identity/token"

    def __init__(self):
        self.api_key = os.getenv("IBM_API_KEY", "")
        self.project_id = os.getenv("WATSONX_PROJECT_ID", "")
        self.watsonx_url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com").rstrip("/")
        self.model_id = os.getenv("GRANITE_MODEL_ID", "ibm/granite-3-3-8b-instruct")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "1024"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self._iam_token: str | None = None

    # ── Authentication ───────────────────────────────────────────────────────

    def _get_iam_token(self) -> str:
        """Exchange the IBM API key for a short-lived IAM bearer token."""
        resp = requests.post(
            self.IAM_URL,
            data={
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": self.api_key,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        resp.raise_for_status()
        self._iam_token = resp.json()["access_token"]
        return self._iam_token

    def _token(self) -> str:
        if not self._iam_token:
            return self._get_iam_token()
        return self._iam_token

    # ── Text generation ──────────────────────────────────────────────────────

    def generate(self, prompt: str, max_tokens: int | None = None, temperature: float | None = None) -> str:
        """
        Call the watsonx.ai text-generation endpoint and return the generated text.
        Falls back gracefully if credentials are missing (demo mode).
        """
        if not self.api_key or self.api_key == "your_ibm_cloud_api_key_here":
            return self._demo_fallback(prompt)

        url = f"{self.watsonx_url}/ml/v1/text/generation?version=2023-05-29"
        headers = {
            "Authorization": f"Bearer {self._token()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "model_id": self.model_id,
            "project_id": self.project_id,
            "input": prompt,
            "parameters": {
                "decoding_method": "sample",
                "max_new_tokens": max_tokens or self.max_tokens,
                "temperature": temperature or self.temperature,
                "top_k": 50,
                "top_p": 0.9,
                "repetition_penalty": 1.1,
            },
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=60)
            # Token may have expired – retry once with a fresh token
            if resp.status_code == 401:
                self._iam_token = None
                headers["Authorization"] = f"Bearer {self._token()}"
                resp = requests.post(url, json=payload, headers=headers, timeout=60)
            resp.raise_for_status()
            results = resp.json().get("results", [{}])
            return results[0].get("generated_text", "").strip()
        except requests.RequestException as exc:
            return f"⚠️ IBM watsonx.ai error: {exc}"

    # ── Demo / offline fallback ───────────────────────────────────────────────

    @staticmethod
    def _demo_fallback(prompt: str) -> str:
        """Return a placeholder when no valid credentials are configured."""
        return (
            "**[Demo Mode – IBM credentials not configured]**\n\n"
            "To get real AI responses, add your `IBM_API_KEY` and "
            "`WATSONX_PROJECT_ID` to the `.env` file.\n\n"
            f"*Received prompt preview:* {prompt[:120]}…"
        )
