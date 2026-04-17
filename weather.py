import re
from typing import Dict, Optional
from urllib.parse import quote

import click
import requests

ZIPCODE_PATTERN = re.compile(r"^\d{5}$")
REQUEST_TIMEOUT_SECONDS = 10


class WeatherError(Exception):
    """Raised when external weather/location services fail."""


def _validate_zipcode(zipcode: str) -> None:
    if not ZIPCODE_PATTERN.match(zipcode):
        raise click.ClickException("Invalid zipcode. Please provide a 5-digit US zipcode.")


def _request_json(url: str) -> Dict:
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        raise WeatherError("Unable to contact external service.") from exc

    if response.status_code == 404:
        return {}

    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise WeatherError("External service request failed.") from exc

    try:
        return response.json()
    except ValueError as exc:
        raise WeatherError("Received an invalid response from external service.") from exc


def get_location_by_zipcode(zipcode: str) -> Optional[Dict[str, str]]:
    _validate_zipcode(zipcode)
    data = _request_json(f"https://api.zippopotam.us/us/{zipcode}")
    places = data.get("places", [])

    if not places:
        return None

    place = places[0]
    city = place.get("place name")
    state = place.get("state")

    if not city or not state:
        raise WeatherError("Location lookup returned incomplete data.")

    return {"city": city, "state": state, "zipcode": zipcode}


def get_current_location() -> Optional[Dict[str, str]]:
    data = _request_json("https://ipapi.co/json/")

    if data.get("error"):
        return None

    city = data.get("city")
    state = data.get("region")
    zipcode = data.get("postal")

    if not city or not state:
        return None

    location = {"city": city, "state": state}
    if zipcode:
        location["zipcode"] = zipcode

    return location


def get_current_weather(query: str) -> Dict[str, str]:
    safe_query = quote(query)
    data = _request_json(f"https://wttr.in/{safe_query}?format=j1")
    current_conditions = data.get("current_condition", [])

    if not current_conditions:
        raise WeatherError("Weather lookup returned no current conditions.")

    current = current_conditions[0]
    temp_f = current.get("temp_F")

    weather_desc_items = current.get("weatherDesc", [])
    weather_desc = weather_desc_items[0].get("value") if weather_desc_items else None

    if temp_f is None or not weather_desc:
        raise WeatherError("Weather lookup returned incomplete data.")

    return {"temperature_f": temp_f, "condition": weather_desc}


@click.group()
def cli() -> None:
    """Weather command line tools."""


@cli.command(name="where-is")
@click.option("--zipcode", help="5-digit US zipcode.")
def where_is(zipcode: Optional[str]) -> None:
    """Display city and state for a zipcode or current location."""
    try:
        if zipcode:
            location = get_location_by_zipcode(zipcode)
            if not location:
                raise click.ClickException(f"Could not find location for zipcode {zipcode}.")
            click.echo(f"{zipcode} is in {location['city']}, {location['state']}.")
            return

        location = get_current_location()
        if not location:
            raise click.ClickException("Unable to determine current location.")

        click.echo(f"Your current location is {location['city']}, {location['state']}.")
    except WeatherError as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command()
@click.option("--zipcode", help="5-digit US zipcode.")
def current(zipcode: Optional[str]) -> None:
    """Display current weather for a zipcode or current location."""
    try:
        if zipcode:
            location = get_location_by_zipcode(zipcode)
            if not location:
                raise click.ClickException(f"Could not find location for zipcode {zipcode}.")
            weather = get_current_weather(zipcode)
            click.echo(
                f"It is currently {weather['temperature_f']}ºF, and {weather['condition']} in "
                f"{location['city']}, {location['state']}."
            )
            return

        location = get_current_location()
        if not location:
            raise click.ClickException("Unable to determine current location.")

        query = location.get("zipcode") or f"{location['city']},{location['state']}"
        weather = get_current_weather(query)
        click.echo(
            f"It is currently {weather['temperature_f']}ºF, and {weather['condition']} in "
            f"{location['city']}, {location['state']}."
        )
    except WeatherError as exc:
        raise click.ClickException(str(exc)) from exc


if __name__ == "__main__":
    cli()
