"""Fetch weather information using the OpenWeatherMap API (pyowm).

The API key is read from configuration (``OWM_API_KEY`` env var) rather than
being hard-coded. This module supports both the pyowm 3.x API and gracefully
degrades to an "unavailable" message when the key/library is missing.
"""

from jarvis import config


def weather(city):
    """Return a spoken-style weather report for ``city``."""
    weather_say = "Weather status in " + city + " is "

    if not config.OWM_API_KEY:
        return weather_say + "unavailable. No OpenWeatherMap API key configured."

    try:
        from pyowm import OWM

        owm = OWM(config.OWM_API_KEY)
        # pyowm 3.x API
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place(city)
        w = observation.weather

        status = w.detailed_status
        temp = w.temperature("celsius")["temp"]
        wind_speed = w.wind().get("speed", 0)
        humidity = w.humidity

        weather_say += f"{temp} celsius and the sky is {status}"
        weather_say += f". The average wind speed is {wind_speed} metres per second"
        weather_say += f" and the humidity is {humidity} percent."
    except Exception as exc:
        print(f"[get_weather] lookup failed: {exc}")
        weather_say += "unavailable."
    return weather_say


if __name__ == "__main__":
    print(weather(config.CITY))
