"""Geoapify-backed Google Maps business lookup for BizCraft.

The filename is retained for compatibility with existing imports. The provider
inside this module is GeoapifyProvider; it does not call the Google Places API.
"""

import asyncio
import ipaddress
import math
import os
import re
import socket
from difflib import SequenceMatcher
from urllib.parse import parse_qs, unquote, urljoin, urlparse

import httpx


GEOCODING_URL = "https://api.geoapify.com/v1/geocode/search"

GOOGLE_DOMAINS = {"google.com", "google.co.in"}
SHORT_URL_HOSTS = {"maps.app.goo.gl", "goo.gl", "share.google"}
REDIRECT_STATUSES = {301, 302, 303, 307, 308}

MAX_REDIRECTS = 5
MAX_URL_LENGTH = 2000
MAX_QUERY_LENGTH = 200

HTTP_TIMEOUT = httpx.Timeout(
    connect=5.0,
    read=15.0,
    write=10.0,
    pool=5.0,
)


class GeoapifyNotConfigured(Exception):
    """Raised when GEOAPIFY_API_KEY is missing."""


class GeoapifyInvalidUrl(Exception):
    """Raised when the supplied URL is not an accepted Google Maps URL."""


class GeoapifyAPIError(Exception):
    """Raised when a Geoapify or Google short-link request fails."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class GeoapifyProvider:
    def __init__(
        self,
        api_key: str | None = None,
        country_code: str | None = None,
        language_code: str | None = None,
    ):
        self.api_key = (
            api_key if api_key is not None else os.getenv("GEOAPIFY_API_KEY", "")
        ).strip()
        self.country_code = (
            country_code
            if country_code is not None
            else os.getenv("GEOAPIFY_COUNTRY_CODE", "in")
        ).strip().lower()
        self.language_code = (
            language_code
            if language_code is not None
            else os.getenv("GEOAPIFY_LANGUAGE_CODE", "en")
        ).strip().lower()

    def is_configured(self) -> bool:
        return bool(self.api_key)

    # ------------------------------------------------------------------
    # Google Maps URL validation
    # ------------------------------------------------------------------

    @staticmethod
    def _is_google_host(hostname: str) -> bool:
        hostname = hostname.lower().rstrip(".")

        if hostname in SHORT_URL_HOSTS:
            return True

        return any(
            hostname == domain or hostname.endswith("." + domain)
            for domain in GOOGLE_DOMAINS
        )

    def _validate_url(self, url: str):
        if not isinstance(url, str):
            raise GeoapifyInvalidUrl("Google Maps URL must be a string.")

        url = url.strip()
        if not url or len(url) > MAX_URL_LENGTH:
            raise GeoapifyInvalidUrl("Invalid Google Maps URL.")

        if any(ord(char) < 32 for char in url):
            raise GeoapifyInvalidUrl("URL contains invalid characters.")

        try:
            parsed = urlparse(url)
            hostname = parsed.hostname
            port = parsed.port
        except ValueError as error:
            raise GeoapifyInvalidUrl("Malformed Google Maps URL.") from error

        if parsed.scheme.lower() != "https":
            raise GeoapifyInvalidUrl("Only HTTPS Google Maps links are accepted.")

        if not hostname or not self._is_google_host(hostname):
            raise GeoapifyInvalidUrl("Please provide a valid Google Maps link.")

        if parsed.username or parsed.password:
            raise GeoapifyInvalidUrl("URLs containing credentials are not accepted.")

        if port not in (None, 443):
            raise GeoapifyInvalidUrl("Unexpected URL port.")

        return parsed

    # ------------------------------------------------------------------
    # DNS protection for short-link resolution
    # ------------------------------------------------------------------

    @staticmethod
    def _check_public_dns(hostname: str) -> None:
        try:
            addresses = socket.getaddrinfo(
                hostname,
                443,
                type=socket.SOCK_STREAM,
            )
        except socket.gaierror as error:
            raise GeoapifyInvalidUrl(
                "Could not resolve Google Maps link."
            ) from error

        if not addresses:
            raise GeoapifyInvalidUrl("Google Maps link has no DNS records.")

        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])
            if not ip.is_global:
                raise GeoapifyInvalidUrl(
                    "Google Maps link resolves to an untrusted address."
                )

    async def _validate_public_destination(self, url: str):
        parsed = self._validate_url(url)
        hostname = parsed.hostname.lower().rstrip(".")

        try:
            ipaddress.ip_address(hostname)
        except ValueError:
            pass
        else:
            raise GeoapifyInvalidUrl("IP-based URLs are not accepted.")

        await asyncio.to_thread(self._check_public_dns, hostname)
        return parsed

    # ------------------------------------------------------------------
    # Resolve short Google Maps links
    # ------------------------------------------------------------------

    async def _resolve_short_url(self, url: str) -> str:
        parsed = self._validate_url(url)
        hostname = parsed.hostname.lower().rstrip(".")

        if hostname not in SHORT_URL_HOSTS:
            return url.strip()

        current_url = url.strip()

        async with httpx.AsyncClient(
            timeout=HTTP_TIMEOUT,
            follow_redirects=False,
            headers={"User-Agent": "BizCraft/1.0"},
        ) as client:
            for _ in range(MAX_REDIRECTS):
                await self._validate_public_destination(current_url)

                try:
                    response = await client.get(current_url)
                except httpx.TimeoutException as error:
                    raise GeoapifyAPIError(
                        "Google Maps link resolution timed out."
                    ) from error
                except httpx.RequestError as error:
                    raise GeoapifyAPIError(
                        "Could not connect to Google Maps."
                    ) from error

                if response.status_code not in REDIRECT_STATUSES:
                    try:
                        response.raise_for_status()
                    except httpx.HTTPStatusError as error:
                        raise GeoapifyInvalidUrl(
                            "Google Maps link could not be resolved."
                        ) from error
                    return current_url

                location = response.headers.get("location")
                if not location:
                    raise GeoapifyInvalidUrl(
                        "Google Maps redirect has no destination."
                    )

                current_url = urljoin(current_url, location)
                self._validate_url(current_url)

        raise GeoapifyInvalidUrl("Too many redirects in the Google Maps link.")

    # ------------------------------------------------------------------
    # Extract business query and coordinates
    # ------------------------------------------------------------------

    def _extract_search_query(self, url: str) -> str:
        parsed = self._validate_url(url)
        parameters = parse_qs(parsed.query)

        for key in ("query", "q"):
            values = parameters.get(key)
            if values and values[0].strip():
                return values[0].strip()[:MAX_QUERY_LENGTH]

        for marker in ("/maps/place/", "/maps/search/"):
            if marker in parsed.path:
                raw_name = parsed.path.split(marker, 1)[1].split("/", 1)[0]
                name = unquote(raw_name.replace("+", " "))
                name = re.sub(r"\s+", " ", name).strip()
                if name:
                    return name[:MAX_QUERY_LENGTH]

        raise GeoapifyInvalidUrl(
            "Could not identify a business name in this link. "
            "Try a full Google Maps business link."
        )

    @staticmethod
    def _split_business_query(query: str) -> tuple[str, str]:
        parts = re.split(
            r"\s+-\s+|\s+in\s+",
            query,
            maxsplit=1,
            flags=re.IGNORECASE,
        )
        name = parts[0].strip()
        location = parts[1].strip() if len(parts) > 1 else ""
        return name, location

    @staticmethod
    def _extract_coordinates(url: str):
        # Google Maps place URLs commonly include !3dLAT!4dLON. The @LAT,LON
        # form is also supported, although it may represent the map centre.
        patterns = (
            r"!3d(-?\d+(?:\.\d+)?)!4d(-?\d+(?:\.\d+)?)",
            r"@(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)",
        )

        for pattern in patterns:
            match = re.search(pattern, url)
            if not match:
                continue

            lat = float(match.group(1))
            lon = float(match.group(2))
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return lat, lon

        return None

    # ------------------------------------------------------------------
    # Geoapify request
    # ------------------------------------------------------------------

    async def _search_businesses(
        self,
        business_name: str,
        location_hint: str,
        coordinates=None,
    ) -> dict:
        # Geoapify supports structured `name` input for amenity/place names.
        # Do not combine `name` with the free-form `text` parameter.
        params = {
            "name": business_name,
            "type": "amenity",
            "format": "json",
            "limit": 20,
            "lang": self.language_code,
            "filter": f"countrycode:{self.country_code}",
            "apiKey": self.api_key,
        }

        # If the Maps URL contains a location hint, pass it as a structured
        # city field. It is only a hint; not every Maps URL contains one.
        if location_hint:
            params["city"] = location_hint

        if coordinates:
            lat, lon = coordinates
            params["bias"] = f"proximity:{lon},{lat}"

        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                response = await client.get(GEOCODING_URL, params=params)

                if response.is_error:
                    raise GeoapifyAPIError(
                        "Geoapify business search failed.",
                        status_code=response.status_code,
                    )

                data = response.json()
        except GeoapifyAPIError:
            raise
        except httpx.TimeoutException as error:
            raise GeoapifyAPIError("Geoapify search timed out.") from error
        except httpx.RequestError as error:
            raise GeoapifyAPIError("Could not connect to Geoapify.") from error
        except ValueError as error:
            raise GeoapifyAPIError("Geoapify returned invalid JSON.") from error

        if not isinstance(data, dict):
            raise GeoapifyAPIError("Geoapify returned an unexpected response.")

        return data

    # ------------------------------------------------------------------
    # Matching helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_name(value: str) -> str:
        return re.sub(r"[^a-z0-9]", "", value.lower())

    @staticmethod
    def _distance_meters(coordinates, item):
        if not coordinates:
            return None

        try:
            lat1, lon1 = coordinates
            lat2 = float(item["lat"])
            lon2 = float(item["lon"])

            earth_radius = 6_371_000
            lat1 = math.radians(lat1)
            lat2 = math.radians(lat2)
            delta_lat = lat2 - lat1
            delta_lon = math.radians(lon2 - lon1)

            a = (
                math.sin(delta_lat / 2) ** 2
                + math.cos(lat1)
                * math.cos(lat2)
                * math.sin(delta_lon / 2) ** 2
            )
            a = max(0.0, min(1.0, a))

            return earth_radius * 2 * math.atan2(
                math.sqrt(a),
                math.sqrt(1 - a),
            )
        except (KeyError, TypeError, ValueError):
            return None

    @staticmethod
    def _candidate_name(item: dict, raw: dict) -> str | None:
        name = item.get("name") or raw.get("name")
        if isinstance(name, str) and name.strip():
            return name.strip()
        return None

    # ------------------------------------------------------------------
    # Match and identify business
    # ------------------------------------------------------------------

    async def lookup_for_autofill(self, maps_url: str) -> dict:
        if not self.is_configured():
            raise GeoapifyNotConfigured("Geoapify is not configured.")

        resolved_url = await self._resolve_short_url(maps_url)
        query = self._extract_search_query(resolved_url)
        business_name, location_hint = self._split_business_query(query)

        if len(business_name) < 2:
            raise GeoapifyInvalidUrl("Could not identify the business name.")

        coordinates = self._extract_coordinates(resolved_url)
        data = await self._search_businesses(
            business_name,
            location_hint,
            coordinates,
        )

        results = data.get("results", [])
        if not isinstance(results, list):
            raise GeoapifyAPIError("Geoapify returned an invalid results list.")

        expected = self._normalize_name(business_name)
        matches = []
        candidate_names = []

        for item in results:
            if not isinstance(item, dict):
                continue

            datasource = item.get("datasource")
            raw = (
                datasource.get("raw", {})
                if isinstance(datasource, dict)
                else {}
            )
            if not isinstance(raw, dict):
                raw = {}

            result_name = self._candidate_name(item, raw)
            if not result_name:
                continue

            candidate_names.append(result_name)
            actual = self._normalize_name(result_name)
            if not actual:
                continue

            name_score = SequenceMatcher(None, expected, actual).ratio()
            if expected in actual or actual in expected:
                name_score = max(name_score, 0.90)

            distance = self._distance_meters(coordinates, item)

            # A coordinate match is useful evidence, but do not let a nearby
            # unrelated business pass solely because it is close to the pin.
            if distance is not None and distance > 5_000:
                continue

            location_score = 0.0
            address = item.get("formatted") or ""
            if location_hint and isinstance(address, str):
                location_normalized = self._normalize_name(location_hint)
                address_normalized = self._normalize_name(address)
                if (
                    location_normalized
                    and location_normalized in address_normalized
                ):
                    location_score = 1.0

            if coordinates and distance is not None:
                proximity_score = max(0.0, 1.0 - distance / 5_000)
                score = (
                    name_score * 0.75
                    + proximity_score * 0.20
                    + location_score * 0.05
                )
                minimum_name_score = 0.55
            else:
                score = (
                    name_score * 0.85 + location_score * 0.15
                    if location_hint
                    else name_score
                )
                minimum_name_score = 0.70

            if name_score < minimum_name_score:
                continue

            matches.append(
                {
                    "score": score,
                    "name_score": name_score,
                    "distance": distance,
                    "item": item,
                    "raw": raw,
                }
            )

        # Useful diagnostics; never log the API key or full request URL.
        print(
            "[BizCraft Geoapify]",
            {
                "query": query,
                "coordinates_found": coordinates is not None,
                "total_results": len(results),
                "matched_results": len(matches),
                "candidate_names": candidate_names[:10],
            },
        )

        if not matches:
            return {
                "status": "no_match",
                "search_query": query,
                "results_count": len(results),
                "candidate_names": candidate_names[:10],
            }

        matches.sort(key=lambda match: match["score"], reverse=True)
        best = matches[0]

        if len(matches) > 1:
            second = matches[1]
            scores_are_close = abs(best["score"] - second["score"]) < 0.04
            distances_do_not_resolve = (
                best["distance"] is None
                or second["distance"] is None
                or abs(best["distance"] - second["distance"]) > 100
            )
            if scores_are_close and distances_do_not_resolve:
                return {
                    "status": "ambiguous",
                    "search_query": query,
                    "candidate_names": candidate_names[:10],
                }

        item = best["item"]
        raw = best["raw"]
        categories = item.get("categories", [])
        if not isinstance(categories, list):
            categories = []

        return {
            "status": "success",
            "search_query": query,
            "source": "Geoapify / OpenStreetMap",
            "match_score": round(best["score"], 2),
            "distance_meters": best["distance"],
            "business_data": {
                "business_name": self._candidate_name(item, raw),
                "location": item.get("formatted"),
                "categories": categories,
                "phone": raw.get("phone") or raw.get("contact:phone"),
                "email": raw.get("email") or raw.get("contact:email"),
                "website": raw.get("website") or raw.get("contact:website"),
                "opening_hours": raw.get("opening_hours"),
                "description": raw.get("description"),
                "place_id": item.get("place_id"),
            },
        }

    # ------------------------------------------------------------------
    # Backwards-compatible endpoint used by the older /lookup route
    # ------------------------------------------------------------------

    async def lookup(self, maps_url: str) -> dict:
        result = await self.lookup_for_autofill(maps_url)
        successful = result.get("status") == "success"
        business_data = result.get("business_data", {})

        return {
            "status": "success" if successful else "no_results",
            "search_query": result.get("search_query"),
            "source": "Geoapify",
            "attribution": "© OpenStreetMap contributors",
            "candidates": (
                [
                    {
                        "place_id": business_data.get("place_id") or "",
                        "name": business_data.get("business_name") or "",
                        "address": business_data.get("location"),
                        "google_maps_url": maps_url,
                    }
                ]
                if successful
                else []
            ),
        }
