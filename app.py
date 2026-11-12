import base64
import datetime
import os
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# 1. PAGE SETUP
st.set_page_config(
    page_title="IlishKhuji | ইলিশখুঁজি",
    page_icon="🌿",
    layout="wide",
)


def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None


# 2. SIDEBAR CONTROLS & LANGUAGE SWITCHER
st.sidebar.header("🌐 Language / ভাষা")
lang = st.sidebar.radio("Choose Interface Language", ["English", "বাংলা (Bangla)"])

st.sidebar.header("⚙️ Simulation & Rules")
selected_date = st.sidebar.date_input(
    "Select Date to Simulate" if lang == "English" else "তারিখ নির্বাচন করুন",
    datetime.date.today(),
)
chl_threshold = st.sidebar.slider(
    "Chl-a Threshold (mg/m³)" if lang == "English" else "ক্লোরোফিল-এ মাত্রা (mg/m³)",
    0.5,
    5.0,
    1.5,
)


# 3. BANGLADESH HILSA BAN PERIOD CHECKER (Checked early so page theme reacts!)
def check_ban_status(check_date):
    m, d = check_date.month, check_date.day
    # 22-day Mother Hilsa Spawning Ban (Oct 8 - Oct 29)
    if m == 10 and (8 <= d <= 29):
        return (
            True,
            "🚫 NATIONWIDE BAN ACTIVE: 22-Day Mother Hilsa Spawning Protection (Oct 8–29). Fishing, transport & sale strictly prohibited!"
            if lang == "English"
            else "🚫 দেশব্যাপী নিষেধাজ্ঞা চলমান: মা ইলিশ সংরক্ষণে ২২ দিনের অবরোধ (৮–২৯ অক্টোবর)। মাছ ধরা ও বিক্রি সম্পূর্ণ নিষিদ্ধ!",
        )
    # 58-day Bay of Bengal Marine Fishing Ban (Apr 15 - Jun 11)
    if (m == 4 and d >= 15) or (m == 5) or (m == 6 and d <= 11):
        return (
            True,
            "🚫 MARINE BAN ACTIVE: 58-Day Bay of Bengal Fishing Ban (Apr 15–Jun 11). All sea fishing vessels must remain ashore!"
            if lang == "English"
            else "🚫 সামুদ্রিক নিষেধাজ্ঞা চলমান: বঙ্গোপসাগরে ৫৮ দিনের মাছ ধরা বন্ধ (১৫ এপ্রিল–১১ জুন)।",
        )
    # Jatka Conservation Period (Mar 1 - Apr 30 in river sanctuaries)
    if m in [3, 4]:
        return (
            False,
            "⚠️ SANCTUARY WARNING: Jatka conservation period active in river sanctuaries (Mar–Apr).",
        )
    return (
        False,
        "✅ FISHING OPEN: No nationwide seasonal ban active on this date."
        if lang == "English"
        else "✅ মাছ ধরা অনুমোদিত: আজ কোনো মৌসুমী নিষেধাজ্ঞা নেই (লাল চিহ্নিত অভয়াশ্রম ব্যতীত)।",
    )


is_banned, ban_message = check_ban_status(selected_date)

# 4. DYNAMIC THEME & TRANSLUCENT LEAF + FISH BACKGROUND PATTERN
if is_banned:
    # Full-page Red Alert Mode during Ban Period
    page_bg_color = "#ffe5e8"
    sidebar_bg_color = "#ffccd5"
    pattern_stroke = "%23d90429"
    banner_gradient = "linear-gradient(135deg, #590d22 0%, #a4133c 50%, #ff4d6d 100%)"
    card_border = "#d90429"
    card_bg = "rgba(255, 240, 243, 0.92)"
    text_primary = "#590d22"
else:
    # Soft Light Green Page with Translucent Leaf & Fish Prints + Distinct Sidebar
    page_bg_color = "#f1faee"
    sidebar_bg_color = "#d8f3dc"
    pattern_stroke = "%232d6a4f"
    banner_gradient = "linear-gradient(135deg, #1b4332 0%, #2d6a4f 45%, #52b788 80%, #95d5b2 100%)"
    card_border = "#2d6a4f"
    card_bg = "rgba(255, 255, 255, 0.88)"
    text_primary = "#1b4332"

