"""
Smart food swap recommender powered by IBM Granite.
"""
from __future__ import annotations

from utils.granite_client import GraniteClient


SWAP_GOALS = [
    "Lower calories",
    "Increase protein",
    "Reduce sugar",
    "Lower sodium / salt",
    "Reduce saturated fat",
    "Increase fibre",
    "Boost vitamins & minerals",
    "Manage blood sugar (diabetic-friendly)",
    "Heart-healthy",
    "Anti-inflammatory",
    "Weight loss",
    "Muscle building",
    "Plant-based / vegan alternative",
    "Gluten-free alternative",
    "Budget-friendly healthier option",
]


class SwapRecommender:
    """Generate smart, goal-aligned food swap recommendations."""

    def __init__(self):
        self.client = GraniteClient()

    def get_swaps(
        self,
        food_item: str,
        goal: str,
        user_profile: dict | None = None,
        n: int = 5,
    ) -> str:
        """
        Returns markdown-formatted swap recommendations.
        """
        profile_ctx = self._profile_ctx(user_profile)
        prompt = f"""<|system|>
You are a smart nutrition swap advisor. Your job is to help people make better food choices
by suggesting practical, delicious, and scientifically-backed alternatives.
<|user|>
Original food: **{food_item}**
Swap goal: **{goal}**
{profile_ctx}

Suggest {n} smart food swaps. For each one, use this exact format:

### Swap [N]: [Food Name]
**Why it's better:** [1-2 sentences explaining the nutritional advantage for the stated goal]
**Key numbers:** [Relevant comparison, e.g. "80 cal vs 220 cal", "12g protein vs 4g protein"]
**How to use it:** [Practical 1-sentence serving suggestion]
**Taste match:** [Score 1-10] – [brief note on how similar it tastes]
**Best for:** [Type of person / scenario this swap works best for]

---
After all swaps, add:
## 🏆 Top Pick
Name the single best swap and give a 2-3 sentence justification.
<|assistant|>"""
        return self.client.generate(prompt, max_tokens=1400)

    def quick_swap(self, food_item: str) -> str:
        """Return a single quick healthier swap suggestion."""
        prompt = f"""<|system|>
You are a concise nutrition coach.
<|user|>
Give me ONE quick, simple, healthier swap for: **{food_item}**

Format:
**Instead of:** {food_item}
**Try:** [healthier option]
**Why:** [one sentence]
**Saving:** [e.g. saves 120 calories, adds 8g protein]
<|assistant|>"""
        return self.client.generate(prompt, max_tokens=200)

    def meal_makeover(self, meal_description: str, user_profile: dict | None = None) -> str:
        """Give a full meal a healthier makeover by swapping individual components."""
        profile_ctx = self._profile_ctx(user_profile)
        prompt = f"""<|system|>
You are an expert nutrition coach specialising in healthy meal transformations.
<|user|>
Give this meal a complete healthy makeover:

**Meal:** {meal_description}
{profile_ctx}

For EACH component of the meal:
1. Identify what it is
2. Suggest a healthier swap (or confirm it's already healthy)
3. Explain the nutritional improvement

Then provide:
## 📊 Nutritional Impact Summary
Compare the original vs. makeover meal in a table:
| Metric | Original | Makeover | Improvement |
|--------|----------|----------|-------------|
| Calories | ... | ... | ... |
| Protein | ... | ... | ... |
| Fibre | ... | ... | ... |
| Saturated Fat | ... | ... | ... |

## 🌟 Overall Assessment
Rate the improvement and add 2-3 motivational sentences.
<|assistant|>"""
        return self.client.generate(prompt, max_tokens=1400)

    @staticmethod
    def _profile_ctx(profile: dict | None) -> str:
        if not profile:
            return ""
        parts = []
        if profile.get("allergies"):
            parts.append(f"⚠️ Allergies/intolerances: {profile['allergies']}")
        if profile.get("diet_type"):
            parts.append(f"Diet: {profile['diet_type']}")
        if profile.get("conditions"):
            parts.append(f"Health conditions: {profile['conditions']}")
        return "\n".join(parts) if parts else ""
