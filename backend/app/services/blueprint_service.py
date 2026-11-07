
from app.services.analysis_service import analyze_business


SECTION_GUIDES = {
    "home": {
        "type": "hero",
        "purpose": "Introduce the business and communicate its main offering.",
        "content_required": ["business_name", "description"],
        "layout": "Hero section with headline, supporting text and primary CTA.",
    },
    "about": {
        "type": "about",
        "purpose": "Explain the business and establish its identity.",
        "content_required": ["description"],
        "layout": "Text and image split layout.",
    },
    "courses": {
        "type": "offerings",
        "purpose": "Present courses and educational programmes.",
        "content_required": ["services"],
        "layout": "Course cards with names and descriptions.",
    },
    "services": {
        "type": "services",
        "purpose": "Explain the services provided.",
        "content_required": ["services"],
        "layout": "Responsive service cards.",
    },
    "services and offerings": {
        "type": "services",
        "purpose": "Showcase the products or services offered.",
        "content_required": ["services"],
        "layout": "Responsive offering cards.",
    },
    "faculty": {
        "type": "team",
        "purpose": "Introduce teachers and their verified qualifications.",
        "content_required": ["faculty_profiles"],
        "layout": "Team profile cards.",
    },
    "results": {
        "type": "achievements",
        "purpose": "Display verified academic results and achievements.",
        "content_required": ["verified_results"],
        "layout": "Achievement highlights with supporting evidence.",
    },
    "admissions": {
        "type": "admissions",
        "purpose": "Explain the admission process.",
        "content_required": ["admission_process", "contact_information"],
        "layout": "Step-by-step admission information with an enquiry CTA.",
    },
    "menu": {
        "type": "menu",
        "purpose": "Present food and drinks available.",
        "content_required": ["menu_items", "menu_prices"],
        "layout": "Categorised menu with item descriptions.",
    },
    "gallery": {
        "type": "gallery",
        "purpose": "Show genuine photographs of the business.",
        "content_required": ["business_photographs"],
        "layout": "Responsive image gallery.",
    },
    "products": {
        "type": "products",
        "purpose": "Showcase available products.",
        "content_required": ["product_details", "product_images"],
        "layout": "Product cards with images and descriptions.",
    },
    "collections": {
        "type": "collections",
        "purpose": "Organise products into categories.",
        "content_required": ["product_categories"],
        "layout": "Visual category grid.",
    },
    "visit us": {
        "type": "visit",
        "purpose": "Encourage customers to visit the business.",
        "content_required": ["location", "opening_hours"],
        "layout": "Location information with directions link.",
    },
    "location": {
        "type": "location",
        "purpose": "Help visitors find the business.",
        "content_required": ["location"],
        "layout": "Address and map-link section.",
    },
    "opening hours": {
        "type": "hours",
        "purpose": "Show when the business is available.",
        "content_required": ["opening_hours"],
        "layout": "Readable weekly opening-hours display.",
    },
    "contact": {
        "type": "contact",
        "purpose": "Give visitors a way to contact the business.",
        "content_required": ["contact_information"],
        "layout": "Contact details and enquiry CTA.",
    },
    "contact and booking": {
        "type": "contact",
        "purpose": "Explain how customers can make enquiries or bookings.",
        "content_required": ["contact_information"],
        "layout": "Contact information with an enquiry CTA.",
    },
    "appointments": {
        "type": "appointments",
        "purpose": "Explain how customers can request appointments.",
        "content_required": ["appointment_information", "contact_information"],
        "layout": "Appointment information and contact CTA.",
    },
    "doctors and staff": {
        "type": "team",
        "purpose": "Introduce healthcare professionals with verified credentials.",
        "content_required": ["verified_staff_profiles"],
        "layout": "Professional profile cards.",
    },
    "facilities": {
        "type": "facilities",
        "purpose": "Show available facilities.",
        "content_required": ["facility_details", "business_photographs"],
        "layout": "Facility highlights with supporting images.",
    },
    "our process": {
        "type": "process",
        "purpose": "Explain how customers work with the business.",
        "content_required": ["process_steps"],
        "layout": "Step-by-step process timeline.",
    },
}


def get_primary_cta(business_type: str) -> str:
    cta_map = {
        "education": "Enquire About Admissions",
        "restaurant": "Explore the Menu",
        "retail": "Explore Products",
        "healthcare": "Contact the Clinic",
        "professional_services": "Request an Enquiry",
        "beauty_wellness": "Explore Services",
        "general_business": "Contact Us",
    }

    return cta_map.get(business_type, "Contact Us")

