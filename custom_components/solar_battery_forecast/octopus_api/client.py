import asyncio
import time

import numpy as np
import pandas as pd

from .graphql_client.account_query import AccountQueryAccountElectricityAgreementsTariffHalfHourlyTariff
from .graphql_client.client import Client
from .graphql_client.exceptions import GraphQLClientGraphQLMultiError

URL_BASE = "https://api.octopus.energy/v1/graphql/"
USER_AGENT = "SolarBatteryForecast"
TOKEN_EXPIRY_SECS = 60 * 60


class Tariff:
    pass


class OctopusApiClient:
    def __init__(self, account_number: str, api_key: str) -> None:
        self._account_number = account_number
        self._api_key = api_key
        self._authed_client_lock = asyncio.Lock()
        self._authed_client: Client | None = None
        self._authed_client_created = 0.0

    async def _auth_client(self) -> Client:
        now = time.monotonic()
        async with self._authed_client_lock:
            if self._authed_client is None or now - self._authed_client_created > TOKEN_EXPIRY_SECS:
                client = Client(URL_BASE, headers={"User-Agent": USER_AGENT})
                try:
                    response = await client.authenticate(self._api_key)
                    self._authed_client = Client(
                        URL_BASE, headers={"User-Agent": USER_AGENT, "Authorization": response.token}
                    )
                    self._authed_client_created = time.monotonic()
                except GraphQLClientGraphQLMultiError as ex:
                    raise AuthenticationFailedError() from ex
            return self._authed_client

    async def get_tariff(self) -> None:
        client = await self._auth_client()
        response = await client.account_query(self._account_number)
        import_tariffs = []
        export_tariffs = []

        for agreement in response.electricity_agreements:
            tariff: list[pd.Series] | None = None

            for meter in agreement.meter_point.meters:
                if meter.smart_import_electricity_meter is not None:
                    tariff = import_tariffs
                else:
                    tariff = export_tariffs

            if tariff is None:
                continue

            if isinstance(agreement.tariff, AccountQueryAccountElectricityAgreementsTariffHalfHourlyTariff):
                for x in agreement.tariff.unit_rates:
                    idx = pd.date_range(start=x.valid_from, end=x.valid_to, freq="30min", inclusive="left")
                    tariff.append(pd.Series(np.repeat(x.value, len(idx)), index=idx))

        df = pd.DataFrame(data={"import": pd.concat(import_tariffs), "export": pd.concat(export_tariffs)})
        return df


async def test():
    client = OctopusApiClient("", "")
    print(await client.get_tariff())


class AuthenticationFailedError(Exception):
    pass


loop = asyncio.get_event_loop()
loop.run_until_complete(test())
