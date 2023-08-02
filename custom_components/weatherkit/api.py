"""Sample API Client."""
from __future__ import annotations

import asyncio
import socket

import aiohttp
import async_timeout
import datetime

import jwt


class WeatherKitApiClientError(Exception):
    """Exception to indicate a general API error."""


class WeatherKitApiClientCommunicationError(WeatherKitApiClientError):
    """Exception to indicate a communication error."""


class WeatherKitApiClientAuthenticationError(WeatherKitApiClientError):
    """Exception to indicate an authentication error."""


class WeatherKitApiClient:
    def __init__(
        self,
        key_id: str,
        service_id: str,
        team_id: str,
        key_pem: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self._key_id = key_id
        self._service_id = service_id
        self._team_id = team_id
        self._key_pem = key_pem
        self._session = session

    async def get_weather_data(
        self, lat: float, lon: float, lang: str = "en-US"
    ) -> any:
        """OBTAIN WEATHER DATA!!!!!!!!!!"""
        token = self._generate_jwt()
        return await self._api_wrapper(
            method="get",
            url=f"https://weatherkit.apple.com/api/v1/weather/{lang}/{lat}/{lon}?dataSets=currentWeather,forecastDaily",
            headers={"Authorization": f"Bearer {token}"},
        )

    async def get_availability(self, lat: float, lon: float) -> any:
        """Determine availability of different weather data sets."""
        token = self._generate_jwt()
        return await self._api_wrapper(
            method="get",
            url=f"https://weatherkit.apple.com/api/v1/availability/{lat}/{lon}",
            headers={"Authorization": f"Bearer {token}"},
        )

    def _generate_jwt(self) -> str:
        return jwt.encode(
            {
                "iss": self._team_id,
                "iat": datetime.datetime.utcnow(),
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=1),
                "sub": self._service_id,
            },
            self._key_pem,
            headers={"kid": self._key_id, "id": f"{self._team_id}.{self._service_id}"},
            algorithm="ES256",
        )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                if response.status in (401, 403):
                    raise WeatherKitApiClientAuthenticationError(
                        "Invalid credentials",
                    )
                response.raise_for_status()
                return await response.json()

        except WeatherKitApiClientAuthenticationError as exception:
            raise exception
        except asyncio.TimeoutError as exception:
            raise WeatherKitApiClientCommunicationError(
                "Timeout error fetching information",
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise WeatherKitApiClientCommunicationError(
                "Error fetching information",
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            raise WeatherKitApiClientError(
                "Something really wrong happened!"
            ) from exception
