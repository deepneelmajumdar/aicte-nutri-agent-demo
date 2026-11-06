"""
Core Nutrition Agent – orchestrates all AI-powered features using IBM Granite.
"""
from __future__ import annotations

from utils.granite_client import GraniteClient


class NutritionAgent:
    """
    The central agent that routes user intents to specialised prompt strategies
    and returns structured, actionable nutrition guidance.
    """

    SYSTEM_PERSONA = (
        "You are 'NutriGenius', an expert AI nutrition assistant powered by IBM Granite. "
        "You combine evidence-based nutritional science with personalised, empathetic coaching. "
        "You always consider the user's health goals, medical conditions, dietary restrictions, "
        "cultural food preferences, and fitness routines before giving advice. "
        "Provide clear, practical, and motivating guidance. Format your responses with headings "
        "and bullet points for readability. Never provide medical diagnoses — always recommend "
        "consulting a registered dietitian for clinical decisions."
    )

    def __init__(self):
        self.client = GraniteClient()
        self.conversation_history: list[dict] = []

    # ── Conversation management ───────────────────────────────────────────────

    def _build_prompt(self, user_message: str, context: str = "") -> str:
        """Build a full prompt string including system persona and chat history."""
        lines = [f"<|system|>\n{self.SYSTEM_PERSONA}\n"]
        if context:
            lines.append(f"<|context|>\n{context}\n")
        # Include last 6 turns of history for context
        for turn in self.conversation_history[-6:]:
            role = turn["role"]
            content = turn["content"]
            lines.append(f"<|{role}|>\n{content}")
        lines.append(f"<|user|>\n{user_message}\n<|assistant|>")
        return "\n".join(lines)

    def chat(self, user_message: str, user_profile: dict | None = None) -> str:
        """General-purpose conversational Q&A with the nutrition assistant."""
        context = self._profile_context(user_profile) if user_profile else ""
        prompt = self._build_prompt(user_message, context)
        response = self.client.generate(prompt)
        # Store in history
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": response})
        return response

    def clear_history(self):
        """Reset conversation history."""
        self.conversation_history = []

    # ── Meal plan generation ──────────────────────────────────────────────────

    def generate_meal_plan(self, user_profile: dict) -> str:
        """
        Generate a personalised weekly meal plan based on the user's profile.
        """
        profile_str = self._profile_context(user_profile)
        prompt = self._build_prompt(
            f"""Create a detailed 7-day personalised meal plan for me.

{profile_str}

Requirements:
- Provide breakfast, lunch, dinner, and 2 snacks for each day
- Include approximate calorie counts per meal
- Explain WHY each meal fits my goals in 1-2 sentences
- Use ingredients that respect my dietary restrictions and cultural preferences
- Keep meals practical and easy to prepare (under 30 min unless noted)
- Format each day clearly with Day headers and meal sections""",
        )
        return self.client.generate(prompt, max_tokens=2000)

    # ── Food analysis ─────────────────────────────────────────────────────────

    def analyze_food(self, food_description: str, user_profile: dict | None = None) -> str:
        """Analyse a described food item or meal for its nutritional profile."""
        context = self._profile_context(user_profile) if user_profile else ""
        prompt = self._build_prompt(
            f"""Analyse the following food/meal for me:

**Food:** {food_description}

Please provide:
1. **Nutritional breakdown** – Estimated calories, protein, carbs, fat, fibre, key vitamins/minerals
2. **Health benefits** – Key nutrients and what they do for the body
3. **Potential concerns** – Allergens, high sodium/sugar, etc.
4. **Suitability rating** – How well this fits my goals (1-10) with explanation
5. **Smart improvements** – 2-3 easy tweaks to make it healthier
6. **Best time to eat** – When in the day this food works best and why""",
            context,
        )
        return self.client.generate(prompt, max_tokens=1200)

    # ── Smart food swaps ──────────────────────────────────────────────────────

    def suggest_food_swaps(self, food_item: str, swap_goal: str, user_profile: dict | None = None) -> str:
        """Recommend healthier alternatives to a given food item."""
        context = self._profile_context(user_profile) if user_profile else ""
        prompt = self._build_prompt(
            f"""I want smarter alternatives for: **{food_item}**
Goal for the swap: **{swap_goal}**

Please provide 5 food swap recommendations:
For each swap, include:
- **Swap name** and brief description
- **Why it's better** for my goal
- **Nutritional comparison** (key numbers vs the original)
- **How to use it** – practical serving suggestion
- **Taste similarity score** (1-10) so I know what to expect""",
            context,
        )
        return self.client.generate(prompt, max_tokens=1200)

    # ── Contextual explanation ────────────────────────────────────────────────

    def explain_nutrition(self, topic: str) -> str:
        """Explain a nutrition concept in plain, engaging language."""
        prompt = self._build_prompt(
            f"""Explain the following nutrition topic in a clear, engaging way suitable for someone without a science background:

**Topic:** {topic}

Structure your explanation with:
1. **What is it?** – Simple definition
2. **Why does it matter?** – Impact on health
3. **How much do I need?** – Recommended amounts
4. **Best food sources** – Top 5-7 foods with amounts
5. **Signs of deficiency / excess** – What to watch for
6. **Common myths busted** – 1-2 misconceptions
7. **Quick practical tips** – 3 actionable takeaways"""
        )
        return self.client.generate(prompt, max_tokens=1000)

    # ── Progress coaching ─────────────────────────────────────────────────────

    def adapt_plan(self, feedback: str, current_plan_summary: str, user_profile: dict | None = None) -> str:
        """Adapt recommendations based on user feedback and progress."""
        context = self._profile_context(user_profile) if user_profile else ""
        prompt = self._build_prompt(
            f"""Based on the following feedback about my nutrition journey, adapt my plan:

**Current plan summary:** {current_plan_summary}
**My feedback / what happened:** {feedback}

Please:
1. **Acknowledge** what I shared with empathy
2. **Identify the root cause** of any challenges
3. **Adjust the plan** – specific changes to address the feedback
4. **Suggest 3 actionable steps** for the coming week
5. **Motivational message** to keep me going""",
            context,
        )
        return self.client.generate(prompt, max_tokens=900)

    # ── Helper ────────────────────────────────────────────────────────────────

    @staticmethod
    def _profile_context(profile: dict) -> str:
        """Convert a user profile dict to a readable context string."""
        if not profile:
            return ""
        lines = ["**My Profile:**"]
        field_labels = {
            "name": "Name",
            "age": "Age",
            "gender": "Gender",
            "weight": "Weight (kg)",
            "height": "Height (cm)",
            "goal": "Health Goal",
            "activity": "Activity Level",
            "conditions": "Medical Conditions",
            "allergies": "Food Allergies / Intolerances",
            "diet_type": "Dietary Preference",
            "cuisine": "Preferred Cuisine / Cultural Foods",
            "avoid": "Foods to Avoid",
        }
        for key, label in field_labels.items():
            value = profile.get(key)
            if value and value not in ("", "None", "Not specified"):
                lines.append(f"- {label}: {value}")
        return "\n".join(lines)
