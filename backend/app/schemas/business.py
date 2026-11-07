
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from urllib.parse import urlparse


class BusinessCreate(BaseModel):
    business_name: str = Field(min_length=2, max_length=120)
    category: str = Field(min_length=2, max_length=100)
    location: str = Field(min_length=2, max_length=200)

    phone: Optional[str] = Field(default=None, max_length=30)
    email: Optional[str] = Field(default=None, max_length=254)
    website: Optional[str] = Field(default=None, max_length=500)

    google_maps_url: Optional[str] = Field(default=None, max_length=2000)
    description: Optional[str] = Field(default=None, max_length=2000)

    services: list[str] = Field(default_factory=list, max_length=30)
    opening_hours: Optional[str] = Field(default=None, max_length=2000)

    @field_validator(
        "website",
        "google_maps_url",
        mode="before"
    )
    @classmethod
    def validate_urls(cls, value):
        if value is None or value == "":
            return None

        if not isinstance(value, str):
            raise ValueError("URL must be text")

        parsed = urlparse(value)

        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("Enter a valid HTTP or HTTPS URL")

        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if value is None or value == "":
            return None

        import re

        if not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            value
        ):
            raise ValueError("Enter a valid email address")

        return value

    @field_validator("services")
    @classmethod
    def clean_services(cls, services):
        cleaned = [item.strip() for item in services if item.strip()]

        if len(cleaned) != len(services):
            return cleaned

        return cleaned

    @field_validator(
        "business_name",
        "category",
        "location"
    )
    @classmethod
    def clean_required_fields(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty")

        return value


class BusinessResponse(BusinessCreate):
    id: str
    created_at: str
