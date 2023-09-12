"""Custom integration to integrate weatherkit with Home Assistant.

For more details about this integration, please refer to
https://github.com/tjhorner/home-assistant-weatherkit
"""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    Platform,
    MAJOR_VERSION,
    MINOR_VERSION,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.components.persistent_notification import (
    DOMAIN as PERSISTENT_NOTIFICATION_DOMAIN,
)
from homeassistant.helpers.issue_registry import async_create_issue, IssueSeverity

from .api import WeatherKitApiClient
from .const import DOMAIN, CONF_KEY_ID, CONF_SERVICE_ID, CONF_TEAM_ID, CONF_KEY_PEM
from .coordinator import WeatherKitDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.WEATHER]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    if MAJOR_VERSION == 2023 and MINOR_VERSION >= 10:
        async_create_issue(
            hass,
            DOMAIN,
            "custom_integration_deprecated",
            is_fixable=False,
            translation_key="custom_component_deprecated",
            learn_more_url="https://github.com/tjhorner/home-assistant-weatherkit/wiki/Migrate-to-Official-Integration",
            severity=IssueSeverity.WARNING,
        )

        await hass.services.async_call(
            PERSISTENT_NOTIFICATION_DOMAIN,
            "create",
            {
                "notification_id": "weatherkit_update",
                "title": "Please update WeatherKit integration",
                "message": 'The WeatherKit integration has been moved into Home Assistant core. Please remove the custom component (e.g., via HACS) and restart Home Assistant. See more details <a href="https://github.com/tjhorner/home-assistant-weatherkit/wiki/Migrate-to-Official-Integration">here</a>.',
            },
        )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator = WeatherKitDataUpdateCoordinator(
        hass=hass,
        client=WeatherKitApiClient(
            key_id=entry.data[CONF_KEY_ID],
            service_id=entry.data[CONF_SERVICE_ID],
            team_id=entry.data[CONF_TEAM_ID],
            key_pem=entry.data[CONF_KEY_PEM],
            session=async_get_clientsession(hass),
        ),
    )
    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