DESIGN_SYSTEMS = {
    "modern-minimal": {
        "name": "Modern Minimal",
        "description": "Clean layouts, clear typography and a professional visual identity.",
        "business_types": [
            "education",
            "healthcare",
            "professional_services",
            "general_business",
        ],
    },
    "bold-vibrant": {
        "name": "Bold & Vibrant",
        "description": "Expressive colours, strong typography and energetic layouts.",
        "business_types": [
            "restaurant",
            "retail",
        ],
    },
    "premium-elegant": {
        "name": "Premium Elegant",
        "description": "Refined typography, warm colours and spacious layouts.",
        "business_types": [
            "beauty_wellness",
        ],
    },
}


def get_design_system(business_type: str, category: str = "") -> dict:
    category_text = category.lower()

    # Strong category-based matching
    if any(word in category_text for word in [
        "restaurant", "cafe", "café", "food",
        "bakery", "fast food", "bar"
    ]):
        system_id = "bold-vibrant"

    elif any(word in category_text for word in [
        "retail", "shop", "store", "boutique",
        "fashion", "clothing", "supermarket"
    ]):
        system_id = "bold-vibrant"

    elif any(word in category_text for word in [
        "luxury", "salon", "spa", "jewellery",
        "jewelry", "beauty", "wellness"
    ]):
        system_id = "premium-elegant"

    else:
        system = next(
            (
                (key, value)
                for key, value in DESIGN_SYSTEMS.items()
                if business_type in value["business_types"]
            ),
            ("modern-minimal", DESIGN_SYSTEMS["modern-minimal"])
        )

        system_id = system[0]

    selected = DESIGN_SYSTEMS[system_id]

    return {
        "system_id": system_id,
        "name": selected["name"],
        "description": selected["description"],
    }

def build_website_blueprint(business: dict) -> dict:
    analysis = analyze_business(business)

    business_type = analysis["classification"]["business_type"]
    design_system = get_design_system(
    business_type,
    business.get("category", "")
)

    recommendations = analysis["website_recommendations"]
    recommended_sections = recommendations["recommended_sections"]

    sections = []
    seen_sections = set()

    for position, recommendation in enumerate(recommended_sections, start=1):
        section_name = recommendation["name"]
        section_key = section_name.strip().lower()

        if section_key in seen_sections:
            continue

        seen_sections.add(section_key)

        guide = SECTION_GUIDES.get(
            section_key,
            {
                "type": "custom",
                "purpose": recommendation["reason"],
                "content_required": ["business_supplied_information"],
                "layout": "A responsive content section appropriate to its purpose.",
            },
        )

        sections.append({
            "id": f"section_{len(sections) + 1}",
            "name": section_name,
            "type": guide["type"],
            "purpose": guide["purpose"],
            "layout": guide["layout"],
            "content_required": guide["content_required"],
            "content_guidance": recommendation["reason"],
        })

    primary_cta = get_primary_cta(business_type)

    return {
        "blueprint_version": "1.0",
        "project": {
            "business_name": business["business_name"],
            "business_category": business["category"],
            "business_location": business["location"],
        },
        "website": {
            "site_type": "static_business_website",
            "initial_page_count": 1,
            "pages": [
                {
                    "id": "home",
                    "name": "Home",
                    "path": "/",
                    "purpose": analysis["classification"]["primary_website_goal"],
                    "sections": sections,
                }
            ],
            "navigation": [
                section["name"]
                for section in sections
                if section["name"].lower() != "home"
            ],
            "primary_cta": primary_cta,
        },
        "design": {
            "direction": recommendations["visual_direction"],
            "audience": analysis["classification"]["likely_audience"],
            "business_type": business_type,
            **design_system,
        },
        "content_requirements": {
            "available_services": business.get("services") or [],
            "description": business.get("description") or "",
            "location": business.get("location"),
            "phone": business.get("phone"),
            "email": business.get("email"),
            "opening_hours": business.get("opening_hours"),
            "missing_information": analysis["missing_information"],
        },
        "generation_rules": [
            "Use only business information supplied or explicitly approved by the owner.",
            "Never invent testimonials, ratings, awards, results or qualifications.",
            "Use placeholders for missing content rather than fabricating facts.",
            "Make the website responsive on mobile, tablet and desktop.",
            "Keep navigation consistent with the generated page sections.",
            "Use accessible semantic HTML.",
        ],
    }
