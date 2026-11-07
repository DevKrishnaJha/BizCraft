
DESIGN_SYSTEMS = {
    "modern-minimal": {
        "name": "Modern Minimal",
        "css": """
:root {
    --background: #f4f8f6;
    --surface: #ffffff;
    --text: #172b25;
    --muted: #687a72;
    --accent: #18745c;
    --border: #dce8e2;
    --container: 1160px;
}

body {
    font-family: Arial, Helvetica, sans-serif;
}

h1, h2, h3 {
    font-family: Arial, Helvetica, sans-serif;
    font-weight: 700;
    letter-spacing: -1.5px;
}

.site-header {
    background: rgba(255,255,255,0.95);
}

.section-hero {
    background: linear-gradient(135deg, #e6f2eb, #f8fbf9);
}

.service-card {
    border-radius: 14px;
    box-shadow: 0 5px 20px rgba(23,43,37,0.04);
}

.button {
    border-radius: 8px;
}

.site-footer {
    background: #172b25;
}
"""
    },

    "bold-vibrant": {
        "name": "Bold & Vibrant",
        "css": """
:root {
    --background: #fff9f1;
    --surface: #ffffff;
    --text: #291b16;
    --muted: #806d62;
    --accent: #e65d32;
    --border: #f0dfd1;
    --container: 1200px;
}

body {
    font-family: Arial, Helvetica, sans-serif;
}

h1, h2, h3 {
    font-family: Arial, Helvetica, sans-serif;
    font-weight: 800;
    letter-spacing: -2px;
}

.site-header {
    background: rgba(255,249,241,0.96);
}

.section-hero {
    background:
        radial-gradient(ellipse at 85% 20%, #ffd49e 0%, transparent 42%),
        linear-gradient(135deg, #fff0dc, #fff9f1);
}

.hero-content {
    max-width: 850px;
}

.button-primary {
    background: #e65d32;
    border-radius: 30px;
}

.button-primary:hover {
    background: #bd3f1c;
}

.service-card {
    border-radius: 20px;
    border: none;
    box-shadow: 0 8px 28px rgba(80,45,20,0.08);
}

.service-card:hover {
    box-shadow: 0 15px 35px rgba(80,45,20,0.13);
}

.site-footer {
    background: #291b16;
}
"""
    },

    "premium-elegant": {
        "name": "Premium Elegant",
        "css": """
:root {
    --background: #faf8f4;
    --surface: #ffffff;
    --text: #25221e;
    --muted: #827b70;
    --accent: #a1814e;
    --border: #e8e1d6;
    --container: 1100px;
}

body {
    font-family: Georgia, "Times New Roman", serif;
}

h1, h2, h3 {
    font-family: Georgia, "Times New Roman", serif;
    font-weight: 500;
    letter-spacing: -1px;
}

.site-header {
    background: rgba(250,248,244,0.96);
}

.section-hero {
    background:
        radial-gradient(ellipse at 80% 20%, #e8ddc9 0%, transparent 45%),
        #faf8f4;
}

.hero-content {
    max-width: 760px;
}

.eyebrow {
    letter-spacing: 3px;
}

.button-primary {
    background: #25221e;
    border-radius: 2px;
    padding: 16px 28px;
}

.button-primary:hover {
    background: #a1814e;
}

.service-card {
    border-radius: 2px;
    box-shadow: none;
    border-color: #e8e1d6;
}

.service-card:hover {
    box-shadow: 0 12px 30px rgba(0,0,0,0.06);
}

.site-footer {
    background: #25221e;
}
"""
    },
}


BUSINESS_STYLE_MAP = {
    "education": "modern-minimal",
    "professional_services": "modern-minimal",
    "healthcare": "modern-minimal",
    "restaurant": "bold-vibrant",
    "retail": "bold-vibrant",
    "beauty_wellness": "premium-elegant",
    "general_business": "modern-minimal",
}


def get_design_system(business_type: str) -> dict:
    style_id = BUSINESS_STYLE_MAP.get(
        business_type,
        "modern-minimal",
    )

    return {
        "id": style_id,
        **DESIGN_SYSTEMS[style_id],
    }