# Repeating translucent SVG tile with small leaves & fish
svg_pattern = (
    f"data:image/svg+xml,%3Csvg width='140' height='140' viewBox='0 0 140 140' xmlns='http://www.w3.org/2000/svg'%3E"
    f"%3Cg fill='none' stroke='{pattern_stroke}' stroke-width='1.4' stroke-opacity='0.11'%3E"
    # Small Leaf 1
    f"%3Cpath d='M25 35 Q40 15 55 35 Q40 55 25 35 Z'/%3E%3Cline x1='25' y1='35' x2='55' y2='35'/%3E"
    # Small Fish 1
    f"%3Cpath d='M85 40 Q102 27 118 40 Q102 53 85 40 Z'/%3E%3Cpolygon points='118,40 128,33 128,47'/%3E%3Ccircle cx='92' cy='39' r='1'/%3E"
    # Small Fish 2
    f"%3Cpath d='M20 100 Q37 87 53 100 Q37 113 20 100 Z'/%3E%3Cpolygon points='53,100 63,93 63,107'/%3E%3Ccircle cx='27' cy='99' r='1'/%3E"
    # Small Leaf 2
    f"%3Cpath d='M88 105 Q103 85 118 105 Q103 125 88 105 Z'/%3E%3Cline x1='88' y1='105' x2='118' y2='105'/%3E"
    f"%3C/g%3E%3C/svg%3E"
)

