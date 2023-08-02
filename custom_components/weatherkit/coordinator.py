"""DataUpdateCoordinator for weatherkit."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed

from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
)

from .api import (
    WeatherKitApiClient,
    WeatherKitApiClientAuthenticationError,
    WeatherKitApiClientError,
)
from .const import DOMAIN, LOGGER


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class WeatherKitDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: WeatherKitApiClient,
    ) -> None:
        """Initialize."""
        self.client = client
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=15),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.client.get_weather_data(
                self.config_entry.data[CONF_LATITUDE],
                self.config_entry.data[CONF_LONGITUDE],
            )
        except WeatherKitApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except WeatherKitApiClientError as exception:
            raise UpdateFailed(exception) from exception
