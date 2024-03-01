import asyncio
import logging
import time
from datetime import datetime

import numpy as np
import pandas as pd

from .graphql_client.account_query import AccountQueryAccountElectricityAgreementsTariffHalfHourlyTariff
from .graphql_client.client import Client
from .graphql_client.exceptions import GraphQLClientGraphQLMultiError

URL_BASE = "https://api.octopus.energy/v1/graphql/"
USER_AGENT = "SolarBatteryForecast"
TOKEN_EXPIRY_SECS = 60 * 10
OCTOPOINTS_PER_PENCE = 8

_LOGGER = logging.getLogger(__name__)


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
                _LOGGER.info("Client is %ss old. Refreshing", now - self._authed_client_created)
                client = Client(URL_BASE, headers={"User-Agent": USER_AGENT})
                try:
                    response = await client.authenticate(self._api_key)
                    self._authed_client = Client(
                        URL_BASE, headers={"User-Agent": USER_AGENT, "Authorization": response.token}
                    )
                    self._authed_client_created = now
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

        df = pd.DataFrame(
            data={"import_tariff": pd.concat(import_tariffs), "feed_in_tariff": pd.concat(export_tariffs)}
        )

        # During a saving session, we save money based on the net amount that we export compared to normal. Fudge the
        # tariffs under the assumption that the baseline is 0, and set the same rate as the import and feed-in. This
        # isn't strictly true, as we're not actually penalised for importing more than we export in practice, but it's
        # good enough for the model
        saving_sessions = await client.saving_sessions_query(self._account_number)
        joined_event_ids = set()
        if saving_sessions.account.has_joined_campaign:
            for event in saving_sessions.account.joined_events:
                joined_event_ids.add(event.event_id)

        for saving_session in saving_sessions.events:
            if saving_session.id not in joined_event_ids:
                continue

            start_at = datetime.fromisoformat(saving_session.start_at)
            end_at = datetime.fromisoformat(saving_session.end_at)
            benefit = saving_session.reward_per_kwh_in_octo_points / OCTOPOINTS_PER_PENCE
            df[start_at:end_at] += benefit

        return df


class AuthenticationFailedError(Exception):
    pass
