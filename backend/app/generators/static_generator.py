
import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse
from app.generators.design_systems import get_design_system


PROJECTS_DIR = Path(__file__).resolve().parents[2] / "projects"


def escape(value) -> str:
    """Safely escape business-provided text before inserting it into HTML."""
    return html.escape(str(value or ""), quote=True)


def safe_url(value: str | None) -> str:
    """Allow only HTTP and HTTPS URLs."""
    if not value:
        return ""

    value = value.strip()
    parsed = urlparse(value)

    if parsed.scheme not in {"http", "https"}:
        return ""

    if not parsed.hostname:
        return ""

    return escape(value)


def safe_section_id(value: str) -> str:
    """Create a predictable HTML section identifier."""
    result = re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-")
    return result or "section"


def render_services(services: list) -> str:
    if not services:
        return """
        <div class="empty-content">
            Services and offerings will be added by the business owner.
        </div>
        """

    cards = []

    for service in services:
        cards.append(
            f"""
            <article class="service-card">
                <div class="service-icon">✦</div>
                <h3>{escape(service)}</h3>
            </article>
            """
        )

    return "\n".join(cards)


def render_section(section: dict, business: dict) -> str:
    name = section.get("name", "Section")
    section_type = section.get("type", "custom")
    section_id = safe_section_id(name)

    description = escape(business.get("description"))
    business_name = escape(business.get("business_name"))
    services = business.get("services") or []

    content = ""

    if section_type == "hero":
        content = f"""
        <div class="hero-content">
            <span class="eyebrow">{escape(business.get("category"))}</span>
            <h1>{business_name}</h1>
            <p>{description or "Discover more about our business and what we offer."}</p>
            <a href="#contact" class="button button-primary">
                Contact Us <span>→</span>
            </a>
        </div>
        """

    elif section_type == "about":
        content = f"""
        <div class="about-content">
            <div>
                <span class="eyebrow">ABOUT US</span>
                <h2>Get to know us.</h2>
            </div>
            <p>{description or "Business information will be added by the owner."}</p>
        </div>
        """

    elif section_type in {"offerings", "services"}:
        content = f"""
        <div class="section-heading">
            <span class="eyebrow">WHAT WE OFFER</span>
            <h2>{escape(name)}</h2>
        </div>
        <div class="service-grid">
            {render_services(services)}
        </div>
        """

    elif section_type == "contact":
        phone = business.get("phone")
        email = business.get("email")

        contact_items = []

        if phone:
            safe_phone = re.sub(r"[^0-9+]", "", str(phone))
            if safe_phone:
                contact_items.append(
                    f'<a href="tel:{escape(safe_phone)}">{escape(phone)}</a>'
                )

        if email:
            safe_email = escape(email)
            contact_items.append(
                f'<a href="mailto:{safe_email}">{safe_email}</a>'
            )

        contact_html = "".join(
            f'<div class="contact-item">{item}</div>'
            for item in contact_items
        )

        if not contact_html:
            contact_html = """
            <p class="empty-content">
                Contact information will be added by the business owner.
            </p>
            """

        content = f"""
        <div class="contact-content">
            <span class="eyebrow">GET IN TOUCH</span>
            <h2>Let's connect.</h2>
            <div class="contact-list">{contact_html}</div>
        </div>
        """

    elif section_type == "location":
        maps_url = safe_url(business.get("google_maps_url"))

        map_link = ""

        if maps_url:
            map_link = f"""
            <a class="text-link" href="{maps_url}"
               target="_blank" rel="noopener noreferrer">
                View on Google Maps ↗
            </a>
            """

        content = f"""
        <div class="location-content">
            <span class="eyebrow">FIND US</span>
            <h2>Visit our location.</h2>
            <p>{escape(business.get("location"))}</p>
            {map_link}
        </div>
        """

    elif section_type == "hours":
        content = f"""
        <div class="hours-content">
            <span class="eyebrow">WHEN WE'RE OPEN</span>
            <h2>Opening hours</h2>
            <p>{escape(business.get("opening_hours")) or "Hours to be confirmed."}</p>
        </div>
        """

    else:
        content = f"""
        <div class="section-heading">
            <span class="eyebrow">{escape(name)}</span>
            <h2>{escape(name)}</h2>
            <p>{escape(section.get("purpose"))}</p>
            <div class="empty-content">
                This section is ready for content supplied by the business owner.
            </div>
        </div>
        """

    return f"""
    <section class="content-section section-{escape(section_type)}"
             id="{escape(section_id)}">
        <div class="container">
            {content}
        </div>
    </section>
    """


