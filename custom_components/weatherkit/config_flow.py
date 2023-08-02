"""Adds config flow for WeatherKit."""
from __future__ import annotations
from homeassistant.helpers.aiohttp_client import async_create_clientsession

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig

from .api import (
    WeatherKitApiClient,
    WeatherKitApiClientAuthenticationError,
    WeatherKitApiClientCommunicationError,
    WeatherKitApiClientError,
)
from .const import (
    CONF_KEY_ID,
    CONF_KEY_PEM,
    CONF_SERVICE_ID,
    CONF_TEAM_ID,
    DOMAIN,
    LOGGER,
)


def _get_data_schema(
    hass: HomeAssistant, config_entry: config_entries.ConfigEntry | None = None
) -> vol.Schema:
    """Get a schema with default values."""
    # If tracking home or no config entry is passed in, default value come from Home location
    if config_entry is None:
        return vol.Schema(
            {
                vol.Required(CONF_NAME, default="Home"): str,
                vol.Required(CONF_LATITUDE, default=hass.config.latitude): cv.latitude,
                vol.Required(
                    CONF_LONGITUDE, default=hass.config.longitude
                ): cv.longitude,
                # Auth
                vol.Required(CONF_KEY_ID): str,
                vol.Required(CONF_SERVICE_ID): str,
                vol.Required(CONF_TEAM_ID): str,
                vol.Required(CONF_KEY_PEM): TextSelector(
                    TextSelectorConfig(
                        multiline=True,
                    )
                ),
            }
        )
    # Not tracking home, default values come from config entry
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=config_entry.data.get(CONF_NAME)): str,
            vol.Required(
                CONF_LATITUDE, default=config_entry.data.get(CONF_LATITUDE)
            ): cv.latitude,
            vol.Required(
                CONF_LONGITUDE, default=config_entry.data.get(CONF_LONGITUDE)
            ): cv.longitude,
            # Auth
            vol.Required(CONF_KEY_ID): str,
            vol.Required(CONF_SERVICE_ID): str,
            vol.Required(CONF_TEAM_ID): str,
            vol.Required(CONF_KEY_PEM): TextSelector(
                TextSelectorConfig(
                    multiline=True,
                )
            ),
        }
    )


class WeatherKitUnsupportedLocationError(Exception):
    """Error to indicate a location is unsupported"""


class WeatherKitFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for WeatherKit."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_config(user_input)
            except WeatherKitUnsupportedLocationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "unsupported_location"
            except WeatherKitApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except WeatherKitApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except WeatherKitApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_get_data_schema(self.hass),
            errors=_errors,
        )

    async def _test_config(self, user_input) -> None:
        """Validate credentials."""
        client = WeatherKitApiClient(
            key_id=user_input[CONF_KEY_ID],
            service_id=user_input[CONF_SERVICE_ID],
            team_id=user_input[CONF_TEAM_ID],
            key_pem=user_input[CONF_KEY_PEM],
            session=async_create_clientsession(self.hass),
        )

        availability = await client.get_availability(
            user_input[CONF_LATITUDE],
            user_input[CONF_LONGITUDE],
        )

        if not "currentWeather" in availability and not "forecastDaily" in availability:
            raise WeatherKitUnsupportedLocationError(
                "API does not support this location"
            )
