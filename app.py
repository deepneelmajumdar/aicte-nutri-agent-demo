"""
🥗 AI Nutrition Assistant – Powered by IBM Granite (watsonx.ai)
Main Streamlit Application
"""
import os
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Nutrition Assistant",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "AI Nutrition Assistant powered by IBM Granite / watsonx.ai",
    },
)

# ── Lazy imports (avoid import errors before requirements install) ─────────────
@st.cache_resource
def get_agent():
    from utils.nutrition_agent import NutritionAgent
    return NutritionAgent()

@st.cache_resource
def get_food_analyzer():
    from utils.food_analyzer import FoodAnalyzer
    return FoodAnalyzer()

@st.cache_resource
def get_swap_recommender():
    from utils.swap_recommender import SwapRecommender, SWAP_GOALS
    return SwapRecommender(), SWAP_GOALS


# ── Custom CSS ─────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown(
        """
        <style>
        /* ── Global ── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f3d2e 0%, #145a32 100%);
        }
        [data-testid="stSidebar"] * { color: #e8f5e9 !important; }
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stTextInput label,
        [data-testid="stSidebar"] .stNumberInput label,
        [data-testid="stSidebar"] .stSlider label { color: #a5d6a7 !important; font-weight: 500; }
        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #81c784 !important; }

        /* ── Metric cards ── */
        [data-testid="metric-container"] {
            background: #f0faf4;
            border: 1px solid #c8e6c9;
            border-radius: 12px;
            padding: 16px;
        }

        /* ── Tab styling ── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: #f8fffe;
            border-radius: 12px;
            padding: 4px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            background: #1b5e20 !important;
            color: white !important;
        }

        /* ── Chat bubbles ── */
        .chat-user {
            background: #e8f5e9;
            border-left: 4px solid #2e7d32;
            border-radius: 0 12px 12px 0;
            padding: 12px 16px;
            margin: 8px 0;
        }
        .chat-assistant {
            background: #f3f4f6;
            border-left: 4px solid #3b82f6;
            border-radius: 0 12px 12px 0;
            padding: 12px 16px;
            margin: 8px 0;
        }

        /* ── Buttons ── */
        .stButton > button {
            background: linear-gradient(135deg, #1b5e20, #2e7d32) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 24px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #2e7d32, #388e3c) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(46, 125, 50, 0.3) !important;
        }

        /* ── Hero banner ── */
        .hero-banner {
            background: linear-gradient(135deg, #0d3b22 0%, #1b5e20 50%, #2e7d32 100%);
            color: white;
            padding: 32px 40px;
            border-radius: 16px;
            margin-bottom: 24px;
        }
        .hero-banner h1 { color: white; font-size: 2.2rem; margin: 0; }
        .hero-banner p { color: #a5d6a7; margin: 8px 0 0; font-size: 1.05rem; }

        /* ── Feature cards ── */
        .feature-card {
            background: white;
            border: 1px solid #e0f2e9;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }
        .feature-card .icon { font-size: 2.5rem; margin-bottom: 12px; }
        .feature-card h4 { color: #1b5e20; margin: 0 0 8px; font-size: 1rem; font-weight: 600; }
        .feature-card p { color: #555; margin: 0; font-size: 0.88rem; line-height: 1.5; }

        /* ── IBM badge ── */
        .ibm-badge {
            background: #0530ad;
            color: white !important;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
        }

        /* ── Result box ── */
        .result-box {
            background: #fafffe;
            border: 1px solid #c8e6c9;
            border-radius: 12px;
            padding: 20px 24px;
        }

        /* ── Score badge ── */
        .score-high { color: #2e7d32; font-size: 2rem; font-weight: 700; }
        .score-mid  { color: #f57c00; font-size: 2rem; font-weight: 700; }
        .score-low  { color: #c62828; font-size: 2rem; font-weight: 700; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Session state initialisation ──────────────────────────────────────────────
def init_session():
    defaults = {
        "chat_messages": [],
        "user_profile": {},
        "meal_plan_result": "",
        "analysis_result": {},
        "swap_result": "",
        "profile_saved": False,
        "active_tab": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Sidebar – User Profile ─────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center; padding: 16px 0 8px;">
                <div style="font-size:3rem;">🥗</div>
                <h2 style="margin:4px 0; font-size:1.3rem;">NutriGenius</h2>
                <div class="ibm-badge">Powered by IBM Granite</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown("### 👤 Your Profile")
        st.caption("Fill in your details for personalised advice")

        with st.form("profile_form"):
            name = st.text_input("Name", placeholder="Your name", value=st.session_state.user_profile.get("name", ""))
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Age", 10, 100, value=int(st.session_state.user_profile.get("age", 30)), step=1)
            with col2:
                gender = st.selectbox("Gender", ["Male", "Female", "Non-binary", "Prefer not to say"],
                    index=["Male", "Female", "Non-binary", "Prefer not to say"].index(
                        st.session_state.user_profile.get("gender", "Male")))

            col3, col4 = st.columns(2)
            with col3:
                weight = st.number_input("Weight (kg)", 30.0, 300.0,
                    value=float(st.session_state.user_profile.get("weight", 70.0)), step=0.5)
            with col4:
                height = st.number_input("Height (cm)", 100, 250,
                    value=int(st.session_state.user_profile.get("height", 170)), step=1)

            goal = st.selectbox("🎯 Health Goal", [
                "Weight loss", "Weight gain / muscle building", "Maintain weight",
                "Improve energy levels", "Manage diabetes", "Heart health",
                "Athletic performance", "Gut health", "Reduce inflammation", "General wellness",
            ], index=0)

            activity = st.selectbox("🏃 Activity Level", [
                "Sedentary (desk job, little exercise)",
                "Lightly active (1-3 days/week)",
                "Moderately active (3-5 days/week)",
                "Very active (6-7 days/week)",
                "Extremely active (athlete / physical job)",
            ])

            diet_type = st.selectbox("🥦 Dietary Preference", [
                "No restriction", "Vegetarian", "Vegan", "Pescatarian",
                "Keto / Low-carb", "Mediterranean", "Paleo", "Gluten-free",
                "Dairy-free", "Halal", "Kosher", "Jain",
            ])

            cuisine = st.text_input("🌍 Preferred Cuisine", placeholder="e.g. Indian, Mediterranean, Mexican",
                value=st.session_state.user_profile.get("cuisine", ""))

            allergies = st.text_input("⚠️ Allergies / Intolerances",
                placeholder="e.g. nuts, lactose, gluten",
                value=st.session_state.user_profile.get("allergies", ""))

            conditions = st.text_area("🏥 Medical Conditions",
                placeholder="e.g. Type 2 diabetes, hypertension, PCOS",
                value=st.session_state.user_profile.get("conditions", ""),
                height=70)

            saved = st.form_submit_button("💾 Save Profile", use_container_width=True)
            if saved:
                st.session_state.user_profile = {
                    "name": name, "age": age, "gender": gender,
                    "weight": weight, "height": height, "goal": goal,
                    "activity": activity, "diet_type": diet_type,
                    "cuisine": cuisine, "allergies": allergies,
                    "conditions": conditions,
                }
                st.session_state.profile_saved = True

        if st.session_state.profile_saved:
            st.success("✅ Profile saved!")

        # BMI Calculator
        if st.session_state.user_profile.get("weight") and st.session_state.user_profile.get("height"):
            bmi = st.session_state.user_profile["weight"] / ((st.session_state.user_profile["height"] / 100) ** 2)
            bmi_cat = (
                "Underweight" if bmi < 18.5 else
                "Normal weight" if bmi < 25 else
                "Overweight" if bmi < 30 else "Obese"
            )
            bmi_color = "#2e7d32" if bmi_cat == "Normal weight" else "#f57c00" if bmi_cat in ("Overweight", "Underweight") else "#c62828"
            st.markdown("---")
            st.markdown(f"**📊 Your BMI:** <span style='color:{bmi_color}; font-size:1.3rem; font-weight:700;'>{bmi:.1f}</span> – {bmi_cat}", unsafe_allow_html=True)

        # TDEE Calculator
        if all(st.session_state.user_profile.get(k) for k in ["weight", "height", "age", "gender", "activity"]):
            w = float(st.session_state.user_profile["weight"])
            h = float(st.session_state.user_profile["height"])
            a = int(st.session_state.user_profile["age"])
            g = st.session_state.user_profile["gender"]
            activity_multipliers = {
                "Sedentary (desk job, little exercise)": 1.2,
                "Lightly active (1-3 days/week)": 1.375,
                "Moderately active (3-5 days/week)": 1.55,
                "Very active (6-7 days/week)": 1.725,
                "Extremely active (athlete / physical job)": 1.9,
            }
            bmr = (10 * w + 6.25 * h - 5 * a + (5 if g == "Male" else -161))
            act_key = st.session_state.user_profile.get("activity", "Sedentary (desk job, little exercise)")
            tdee = bmr * activity_multipliers.get(act_key, 1.2)
            st.markdown(f"**🔥 Daily Calories (TDEE):** <span style='color:#e65100; font-size:1.1rem; font-weight:700;'>{tdee:.0f} kcal</span>", unsafe_allow_html=True)

        st.markdown("---")
        st.caption("🔐 IBM watsonx.ai · Granite LLM\nYour data stays local.")


# ── Tab: Home / Overview ──────────────────────────────────────────────────────
def render_home():
    st.markdown(
        """
        <div class="hero-banner">
            <h1>🥗 AI Nutrition Assistant</h1>
            <p>Personalised nutrition intelligence powered by <strong>IBM Granite</strong> on watsonx.ai</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Feature overview cards
    features = [
        ("💬", "Ask NutriGenius", "Chat with your AI nutrition expert for instant, personalised guidance on any food or diet question."),
        ("📅", "Meal Plan Generator", "Get a personalised 7-day meal plan with calories, macros, and explanations — tailored to your goals."),
        ("🔍", "Food Analyzer", "Describe a food or paste a nutrition label to get a deep nutritional breakdown and smart tips."),
        ("🔄", "Smart Food Swaps", "Discover healthier alternatives to your favourite foods, aligned with your specific health goals."),
        ("🧠", "Nutrition Encyclopedia", "Understand any nutrition concept in plain English — from macros to micronutrients."),
        ("📈", "Progress Coach", "Share your experience and get your plan dynamically adapted with empathy and precision."),
    ]

    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="feature-card">
                    <div class="icon">{icon}</div>
                    <h4>{title}</h4>
                    <p>{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        if i == 2:
            st.markdown("")
            cols = st.columns(3)

    st.markdown("---")

    # How it works
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown("### 🚀 How It Works")
        st.markdown("""
1. **Set up your profile** in the sidebar → health goal, dietary preferences, allergies, medical conditions
2. **Choose a feature** from the tabs above
3. **Interact with IBM Granite AI** to get personalised, evidence-based nutrition guidance
4. **Refine & adapt** — provide feedback and watch your plan evolve

> 💡 **Tip:** The more complete your profile, the more personalised your recommendations!
""")
    with col_b:
        st.markdown("### ⚙️ Powered By")
        st.markdown("""
| Component | Technology |
|-----------|------------|
| 🤖 LLM Engine | IBM Granite 3.3 8B Instruct |
| ☁️ Cloud | IBM watsonx.ai (Lite) |
| 🖥️ Interface | Streamlit |
| 🔐 Auth | IBM Cloud IAM |
| 🐍 Language | Python 3.11+ |

🔗 [Get IBM Cloud Lite Account](https://cloud.ibm.com/registration) (Free)
""")

    st.markdown("---")
    st.info(
        "⚠️ **Medical Disclaimer:** This AI assistant provides general nutrition information only. "
        "It is not a substitute for professional medical or dietetic advice. "
        "Always consult a registered dietitian or physician for clinical decisions.",
        icon="🏥",
    )


# ── Tab: Chat ─────────────────────────────────────────────────────────────────
def render_chat():
    st.markdown("## 💬 Chat with NutriGenius")
    st.caption("Ask anything about nutrition, diet, food, or your health goals")

    agent = get_agent()

    # Display conversation history
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_messages:
            st.markdown(
                """
                <div class="chat-assistant">
                👋 <strong>Hi! I'm NutriGenius</strong>, your personal AI nutrition assistant powered by IBM Granite.<br><br>
                I can help you with:<br>
                • 🥗 Food choices and meal ideas<br>
                • 📊 Understanding nutrition labels<br>
                • 🎯 Reaching your health goals<br>
                • 💊 Vitamins, minerals, and supplements<br>
                • 🍽️ Recipe improvements<br><br>
                What nutrition question can I help you with today?
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            for msg in st.session_state.chat_messages:
                css_class = "chat-user" if msg["role"] == "user" else "chat-assistant"
                icon = "🧑" if msg["role"] == "user" else "🤖"
                st.markdown(
                    f'<div class="{css_class}"><strong>{icon} {"You" if msg["role"] == "user" else "NutriGenius"}:</strong><br>{msg["content"]}</div>',
                    unsafe_allow_html=True,
                )

    # Quick prompt suggestions
    st.markdown("**💡 Quick questions:**")
    qs = [
        "What should I eat before a workout?",
        "Is intermittent fasting right for me?",
        "How do I read a nutrition label?",
        "What are the best high-protein snacks?",
    ]
    cols = st.columns(4)
    for i, q in enumerate(qs):
        if cols[i].button(q, key=f"quick_{i}", use_container_width=True):
            st.session_state["_pending_chat"] = q

    # Input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Your message",
            placeholder="Ask me anything about nutrition...",
            height=80,
            label_visibility="collapsed",
        )
        col_send, col_clear = st.columns([4, 1])
        submitted = col_send.form_submit_button("🚀 Send", use_container_width=True)
        cleared = col_clear.form_submit_button("🗑️ Clear", use_container_width=True)

    # Handle quick prompt injection
    if "_pending_chat" in st.session_state:
        user_input = st.session_state.pop("_pending_chat")
        submitted = True

    if cleared:
        st.session_state.chat_messages = []
        agent.clear_history()
        st.rerun()

    if submitted and user_input.strip():
        st.session_state.chat_messages.append({"role": "user", "content": user_input.strip()})
        with st.spinner("🤔 NutriGenius is thinking..."):
            response = agent.chat(user_input.strip(), st.session_state.user_profile or None)
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.rerun()


# ── Tab: Meal Plan ─────────────────────────────────────────────────────────────
def render_meal_plan():
    st.markdown("## 📅 Personalised Meal Plan Generator")
    st.caption("Get a complete 7-day meal plan tailored to your goals, preferences, and lifestyle")

    agent = get_agent()

    if not st.session_state.user_profile:
        st.warning("👈 Please fill in your profile in the sidebar first for a personalised meal plan.")
        return

    profile = st.session_state.user_profile
    col1, col2, col3 = st.columns(3)
    col1.metric("🎯 Goal", profile.get("goal", "—").split("/")[0].strip())
    col2.metric("🥦 Diet", profile.get("diet_type", "—"))
    col3.metric("🏃 Activity", profile.get("activity", "—").split("(")[0].strip())

    st.markdown("---")

    # Additional preferences
    with st.expander("⚙️ Advanced Meal Plan Options", expanded=False):
        col_a, col_b = st.columns(2)
        with col_a:
            prep_time = st.selectbox("Max prep time per meal", ["No preference", "Under 15 min", "Under 30 min", "Under 45 min", "Up to 1 hour"])
            budget = st.selectbox("Budget level", ["No preference", "Budget-friendly", "Moderate", "Premium ingredients ok"])
        with col_b:
            servings = st.selectbox("Cooking for", ["Just me (1 person)", "2 people", "Family (4+)"])
            focus_meal = st.selectbox("Focus on", ["Balanced across all meals", "High-protein breakfasts", "Light dinners", "Meal prep friendly"])

    if st.button("🚀 Generate My 7-Day Meal Plan", use_container_width=True):
        enhanced_profile = {**profile, "prep_time": prep_time, "budget": budget, "servings": servings, "focus": focus_meal}
        with st.spinner("🧠 Generating your personalised meal plan with IBM Granite AI... (this may take 30-60 seconds)"):
            result = agent.generate_meal_plan(enhanced_profile)
        st.session_state.meal_plan_result = result

    if st.session_state.meal_plan_result:
        st.markdown("---")
        st.markdown("### 📋 Your Personalised 7-Day Meal Plan")
        st.markdown(
            f'<div class="result-box">{st.session_state.meal_plan_result}</div>',
            unsafe_allow_html=True,
        )

        # Download button
        st.download_button(
            "⬇️ Download Meal Plan (.txt)",
            data=st.session_state.meal_plan_result,
            file_name="my_nutrition_plan.txt",
            mime="text/plain",
        )


# ── Tab: Food Analyzer ─────────────────────────────────────────────────────────
def render_food_analyzer():
    st.markdown("## 🔍 Food Analyzer")
    st.caption("Analyse any food, dish, or nutrition label for deep nutritional insights")

    analyzer = get_food_analyzer()

    tabs = st.tabs(["📝 Describe a Food", "📷 Food Photo", "🏷️ Nutrition Label"])

    # ── Text description ──────────────────────────────────────────────
    with tabs[0]:
        st.markdown("**Describe your food or meal:**")
        food_desc = st.text_area(
            "Food description",
            placeholder="e.g. A bowl of overnight oats with chia seeds, almond milk, mixed berries, and a drizzle of honey",
            height=100,
            label_visibility="collapsed",
        )

        example_foods = ["Avocado toast with poached egg", "Chicken Caesar salad", "Dal tadka with brown rice", "Greek yogurt with granola", "Veggie burger"]
        st.markdown("**Try an example:**")
        ex_cols = st.columns(5)
        for i, ex in enumerate(example_foods):
            if ex_cols[i].button(ex, key=f"ex_{i}", use_container_width=True):
                st.session_state["_pending_food"] = ex

        if "_pending_food" in st.session_state:
            food_desc = st.session_state.pop("_pending_food")

        if st.button("🔬 Analyse Food", key="analyze_btn", use_container_width=True):
            if food_desc.strip():
                with st.spinner("🧪 Analysing nutritional profile with IBM Granite AI..."):
                    result = analyzer.analyze_from_description(food_desc.strip(), st.session_state.user_profile or None)
                st.session_state.analysis_result = result
            else:
                st.warning("Please describe a food item first.")

        if st.session_state.analysis_result:
            st.markdown("---")
            score = st.session_state.analysis_result.get("score", 7)
            score_class = "score-high" if score >= 7 else "score-mid" if score >= 5 else "score-low"
            st.markdown(
                f'<div class="result-box">'
                f'<div style="float:right; text-align:center;">'
                f'<span class="{score_class}">{score}/10</span><br>'
                f'<small style="color:#888;">Goal Match</small>'
                f'</div>'
                f'{st.session_state.analysis_result["analysis"]}'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Image upload ──────────────────────────────────────────────────
    with tabs[1]:
        st.info("📸 **How it works:** Upload a photo of your meal, and then describe it in the text box below. IBM Granite AI will analyse the nutritional content based on your description.")
        uploaded_file = st.file_uploader("Upload food photo", type=["jpg", "jpeg", "png", "webp"])
        if uploaded_file:
            img = Image.open(uploaded_file)
            col_img, col_desc = st.columns([1, 1])
            with col_img:
                st.image(img, caption="Your food photo", use_container_width=True)
            with col_desc:
                st.markdown("**What's in this photo?**")
                img_desc = st.text_area(
                    "Describe what you see",
                    placeholder="e.g. Grilled salmon fillet with steamed broccoli and quinoa on the side",
                    height=120,
                    key="img_desc",
                    label_visibility="collapsed",
                )
                if st.button("🔬 Analyse Photo Food", use_container_width=True):
                    if img_desc.strip():
                        with st.spinner("Analysing..."):
                            result = analyzer.analyze_from_description(img_desc.strip(), st.session_state.user_profile or None)
                        st.session_state.analysis_result = result
                        st.rerun()
                    else:
                        st.warning("Please describe what's in the photo.")

    # ── Label parser ──────────────────────────────────────────────────
    with tabs[2]:
        st.markdown("**Paste the text from a nutrition label or ingredient list:**")
        label_text = st.text_area(
            "Label text",
            placeholder="Paste the full nutrition facts panel or ingredient list here...\ne.g.\nServing size: 30g\nCalories: 120\nProtein: 3g\nCarbohydrates: 22g\n...",
            height=200,
            label_visibility="collapsed",
        )
        if st.button("🏷️ Decode Label", use_container_width=True):
            if label_text.strip():
                with st.spinner("🧐 Interpreting nutrition label with IBM Granite AI..."):
                    result = analyzer.analyze_grocery_label(label_text.strip())
                st.markdown("---")
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.markdown(result["analysis"])
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("Please paste some label text first.")


# ── Tab: Food Swaps ────────────────────────────────────────────────────────────
def render_food_swaps():
    st.markdown("## 🔄 Smart Food Swap Advisor")
    st.caption("Find healthier alternatives to your favourite foods, aligned with your goals")

    swap_recommender, swap_goals = get_swap_recommender()

    swap_tabs = st.tabs(["🎯 Goal-Based Swaps", "⚡ Quick Swap", "🍽️ Meal Makeover"])

    # ── Goal-based swaps ──────────────────────────────────────────────
    with swap_tabs[0]:
        col1, col2 = st.columns(2)
        with col1:
            food_item = st.text_input(
                "Food to swap",
                placeholder="e.g. white rice, butter, whole milk, white bread",
                key="swap_food",
            )
        with col2:
            swap_goal = st.selectbox("Swap goal", swap_goals, key="swap_goal")

        n_swaps = st.slider("Number of alternatives", 3, 7, 5)

        if st.button("🔄 Find Smart Swaps", use_container_width=True):
            if food_item.strip():
                with st.spinner("🧠 Finding the best alternatives with IBM Granite AI..."):
                    result = swap_recommender.get_swaps(
                        food_item.strip(), swap_goal, st.session_state.user_profile or None, n=n_swaps
                    )
                st.session_state.swap_result = result
            else:
                st.warning("Please enter a food item to swap.")

        if st.session_state.swap_result:
            st.markdown("---")
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown(st.session_state.swap_result)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Quick swap ────────────────────────────────────────────────────
    with swap_tabs[1]:
        st.markdown("Get a single quick and easy healthier swap instantly.")
        quick_food = st.text_input("What food do you want to swap?", placeholder="e.g. chips, soda, white pasta", key="quick_swap")

        # Popular quick swaps
        popular = ["Chips 🥔", "Soda 🥤", "White bread 🍞", "Mayonnaise 🫙", "Milk chocolate 🍫", "Ice cream 🍦"]
        st.markdown("**Popular swaps:**")
        p_cols = st.columns(6)
        for i, p in enumerate(popular):
            if p_cols[i].button(p, key=f"pop_{i}"):
                st.session_state["_pending_quick"] = p.split(" ")[0]

        if "_pending_quick" in st.session_state:
            quick_food = st.session_state.pop("_pending_quick")

        if st.button("⚡ Get Quick Swap", use_container_width=True, key="quick_btn"):
            if quick_food.strip():
                with st.spinner("Finding best swap..."):
                    result = swap_recommender.quick_swap(quick_food.strip())
                st.markdown("---")
                st.success(result)
            else:
                st.warning("Please enter a food item.")

    # ── Meal makeover ─────────────────────────────────────────────────
    with swap_tabs[2]:
        st.markdown("Transform an entire meal into a healthier version, component by component.")
        meal_desc = st.text_area(
            "Describe your meal",
            placeholder="e.g. Fried chicken breast with white rice, creamy coleslaw made with mayo, and a large glass of orange juice",
            height=120,
            key="meal_makeover",
            label_visibility="collapsed",
        )
        if st.button("✨ Give My Meal a Makeover", use_container_width=True):
            if meal_desc.strip():
                with st.spinner("🍽️ Creating your meal makeover with IBM Granite AI..."):
                    result = swap_recommender.meal_makeover(meal_desc.strip(), st.session_state.user_profile or None)
                st.markdown("---")
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.markdown(result)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("Please describe your meal.")


# ── Tab: Nutrition Encyclopedia ────────────────────────────────────────────────
def render_encyclopedia():
    st.markdown("## 🧠 Nutrition Encyclopedia")
    st.caption("Understand any nutrition concept in plain, practical English")

    agent = get_agent()

    # Popular topics
    popular_topics = {
        "Macronutrients": ["Protein", "Carbohydrates", "Healthy fats", "Dietary fibre"],
        "Micronutrients": ["Vitamin D", "Iron", "Omega-3 fatty acids", "Magnesium", "B12", "Zinc"],
        "Concepts": ["Glycaemic index", "Intermittent fasting", "Anti-inflammatory diet", "Gut microbiome", "Calorie deficit"],
        "Special": ["Protein for muscle building", "Nutrition for diabetes", "Foods for heart health", "Brain foods"],
    }

    col1, col2 = st.columns([2, 1])
    with col1:
        topic_input = st.text_input(
            "Search or type any nutrition topic",
            placeholder="e.g. vitamin B12, omega-3, glycaemic index, keto diet...",
            key="encyclopedia_topic",
        )
    with col2:
        st.markdown("")  # spacer

    st.markdown("**Or browse by category:**")
    for category, topics in popular_topics.items():
        with st.expander(f"📚 {category}", expanded=(category == "Macronutrients")):
            cols = st.columns(len(topics))
            for i, topic in enumerate(topics):
                if cols[i].button(topic, key=f"enc_{category}_{i}", use_container_width=True):
                    st.session_state["_pending_topic"] = topic

    if "_pending_topic" in st.session_state:
        topic_input = st.session_state.pop("_pending_topic")

    if st.button("📖 Explain This Topic", use_container_width=True) or (topic_input and st.session_state.get("_auto_explain")):
        if topic_input.strip():
            with st.spinner(f"📚 Researching {topic_input} with IBM Granite AI..."):
                result = agent.explain_nutrition(topic_input.strip())
            st.markdown("---")
            st.markdown(f"### 📖 {topic_input}")
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown(result)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Please enter a topic to explain.")


# ── Tab: Progress Coach ────────────────────────────────────────────────────────
def render_progress_coach():
    st.markdown("## 📈 Progress & Adaptation Coach")
    st.caption("Share how you're doing and get your plan dynamically adapted")

    agent = get_agent()

    if not st.session_state.user_profile:
        st.warning("👈 Please fill in your profile in the sidebar to get personalised coaching.")
        return

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📊 How have you been doing?")
        feedback = st.text_area(
            "Your feedback",
            placeholder="Tell me how your nutrition journey is going...\n\nFor example:\n- What's working well?\n- What challenges are you facing?\n- How is your energy / weight / digestion?\n- What did you eat this week?\n- What cravings have you had?",
            height=200,
            label_visibility="collapsed",
        )

    with col2:
        st.markdown("### 📋 Current plan summary (optional)")
        current_plan = st.text_area(
            "Current plan",
            placeholder="Briefly describe your current diet/plan...\n\nFor example:\n- Eating 1800 calories/day\n- High protein diet\n- Avoiding sugar\n- Working out 3x per week",
            height=200,
            label_visibility="collapsed",
        )

    # Progress check-in metrics
    st.markdown("### 📌 Quick Check-in")
    metric_cols = st.columns(4)
    energy_level = metric_cols[0].select_slider("⚡ Energy", options=["Very low", "Low", "Okay", "Good", "Excellent"], value="Okay")
    hunger_level = metric_cols[1].select_slider("🍽️ Hunger control", options=["Always hungry", "Often hungry", "Moderate", "Well controlled", "Never hungry"], value="Moderate")
    mood = metric_cols[2].select_slider("😊 Mood", options=["Poor", "Low", "Neutral", "Good", "Great"], value="Good")
    adherence = metric_cols[3].select_slider("✅ Plan adherence", options=["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"], value="60-80%")

    enhanced_feedback = f"""{feedback}

Check-in metrics:
- Energy level: {energy_level}
- Hunger control: {hunger_level}
- Mood: {mood}
- Plan adherence: {adherence}"""

    if st.button("🎯 Adapt My Plan", use_container_width=True):
        if feedback.strip():
            with st.spinner("💭 Analysing your progress and adapting your plan with IBM Granite AI..."):
                result = agent.adapt_plan(
                    enhanced_feedback,
                    current_plan or "No specific plan provided.",
                    st.session_state.user_profile,
                )
            st.markdown("---")
            st.markdown("### 🎯 Your Adapted Plan")
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown(result)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Please share some feedback about how you've been doing.")


# ── Main app ──────────────────────────────────────────────────────────────────
def main():
    inject_css()
    init_session()
    render_sidebar()

    # Check IBM credentials status
    ibm_key = os.getenv("IBM_API_KEY", "")
    if not ibm_key or ibm_key == "your_ibm_cloud_api_key_here":
        st.warning(
            "⚙️ **IBM watsonx.ai not configured.** The app is running in **demo mode**. "
            "Add your `IBM_API_KEY` and `WATSONX_PROJECT_ID` to the `.env` file to enable full AI features.",
            icon="⚠️",
        )

    # Main navigation tabs
    tab_labels = ["🏠 Home", "💬 Chat", "📅 Meal Plan", "🔍 Food Analyzer", "🔄 Food Swaps", "🧠 Encyclopedia", "📈 Progress"]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        render_home()
    with tabs[1]:
        render_chat()
    with tabs[2]:
        render_meal_plan()
    with tabs[3]:
        render_food_analyzer()
    with tabs[4]:
        render_food_swaps()
    with tabs[5]:
        render_encyclopedia()
    with tabs[6]:
        render_progress_coach()


if __name__ == "__main__":
    main()