def generate_html(business: dict, blueprint: dict) -> str:
    business_name = escape(business.get("business_name"))
    category = escape(business.get("category"))
    description = escape(business.get("description"))

    website_url = safe_url(business.get("website"))

    # Safely retrieve the first page's sections.
    pages = blueprint.get("website", {}).get("pages") or []
    sections = pages[0].get("sections", []) if pages else []

    design_id = blueprint.get("design", {}).get(
        "system_id",
        "modern-minimal",
    )

    allowed_designs = {
        "modern-minimal",
        "bold-vibrant",
        "premium-elegant",
    }

    if design_id not in allowed_designs:
        design_id = "modern-minimal"

    navigation = []

    for section in sections:
        name = section.get("name", "Section")

        if name.lower() == "home":
            continue

        section_id = safe_section_id(name)

        navigation.append(
            f'<a href="#{escape(section_id)}">{escape(name)}</a>'
        )

    navigation_html = "\n".join(navigation)

    section_html = "\n".join(
        render_section(section, business)
        for section in sections
    )

    website_link = ""

    if website_url:
        website_link = f"""
        <a href="{website_url}" target="_blank"
           rel="noopener noreferrer">Existing website</a>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{description or category}">
    <title>{business_name}</title>
    <link rel="stylesheet" href="css/style.css">
</head>

<body class="design-{design_id}">
    <header class="site-header">
        <div class="container nav-container">
            <a href="#" class="brand">{business_name}</a>

            <button class="menu-toggle"
                    id="menuToggle"
                    aria-label="Toggle navigation"
                    aria-expanded="false">
                <span></span>
                <span></span>
            </button>

            <nav class="navigation" id="navigation">
                {navigation_html}
            </nav>
        </div>
    </header>

    <main>
        {section_html}
    </main>

    <footer class="site-footer">
        <div class="container footer-content">
            <div>
                <h3>{business_name}</h3>
                <p>{category}</p>
            </div>

            <div class="footer-links">
                {website_link}
            </div>

            <p class="copyright">
                © <span id="currentYear"></span> {business_name}
            </p>
        </div>
    </footer>

    <script src="js/script.js"></script>
</body>
</html>
"""


def generate_css(blueprint: dict) -> str:
    base_css = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');

:root {
    --background: #faf9f6;
    --surface: #ffffff;
    --text: #20201f;
    --muted: #77746e;
    --accent: #9b8055;
    --border: #e9e6df;
    --container: 1120px;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html {
    scroll-behavior: smooth;
    scroll-padding-top: 90px;
}

body {
    font-family: 'DM Sans', sans-serif;
    background: var(--background);
    color: var(--text);
    line-height: 1.7;
}

a {
    color: inherit;
    text-decoration: none;
}

.container {
    width: min(var(--container), 90%);
    margin: 0 auto;
}

.site-header {
    position: sticky;
    top: 0;
    z-index: 100;
    background: rgba(250, 249, 246, 0.94);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid var(--border);
}

.nav-container {
    min-height: 76px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 30px;
}

.brand {
    font-size: 20px;
    font-weight: 700;
    letter-spacing: -0.8px;
}

.navigation {
    display: flex;
    align-items: center;
    gap: 28px;
}

.navigation a,
.footer-links a {
    font-size: 13px;
    color: var(--muted);
    transition: color 0.2s;
}

.navigation a:hover,
.footer-links a:hover {
    color: var(--accent);
}

.menu-toggle {
    display: none;
    background: none;
    border: 0;
    cursor: pointer;
}

.menu-toggle span {
    display: block;
    width: 24px;
    height: 2px;
    margin: 5px;
    background: var(--text);
}

.content-section {
    padding: 100px 0;
    border-bottom: 1px solid var(--border);
}

.section-hero {
    min-height: 620px;
    display: flex;
    align-items: center;
    background:
        radial-gradient(ellipse at 80% 20%, #e8dfce 0%, transparent 45%),
        var(--background);
}

.hero-content {
    max-width: 760px;
}

.eyebrow {
    display: inline-block;
    margin-bottom: 20px;
    color: var(--accent);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
}

h1, h2, h3 {
    font-family: 'Playfair Display', serif;
    line-height: 1.15;
}

h1 {
    max-width: 750px;
    font-size: clamp(44px, 8vw, 82px);
    letter-spacing: -2px;
}

h2 {
    font-size: clamp(34px, 5vw, 50px);
    letter-spacing: -1px;
}

.hero-content > p {
    max-width: 590px;
    margin: 25px 0 32px;
    color: var(--muted);
    font-size: 16px;
}

.button {
    display: inline-flex;
    align-items: center;
    gap: 20px;
    padding: 14px 23px;
    font-size: 13px;
    font-weight: 600;
    transition: transform 0.2s, background 0.2s;
}

.button:hover {
    transform: translateY(-2px);
}

.button-primary {
    background: var(--text);
    color: white;
}

.button-primary:hover {
    background: var(--accent);
}

.about-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 80px;
    align-items: start;
}

.about-content > p,
.location-content > p,
.hours-content > p {
    color: var(--muted);
    font-size: 16px;
    white-space: pre-line;
}

.section-heading {
    margin-bottom: 45px;
}

.section-heading > p {
    margin-top: 15px;
    color: var(--muted);
}

.service-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 18px;
}