st.markdown(
    f"""
    <style>
    /* Main scrolling area with soft green/red color + translucent leaf & fish pattern */
    [data-testid="stAppViewContainer"] {{
        background-color: {page_bg_color};
        background-image: url("{svg_pattern}");
        background-repeat: repeat;
    }}
    [data-testid="stHeader"] {{
        background-color: rgba(0, 0, 0, 0);
    }}
    /* Distinct Sidebar Background */
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg_color};
        border-right: 2px solid {card_border}33;
    }}
    /* Hero Banner */
    .hero-banner {{
        background: {banner_gradient};
        padding: 28px 36px;
        border-radius: 20px;
        color: white;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 20px;
        box-shadow: 0 10px 26px rgba(0, 0, 0, 0.18);
        margin-bottom: 20px;
    }}
    .hero-text {{
        flex: 1;
    }}
    .hero-text h1 {{
        margin: 0;
        font-size: 2.6rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
    }}
    .hero-motto {{
        margin: 8px 0 10px 0;
        font-size: 1.25rem;
        font-style: italic;
        font-weight: 500;
        color: #f8f9fa;
        letter-spacing: 0.3px;
    }}
    .hero-sub {{
        margin: 0;
        font-size: 0.98rem;
        color: #ffffff;
        opacity: 0.92;
    }}
    .badge {{
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-bottom: 10px;
        letter-spacing: 0.6px;
        color: #ffffff;
    }}
    /* 3x Larger Hilsa Image */
    .hilsa-logo {{
        max-height: 330px;
        max-width: 420px;
        width: auto;
        object-fit: contain;
        filter: drop-shadow(0 10px 18px rgba(0, 0, 0, 0.32));
    }}
    .legend-box {{
        background-color: {card_bg};
        border-left: 6px solid {card_border};
        padding: 13px 18px;
        border-radius: 10px;
        margin-bottom: 14px;
        color: {text_primary};
        font-size: 0.96rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}
    .rule-card {{
        background-color: {card_bg};
        border-top: 5px solid {card_border};
        border-radius: 14px;
        padding: 20px 22px;
        height: 100%;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
        color: {text_primary};
    }}
    .rule-card h4 {{
        margin-top: 0;
        color: {text_primary};
        font-weight: 700;
    }}
    .custom-footer {{
        margin-top: 40px;
        background: {banner_gradient};
        color: #ffffff;
        padding: 24px 30px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.15);
    }}
    .custom-footer a {{
        color: #d8f3dc;
        text-decoration: underline;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# 5. HERO HEADING WITH MOTTO & 3X HILSA.PNG
title_text = "IlishKhuji" if lang == "English" else "ইলিশখুঁজি (IlishKhuji)"
motto_text = (
    "“Guiding Every Cast with Science, Safety & Stewardship.”"
    if lang == "English"
    else "“বিজ্ঞান, নিরাপত্তা ও সংরক্ষণের আলোয় নিরাপদ প্রতিটি জাল।”"
)
subtitle_text = (
    "AI-Guided, Conservation-Aware Hilsa Fishing Advisory • Meghna Estuary & Bay of Bengal"
    if lang == "English"
    else "মেঘনা মোহনা ও বঙ্গোপসাগরে সংরক্ষণ-সচেতন স্মার্ট ইলিশ অনুসন্ধান নির্দেশিকা"
)

img_base64 = get_base64_image("hilsa.png")
if img_base64:
    right_visual = f'<img src="data:image/png;base64,{img_base64}" class="hilsa-logo" alt="Hilsa">'
else:
    right_visual = '<div style="color:#ffffff; font-size:0.9rem;">(Save image as <b>hilsa.png</b> in project folder)</div>'

st.markdown(
    f"""
    <div class="hero-banner">
        <div class="hero-text">
            <div class="badge">BMU BLUE AI CHALLENGE 2026–27</div>
            <h1>{title_text}</h1>
            <div class="hero-motto">{motto_text}</div>
            <p class="hero-sub">{subtitle_text}</p>
        </div>
        <div>{right_visual}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Display Active Ban / Open Banner
if is_banned:
    st.error(ban_message)
else:
    st.success(ban_message)


# 6. FETCH NEAR-REAL-TIME NASA MODIS CHLOROPHYLL-A DATA
@st.cache_data(ttl=3600)
def fetch_nasa_chla():
    url = (
        "https://coastwatch.pfeg.noaa.gov/erddap/griddap/erdMH1chla8day.csv?"
        "chlorophyll[(last)][(20.5):(22.8)][(89.5):(92.2)]"
    )
    try:
        df = pd.read_csv(url, skiprows=[1])
        df = df.dropna(subset=["chlorophyll"])
        return df, "Live NASA Aqua MODIS (8-Day NRT Composite)"
    except Exception:
        fallback = pd.DataFrame({
            "latitude": [21.8, 21.5, 21.2, 22.1, 20.9, 21.6, 22.3],
            "longitude": [90.8, 91.1, 90.4, 90.6, 91.5, 90.1, 90.9],
            "chlorophyll": [2.8, 3.4, 1.9, 2.2, 0.8, 3.1, 1.4],
        })
        return fallback, "Cached Fallback Dataset (Offline Demo Mode)"


df_chl, data_source = fetch_nasa_chla()

# 7. MAP LEGEND BAR
st.markdown(
    """
    <div class="legend-box">
        <b>🗺️ Map Guide:</b> &nbsp;&nbsp;
        🟢 <b>Green Circles</b> = High Chlorophyll-a (Favorable Hilsa Feeding Zone) &nbsp;|&nbsp;
        🟥 <b>Red Zones</b> = Protected MPA / Sanctuary (Automatically Excluded)
    </div>
    """,
    unsafe_allow_html=True,
)

# 8. DEFINE MPAs & SANCTUARIES
restricted_zones = [
    {
        "name": "Nijhum Dwip Marine Protected Area (MPA)",
        "bounds": [[21.85, 90.85], [22.15, 91.15]],
        "rule": "Strict MPA — Fishing Restricted",
    },
    {
        "name": "Swatch of No-Ground MPA",
        "bounds": [[21.10, 89.55], [21.55, 89.95]],
        "rule": "Marine Protected Area — No Fishing",
    },
    {
        "name": "Lower Meghna Hilsa Sanctuary (Chandpur–Laxmipur)",
        "bounds": [[22.40, 90.60], [22.85, 90.80]],
        "rule": "Hilsa Sanctuary (Closed Mar–Apr)",
    },
]


def is_inside_mpa(lat, lon):
    for zone in restricted_zones:
        (min_lat, min_lon), (max_lat, max_lon) = zone["bounds"]
        if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
            return True
    return False


# 9. BUILD THE INTERACTIVE MAP
m = folium.Map(location=[21.75, 90.85], zoom_start=8, tiles="OpenStreetMap")

for zone in restricted_zones:
    folium.Rectangle(
        bounds=zone["bounds"],
        color="#d90429",
        fill=True,
        fill_color="#d90429",
        fill_opacity=0.38,
        popup=f"<b>{zone['name']}</b><br>{zone['rule']}",
        tooltip=f"🚫 {zone['name']}",
    ).add_to(m)

recommended_count = 0
if not is_banned:
    for _, row in df_chl.iterrows():
        lat, lon, chl = row["latitude"], row["longitude"], row["chlorophyll"]
        if is_inside_mpa(lat, lon):
            continue
        if chl >= chl_threshold:
            recommended_count += 1
            folium.CircleMarker(
                location=[lat, lon],
                radius=7,
                color="#1b4332",
                fill=True,
                fill_color="#40916c",
                fill_opacity=0.82,
                popup=(
                    f"<b>High Hilsa Suitability</b><br>Chl-a: {chl:.2f}"
                    f" mg/m³<br>Coords: {lat:.2f}°N, {lon:.2f}°E"
                ),
            ).add_to(m)

st_folium(m, width=1200, height=520)

# 10. SUMMARY METRICS
col1, col2, col3 = st.columns(3)
col1.metric("🟢 Recommended Safe Zones", recommended_count)
col2.metric("🟥 Protected Zones Masked", len(restricted_zones))
col3.metric("⚖️ Legal Status", "CLOSED (BAN ACTIVE)" if is_banned else "OPEN")
st.caption(f"📡 **Satellite Feed:** {data_source} • Total grid points analyzed: {len(df_chl)}")

st.markdown("---")

# 11. SCROLLABLE HILSA CONSERVATION & FISHERIES GUIDELINES
st.subheader(
    "📘 Hilsa Conservation Rules & Fisher Guidelines (Bangladesh Fisheries Act)"
    if lang == "English"
    else "📘 ইলিশ সংরক্ষণ আইন ও মৎস্যজীবীদের জন্য নির্দেশিকা"
)

g1, g2 = st.columns(2)
with g1:
    st.markdown(
        """
        <div class="rule-card">
            <h4>🗓️ 1. Official Ban Periods (অবরোধের সময়কাল)</h4>
            <ul>
                <li><b>22-Day Mother Hilsa Ban (Oct 8–29):</b> Protects brood hilsa during peak monsoon spawning migration. Catching, landing, transporting, and selling hilsa is strictly illegal nationwide.</li>
                <li><b>58-Day Marine Ban (Apr 15–Jun 11):</b> Protects breeding stocks and juveniles in the Bay of Bengal.</li>
                <li><b>Jatka Sanctuary Closure (Mar 1–Apr 30):</b> Fishing is banned in designated Meghna, Padma, Tetulia, and Andharmanik river sanctuaries.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

with g2:
    st.markdown(
        """
        <div class="rule-card">
            <h4>📏 2. Minimum Legal Size (MLS) & Mesh Size (জালের ফাঁস ও আকার)</h4>
            <ul>
                <li><b>Minimum Legal Size (MLS):</b> Hilsa smaller than <b>25 cm (approx. 10 inches)</b> are legally classified as <i>Jatka</i>. Catching, possessing, or selling Jatka is a punishable offense.</li>
                <li><b>Legal Gillnet Mesh Size:</b> Net mesh size must be at least <b>6.5 cm (2.6 inches)</b> stretched mesh so juvenile fish can escape safely.</li>
                <li><b>Monofilament Net Ban:</b> Fine-mesh <i>Current Jal</i> (কারেন্ট জাল) is completely banned under the Protection and Conservation of Fish Act.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
g3, g4 = st.columns(2)
with g3:
    st.markdown(
        """
        <div class="rule-card">
            <h4>🌊 3. Marine Protected Areas (MPAs) & Sanctuaries</h4>
            <ul>
                <li><b>Zero-Take & Restricted Zones:</b> Nijhum Dwip MPA, Swatch of No-Ground MPA, and river sanctuaries serve as nursery and breeding refuges.</li>
                <li><b>Automated Protection:</b> IlishKhuji automatically masks out all restricted polygons so fishers never accidentally drift into prohibited waters.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

with g4:
    st.markdown(
        """
        <div class="rule-card">
            <h4>🌱 4. Why These Rules Are Necessary (কেন সংরক্ষণ জরুরি?)</h4>
            <ul>
                <li><b>100x Growth Multiplication:</b> A 15-gram <i>Jatka</i> protected for just 6–8 months grows into a 1.0–1.5 kg adult Hilsa—multiplying fisher income over 60×.</li>
                <li><b>Millions of Eggs Saved:</b> A single mature female Hilsa lays 1.5 to 2 million eggs during the October spawning window.</li>
                <li><b>Fuel & Safety Savings:</b> Combining legal compliance with satellite chlorophyll data cuts wasted fuel and protects coastal livelihoods.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

# 12. CREATOR FOOTER (Edit your name, phone & email below!)
st.markdown(
    """
    <div class="custom-footer">
        <h4 style="margin:0 0 6px 0; color:#ffffff;">🐟 IlishKhuji — BMU Blue AI Challenge 2026–27</h4>
        <p style="margin:4px 0; font-size:0.95rem;">
            <b>Created by:</b> Tahsin Mahmud Tamanna &nbsp;|&nbsp;
            <b> Bangladesh Maritime University
        </p>
        <p style="margin:4px 0; font-size:0.92rem;">
            📞 <b>Phone:</b> +880 1XXX-XXXXXX &nbsp;|&nbsp;
            ✉️ <b>Email:</b> your.email@example.com
        </p>
        <p style="margin:8px 0 0 0; font-size:0.8rem; opacity:0.85;">
            Data Powered by NASA Aqua MODIS (NOAA ERDDAP) & OpenStreetMap • Built with Python & Streamlit
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)