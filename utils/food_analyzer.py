"""
Food image / label analyzer using IBM Granite multimodal-style text description.
Users describe what they see or upload a photo; this module extracts nutritional insights.
"""
from __future__ import annotations

import base64
import io
from PIL import Image

from utils.granite_client import GraniteClient


def image_to_base64(image: Image.Image) -> str:
    """Convert a PIL Image to a base64-encoded JPEG string."""
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def extract_label_text(image: Image.Image) -> str:
    """
    Attempt OCR-style extraction from a food label image.
    Returns a description prompt for Granite (vision not available on Lite tier;
    we ask the user to describe, or parse any readable text segments).
    """
    # On IBM Cloud Lite, we use text-only Granite.
    # We accept the image for display, but ask the user to describe contents.
    return (
        "I can see a food product image. Based on typical food label formats, "
        "please describe the product details so I can give you accurate nutrition analysis."
    )


class FoodAnalyzer:
    """Analyse foods described as text or from uploaded images."""

    def __init__(self):
        self.client = GraniteClient()

    def analyze_from_description(self, description: str, user_profile: dict | None = None) -> dict:
        """
        Full analysis from a text description of a food item.
        Returns a dict with keys: analysis, score, macros_estimate.
        """
        profile_ctx = self._profile_ctx(user_profile)
        prompt = f"""<|system|>
You are a precision nutrition analyst AI. Be specific, data-driven, and practical.
<|user|>
Analyse this food for me:
**{description}**

{profile_ctx}

Return your analysis in this exact structure:

## 🔬 Nutritional Breakdown (per 100g / per serving)
| Nutrient | Amount |
|----------|--------|
| Calories | ... |
| Protein | ... |
| Carbohydrates | ... |
| Fat | ... |
| Fibre | ... |
| Sugar | ... |
| Sodium | ... |

## ✅ Health Benefits
(3-4 bullet points)

## ⚠️ Watch Out For
(allergens, concerns)

## 🎯 Goal Compatibility
Rate 1-10 how well this fits the user's goals and explain briefly.

## 💡 Smart Improvements
(2-3 specific tweaks)

## ⏰ Best Time to Eat
<|assistant|>"""
        analysis = self.client.generate(prompt, max_tokens=1200)
        score = self._extract_score(analysis)
        return {"analysis": analysis, "score": score}

    def analyze_grocery_label(self, label_text: str) -> dict:
        """Parse and interpret a grocery/nutrition label's text content."""
        prompt = f"""<|system|>
You are an expert at reading and interpreting food nutrition labels.
<|user|>
Here is the nutrition label / ingredient list from a food product:

{label_text}

Please:
1. **Summarise what this product is** based on the label
2. **Highlight the top 3 nutritional pros** of this product
3. **Flag the top 3 nutritional concerns** (e.g. high sodium, added sugars, trans fats)
4. **Decode the ingredient list** – explain any unfamiliar additives
5. **Who should / shouldn't eat this** – ideal consumer profile
6. **Healthier alternatives** – 2 similar products that are typically better
7. **Overall health rating** – A/B/C/D/F with justification
<|assistant|>"""
        analysis = self.client.generate(prompt, max_tokens=1000)
        return {"analysis": analysis}

    @staticmethod
    def _extract_score(text: str) -> int:
        """Try to parse the 1-10 compatibility score from the analysis text."""
        import re
        matches = re.findall(r"\b([1-9]|10)\s*/\s*10\b", text)
        if matches:
            return int(matches[0])
        return 7  # default

    @staticmethod
    def _profile_ctx(profile: dict | None) -> str:
        if not profile:
            return ""
        parts = []
        if profile.get("goal"):
            parts.append(f"Goal: {profile['goal']}")
        if profile.get("conditions"):
            parts.append(f"Medical conditions: {profile['conditions']}")
        if profile.get("allergies"):
            parts.append(f"Allergies: {profile['allergies']}")
        if profile.get("diet_type"):
            parts.append(f"Diet type: {profile['diet_type']}")
        return "**User context:** " + " | ".join(parts) if parts else ""