.service-card {
    padding: 30px;
    min-height: 150px;
    background: var(--surface);
    border: 1px solid var(--border);
    transition: transform 0.2s, box-shadow 0.2s;
}

.service-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(0,0,0,0.05);
}

.service-icon {
    margin-bottom: 20px;
    color: var(--accent);
}

.service-card h3 {
    font-size: 22px;
}

.contact-content,
.location-content,
.hours-content {
    max-width: 650px;
}

.contact-list {
    display: grid;
    gap: 15px;
    margin-top: 30px;
}

.contact-item a {
    color: var(--accent);
    font-weight: 600;
}

.text-link {
    display: inline-block;
    margin-top: 20px;
    color: var(--accent);
    font-weight: 600;
}

.empty-content {
    margin-top: 20px;
    padding: 18px;
    border: 1px dashed var(--border);
    color: var(--muted);
    font-size: 13px;
}

.site-footer {
    padding: 55px 0;
    background: #20201f;
    color: white;
}

.footer-content {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 25px;
}

.footer-content h3 {
    font-size: 22px;
}

.footer-content p,
.footer-links a {
    color: #aaa69e;
    font-size: 12px;
}

@media (max-width: 760px) {
    .nav-container {
        min-height: 68px;
    }

    .menu-toggle {
        display: block;
    }

    .navigation {
        display: none;
        position: absolute;
        top: 68px;
        left: 0;
        right: 0;
        padding: 22px 5%;
        background: var(--background);
        border-bottom: 1px solid var(--border);
        flex-direction: column;
        align-items: flex-start;
        gap: 18px;
    }

    .navigation.open {
        display: flex;
    }

    .content-section {
        padding: 75px 0;
    }

    .section-hero {
        min-height: 530px;
    }

    .about-content {
        grid-template-columns: 1fr;
        gap: 25px;
    }

    .footer-content {
        align-items: flex-start;
        flex-direction: column;
    }
}
"""
    design_styles = {

        "modern-minimal": """
body {
    background: #f8fafc;
    color: #172033;
}

.site-header {
    background: rgba(248, 250, 252, 0.94);
}

h1, h2, h3 {
    font-family: 'DM Sans', sans-serif;
    font-weight: 700;
}

