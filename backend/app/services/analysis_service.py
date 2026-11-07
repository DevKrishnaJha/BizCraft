
def analyze_business(business: dict) -> dict:
    """
    Generate a structured, rule-based analysis of a business.
    No external AI API is used.
    """

    name = business["business_name"]
    category = business["category"]
    location = business["location"]
    description = business.get("description") or ""
    services = business.get("services") or []
    opening_hours = business.get("opening_hours")
    phone = business.get("phone")
    email = business.get("email")
    website = business.get("website")

    category_text = category.lower()

    # -------------------------
    # Business classification
    # -------------------------

    business_types = {
        "education": {
            "keywords": [
                "education", "school", "college", "coaching",
                "institute", "academy", "tutor", "training",
            ],
            "audience": [
                "Students",
                "Parents and guardians",
            ],
            "goal": "Build trust and help students discover courses and enrolment information.",
            "sections": [
                ("Courses", "Present the courses and subjects offered."),
                ("Faculty", "Introduce teachers and their qualifications."),
                ("Results", "Show verified academic results and achievements."),
                ("Admissions", "Explain the admission process."),
            ],
            "style": "Professional, trustworthy and education-focused.",
        },

        "restaurant": {
            "keywords": [
                "restaurant", "cafe", "café", "food",
                "bakery", "pizza", "hotel", "dhaba",
            ],
            "audience": [
                "Local residents",
                "Food enthusiasts",
                "Visitors looking for dining options",
            ],
            "goal": "Help customers explore the menu, location and contact information.",
            "sections": [
                ("Menu", "Present available food and drinks."),
                ("Gallery", "Show genuine food and restaurant photographs."),
                ("About", "Introduce the restaurant and its identity."),
                ("Location", "Help customers find the restaurant."),
            ],
            "style": "Warm, appetising and visually engaging.",
        },

        "retail": {
            "keywords": [
                "retail", "shop", "store", "clothing",
                "fashion", "grocery", "boutique", "jewellery",
                "jewelry", "electronics",
            ],
            "audience": [
                "Local shoppers",
                "People searching for specific products",
            ],
            "goal": "Showcase products, communicate the store's identity and encourage visits.",
            "sections": [
                ("Products", "Showcase available products."),
                ("Collections", "Organise products into useful categories."),
                ("About", "Introduce the store."),
                ("Visit Us", "Display location and contact information."),
            ],
            "style": "Modern, product-focused and easy to navigate.",
        },

        "healthcare": {
            "keywords": [
                "clinic", "hospital", "dentist", "medical",
                "healthcare", "physiotherapy", "pharmacy",
            ],
            "audience": [
                "Patients",
                "Families seeking healthcare services",
            ],
            "goal": "Present services, contact information and appointment details clearly.",
            "sections": [
                ("Services", "Explain the services offered."),
                ("Doctors and Staff", "Introduce verified professional credentials."),
                ("Facilities", "Show available facilities."),
                ("Appointments", "Explain how to contact the provider."),
            ],
            "style": "Clean, accessible and reassuring.",
        },

        "professional_services": {
            "keywords": [
                "consultancy", "consultant", "agency", "legal",
                "lawyer", "accounting", "accountant", "architect",
                "real estate", "insurance",
            ],
            "audience": [
                "Potential clients",
                "Individuals and organisations seeking professional services",
            ],
            "goal": "Establish credibility and generate relevant enquiries.",
            "sections": [
                ("Services", "Explain the professional services offered."),
                ("About", "Introduce the business and its experience."),
                ("Our Process", "Explain how clients work with the business."),
                ("Contact", "Make enquiries straightforward."),
            ],
            "style": "Professional, structured and credibility-focused.",
        },

        "beauty_wellness": {
            "keywords": [
                "salon", "beauty", "spa", "barber",
                "makeup", "hair", "wellness",
            ],
            "audience": [
                "People looking for personal care services",
                "Local customers",
            ],
            "goal": "Showcase services and make enquiries or bookings easier.",
            "sections": [
                ("Services", "Present treatments and services."),
                ("Gallery", "Show genuine examples of the business."),
                ("About", "Introduce the team and business."),
                ("Contact and Booking", "Explain how customers can enquire."),
            ],
            "style": "Elegant, welcoming and visually polished.",
        },
    }

    matched_type = None

    for type_name, config in business_types.items():
        if any(keyword in category_text for keyword in config["keywords"]):
            matched_type = type_name
            break

    if matched_type:
        config = business_types[matched_type]
        business_type = matched_type
        audience = config["audience"]
        goal = config["goal"]
        style = config["style"]

        recommended_sections = [
            {
                "name": "Home",
                "reason": "Introduce the business and communicate its main offering.",
            },
            {
                "name": "About",
                "reason": "Help visitors understand the business.",
            },
        ] + [
            {"name": section, "reason": reason}
            for section, reason in config["sections"]
        ]

    else:
        business_type = "general_business"
        audience = [
            "Potential customers in the business's service area",
        ]
        goal = "Explain the business, showcase its offerings and help customers get in touch."
        style = "Modern, clear and appropriate to the business identity."

        recommended_sections = [
            {
                "name": "Home",
                "reason": "Introduce the business and its main offering.",
            },
            {
                "name": "About",
                "reason": "Explain the business and its background.",
            },
            {
                "name": "Services",
                "reason": "Present the products or services offered.",
            },
        ]

    # -------------------------
    # Common website sections
    # -------------------------

    recommended_sections.extend([
        {
            "name": "Contact",
            "reason": "Give visitors a clear way to contact the business.",
        },
        {
            "name": "Location",
            "reason": "Help visitors understand where the business operates.",
        },
    ])

    if opening_hours:
        recommended_sections.append({
            "name": "Opening Hours",
            "reason": "Show customers when the business is available.",
        })

    if services:
        recommended_sections.append({
            "name": "Services and Offerings",
            "reason": "Present the information supplied about the business's offerings.",
        })

    # -------------------------
    # Missing information
    # -------------------------

    missing_information = []

    if not description.strip():
        missing_information.append("Business description")

    if not services:
        missing_information.append("Services or products")

    if not phone and not email:
        missing_information.append("Contact information")

    if not opening_hours:
        missing_information.append("Opening hours")

    if not business.get("google_maps_url"):
        missing_information.append("Google Maps link")

    # -------------------------
    # Final analysis
    # -------------------------

    return {
        "analysis_version": "1.0",
        "business": {
            "name": name,
            "category": category,
            "location": location,
        },
        "classification": {
            "business_type": business_type,
            "likely_audience": audience,
            "primary_website_goal": goal,
        },
        "website_recommendations": {
            "visual_direction": style,
            "recommended_sections": recommended_sections,
        },
        "business_information": {
            "description": description,
            "services": services,
            "has_phone": bool(phone),
            "has_email": bool(email),
            "has_existing_website": bool(website),
        },
        "missing_information": missing_information,
        "notes": [
            "This analysis is generated using predefined Python rules.",
            "Audience and design recommendations are suggestions, not verified market research.",
            "Only information supplied by the business owner should be used as factual website content.",
        ],
    }
