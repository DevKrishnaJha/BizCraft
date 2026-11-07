
import re
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


class MapsLookupRequest(BaseModel):
    maps_url: str = Field(min_length=10, max_length=2000)

    @field_validator("maps_url")
    @classmethod
    def validate_maps_url(cls, value):
        value = value.strip()
        parsed = urlparse(value)

        if parsed.scheme != "https":
            raise ValueError("Only HTTPS Google Maps links are accepted.")

        hostname = (parsed.hostname or "").lower()

        allowed_short_domains = {
    "maps.app.goo.gl",
    "goo.gl",
    "share.google",
}

        google_domain = bool(
            re.fullmatch(
                r"(?:[a-z0-9-]+\.)*google\.(?:com|[a-z]{2,3}|co\.[a-z]{2})",
                hostname,
            )
        )

        if hostname not in allowed_short_domains and not google_domain:
            raise ValueError("Please provide a genuine Google Maps URL.")

        if hostname in allowed_short_domains:
            return value

        if not parsed.path.startswith("/maps"):
            raise ValueError("The supplied Google URL is not a Maps link.")

        return value