.section-hero {
    background:
        radial-gradient(circle at 80% 20%, #dbeafe, transparent 45%),
        #f8fafc;
}

.eyebrow {
    color: #2563eb;
}

.button-primary {
    background: #2563eb;
    border-radius: 8px;
}

.button-primary:hover {
    background: #1d4ed8;
}

.service-card {
    border-radius: 14px;
    box-shadow: 0 8px 25px rgba(15, 23, 42, 0.04);
}
""",

        "bold-vibrant": """
body {
    background: #fff9f1;
    color: #21170f;
}

.site-header {
    background: #21170f;
    border-bottom: none;
}

.brand,
.navigation a {
    color: #ffffff;
}

.navigation a:hover {
    color: #ffb36b;
}
@media (max-width: 760px) {
    .design-bold-vibrant .navigation {
        background: #21170f;
        border-bottom: 1px solid rgba(255, 255, 255, 0.16);
    }

    .design-bold-vibrant .navigation a {
        color: #ffffff;
    }

    .design-bold-vibrant .navigation a:hover {
        color: #ffb36b;
    }

    .design-bold-vibrant .menu-toggle span {
        background: #ffffff;
    }
}
h1, h2, h3 {
    font-family: 'DM Sans', sans-serif;
    font-weight: 800;
    letter-spacing: -1px;
}

.section-hero {
    min-height: 680px;
    background:
        radial-gradient(circle at 85% 20%, #ffb36b, transparent 35%),
        #f05a28;
    color: #ffffff;
}

.section-hero .eyebrow {
    color: #ffe0a8;
}

.hero-content > p {
    color: #fff0e6;
}

.button-primary {
    background: #ffffff;
    color: #21170f;
    border-radius: 999px;
}

.button-primary:hover {
    background: #ffe0a8;
    color: #21170f;
}

.service-card {
    background: #21170f;
    color: #ffffff;
    border: none;
    border-radius: 16px;
}

.service-card h3 {
    color: #ffffff;
}

.service-icon,
.eyebrow {
    color: #f05a28;
}

.site-footer {
    background: #f05a28;
    color: #ffffff;
}
""",

        "premium-elegant": """
body {
    background: #f7f3ef;
    color: #30251f;
}

.site-header {
    background: rgba(247, 243, 239, 0.96);
}

h1, h2, h3 {
    font-family: 'Playfair Display', serif;
    font-weight: 500;
}

.section-hero {
    min-height: 700px;
    background:
        radial-gradient(ellipse at 75% 20%, #e8d7c8, transparent 45%),
        #f7f3ef;
}

.hero-content {
    max-width: 800px;
}

.hero-content h1 {
    font-size: clamp(48px, 8vw, 92px);
    letter-spacing: -2px;
}

.eyebrow {
    color: #9a7054;
    letter-spacing: 3px;
}

.button-primary {
    background: #30251f;
    border-radius: 2px;
    padding: 16px 30px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.button-primary:hover {
    background: #9a7054;
}

.service-card {
    background: #fffdfb;
    border: 1px solid #e8ddd4;
    border-radius: 2px;
    padding: 38px;
    box-shadow: none;
}

.service-card:hover {
    box-shadow: 0 15px 35px rgba(48, 37, 31, 0.07);
}

.site-footer {
    background: #30251f;
}
"""

    }

    design_id = blueprint.get("design", {}).get(
        "system_id",
        "modern-minimal"
    )

    selected_style = design_styles.get(
        design_id,
        design_styles["modern-minimal"]
    )

    return base_css + "\n" + selected_style


def generate_javascript() -> str:
    return """
const menuToggle = document.getElementById("menuToggle");
const navigation = document.getElementById("navigation");

if (menuToggle && navigation) {
    menuToggle.addEventListener("click", () => {
        const isOpen = navigation.classList.toggle("open");

        menuToggle.setAttribute(
            "aria-expanded",
            String(isOpen)
        );
    });

    navigation.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => {
            navigation.classList.remove("open");
            menuToggle.setAttribute("aria-expanded", "false");
        });
    });
}

const yearElement = document.getElementById("currentYear");

if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
}
"""

def generate_static_website(
    business: dict,
    blueprint: dict,
) -> dict:
    """
    Generate an independent static website project.

    Returns project metadata and relative file paths.
    """

    business_id = str(business.get("id", ""))

    # Business IDs are UUIDs. Reject anything else to prevent
    # directory traversal through an unexpected identifier.
    if not re.fullmatch(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{12}",
        business_id,
    ):
        raise ValueError("Invalid business ID.")

    project_dir = PROJECTS_DIR / business_id

    css_dir = project_dir / "css"
    js_dir = project_dir / "js"

    css_dir.mkdir(parents=True, exist_ok=True)
    js_dir.mkdir(parents=True, exist_ok=True)

    print("BIZCRAFT DESIGN:", blueprint.get("design"))
    
    html_content = generate_html(business, blueprint)
    css_content = generate_css(blueprint)
    js_content = generate_javascript()

    (project_dir / "index.html").write_text(
        html_content,
        encoding="utf-8",
    )

    (css_dir / "style.css").write_text(
        css_content,
        encoding="utf-8",
    )

    (js_dir / "script.js").write_text(
        js_content,
        encoding="utf-8",
    )

    metadata = {
    "business_id": business_id,
    "business_name": business["business_name"],
    "project_directory": str(project_dir),
    "selected_design_id": blueprint.get(
        "design", {}
    ).get("system_id", "modern-minimal"),
    "selected_design_name": blueprint.get(
        "design", {}
    ).get("name", "Modern Minimal"),
    "files": [
        "index.html",
        "css/style.css",
        "js/script.js",
    ],
    "status": "generated",
}

    (project_dir / "project.json").write_text(
        json.dumps(metadata, indent=4),
        encoding="utf-8",
    )

    return metadata
