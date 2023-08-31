from types import MappingProxyType
from typing import Any
from homeassistant.components.weather import (
    Forecast,
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_NAME,
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback


from .coordinator import WeatherKitDataUpdateCoordinator

from .const import ATTRIBUTION, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add a weather entity from a config_entry."""
    coordinator: WeatherKitDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]
    async_add_entities(
        [
            WeatherKitWeather(
                coordinator,
                config_entry.data,
            ),
        ]
    )


condition_code_to_hass = {
    "BlowingDust": "windy",
    "Clear": "sunny",
    "Cloudy": "cloudy",
    "Foggy": "fog",
    "Haze": "fog",
    "MostlyClear": "sunny",
    "MostlyCloudy": "cloudy",
    "PartlyCloudy": "partlycloudy",
    "Smoky": "fog",
    "Breezy": "windy",
    "Windy": "windy",
    "Drizzle": "rainy",
    "HeavyRain": "pouring",
    "IsolatedThunderstorms": "lightning",
    "Rain": "rainy",
    "SunShowers": "rainy",
    "ScatteredThunderstorms": "lightning",
    "StrongStorms": "lightning",
    "Thunderstorms": "lightning",
    "Frigid": "snowy",
    "Hail": "hail",
    "Hot": "sunny",
    "Flurries": "snowy",
    "Sleet": "snowy",
    "Snow": "snowy",
    "SunFlurries": "snowy",
    "WintryMix": "snowy",
    "Blizzard": "snowy",
    "BlowingSnow": "snowy",
    "FreezingDrizzle": "snowy-rainy",
    "FreezingRain": "snowy-rainy",
    "HeavySnow": "snowy",
    "Hurricane": "exceptional",
    "TropicalStorm": "exceptional",
}


def _map_daily_forecast(forecast) -> Forecast:
    return {
        "datetime": forecast.get("forecastStart"),
        "condition": condition_code_to_hass[forecast.get("conditionCode")],
        "native_temperature": forecast.get("temperatureMax"),
        "native_templow": forecast.get("temperatureMin"),
        "native_precipitation": forecast.get("precipitationAmount"),
        "precipitation_probability": forecast.get("precipitationChance") * 100,
        "uv_index": forecast.get("maxUvIndex"),
    }


def _map_hourly_forecast(forecast) -> Forecast:
    return {
        "datetime": forecast.get("forecastStart"),
        "condition": condition_code_to_hass[forecast.get("conditionCode")],
        "native_temperature": forecast.get("temperature"),
        "native_apparent_temperature": forecast.get("temperatureApparent"),
        "native_dew_point": forecast.get("temperatureDewPoint"),
        "native_pressure": forecast.get("pressure"),
        "native_wind_gust_speed": forecast.get("windGust"),
        "native_wind_speed": forecast.get("windSpeed"),
        "wind_bearing": forecast.get("windDirection"),
        "humidity": forecast.get("humidity") * 100,
        "native_precipitation": forecast.get("precipitationAmount"),
        "precipitation_probability": forecast.get("precipitationChance") * 100,
        "cloud_coverage": forecast.get("cloudCover") * 100,
        "uv_index": forecast.get("uvIndex"),
    }


class WeatherKitWeather(
    CoordinatorEntity[WeatherKitDataUpdateCoordinator], WeatherEntity
):
    _attr_attribution = ATTRIBUTION

    _attr_has_entity_name = True
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = UnitOfPressure.MBAR
    _attr_native_visibility_unit = UnitOfLength.KILOMETERS
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR

    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_DAILY | WeatherEntityFeature.FORECAST_HOURLY
    )

    def __init__(
        self,
        coordinator: WeatherKitDataUpdateCoordinator,
        config: MappingProxyType[str, Any],
    ) -> None:
        """Initialise the platform with a data instance and site."""
        super().__init__(coordinator)
        self._config = config

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._config[CONF_LATITUDE]}-{self._config[CONF_LONGITUDE]}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        name = self._config.get(CONF_NAME)
        return name

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        condition_code = self.coordinator.data.get("currentWeather").get(
            "conditionCode"
        )
        condition = condition_code_to_hass[condition_code]

        if (
            condition == "sunny"
            and self.coordinator.data.get("currentWeather").get("daylight") is False
        ):
            condition = "clear-night"

        return condition

    @property
    def native_temperature(self) -> float | None:
        """Return the current temperature."""
        temperature = self.coordinator.data.get("currentWeather").get("temperature")
        return temperature

    @property
    def native_apparent_temperature(self) -> float | None:
        """Return the current apparent_temperature."""
        apparent_temperature = self.coordinator.data.get("currentWeather").get(
            "temperatureApparent"
        )
        return apparent_temperature

    @property
    def native_dew_point(self) -> float | None:
        """Return the current dew_point."""
        dew_point = self.coordinator.data.get("currentWeather").get(
            "temperatureDewPoint"
        )
        return dew_point

    @property
    def native_pressure(self) -> float | None:
        """Return the current pressure."""
        pressure = self.coordinator.data.get("currentWeather").get("pressure")
        return pressure

    @property
    def humidity(self) -> float | None:
        """Return the current humidity."""
        humidity = self.coordinator.data.get("currentWeather").get("humidity")
        return humidity * 100

    @property
    def cloud_coverage(self) -> int | None:
        """Return the current cloud_coverage."""
        cloud_coverage = self.coordinator.data.get("currentWeather").get("cloudCover")
        return cloud_coverage * 100

    @property
    def uv_index(self) -> float | None:
        """Return the current uv_index."""
        uv_index = self.coordinator.data.get("currentWeather").get("uvIndex")
        return uv_index

    @property
    def native_visibility(self) -> float | None:
        """Return the current visibility."""
        visibility = self.coordinator.data.get("currentWeather").get("visibility")
        return visibility / 1000

    @property
    def native_wind_gust_speed(self) -> float | None:
        """Return the current wind_gust_speed."""
        wind_gust_speed = self.coordinator.data.get("currentWeather").get("windGust")
        return wind_gust_speed

    @property
    def native_wind_speed(self) -> float | None:
        """Return the current wind_speed."""
        wind_speed = self.coordinator.data.get("currentWeather").get("windSpeed")
        return wind_speed

    @property
    def wind_bearing(self) -> float | None:
        """Return the current wind_bearing."""
        wind_bearing = self.coordinator.data.get("currentWeather").get("windDirection")
        return wind_bearing

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return the forecast."""
        if not self.coordinator.data.get("forecastDaily"):
            return None
        forecast = self.coordinator.data.get("forecastDaily").get("days")
        return [_map_daily_forecast(f) for f in forecast]

    async def async_forecast_hourly(self) -> list[Forecast] | None:
        if not self.coordinator.data.get("forecastHourly"):
            return None
        forecast = self.coordinator.data.get("forecastHourly").get("hours")
        return [_map_hourly_forecast(f) for f in forecast]
