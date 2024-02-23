# Generated by ariadne-codegen
# Source: custom_components/solar_battery_forecast/octopus_api/queries.graphql

from typing import Any, Dict, Optional

from .account_query import AccountQuery, AccountQueryAccount
from .async_base_client import AsyncBaseClient
from .authenticate import Authenticate, AuthenticateObtainKrakenToken
from .saving_sessions_query import (
    SavingSessionsQuery,
    SavingSessionsQuerySavingSessions,
)


def gql(q: str) -> str:
    return q


class Client(AsyncBaseClient):
    async def authenticate(
        self, api_key: str, **kwargs: Any
    ) -> Optional[AuthenticateObtainKrakenToken]:
        query = gql(
            """
            mutation Authenticate($apiKey: String!) {
              obtainKrakenToken(input: {APIKey: $apiKey}) {
                token
              }
            }
            """
        )
        variables: Dict[str, object] = {"apiKey": api_key}
        response = await self.execute(
            query=query, operation_name="Authenticate", variables=variables, **kwargs
        )
        data = self.get_data(response)
        return Authenticate.model_validate(data).obtain_kraken_token

    async def account_query(
        self, account_number: str, **kwargs: Any
    ) -> Optional[AccountQueryAccount]:
        query = gql(
            """
            query AccountQuery($accountNumber: String!) {
              account(accountNumber: $accountNumber) {
                electricityAgreements(active: true) {
                  tariff {
                    __typename
                    ... on HalfHourlyTariff {
                      id
                      unitRates {
                        value
                        validTo
                        validFrom
                      }
                    }
                  }
                  meterPoint {
                    meters {
                      meterType
                      smartExportElectricityMeter {
                        deviceId
                      }
                      smartImportElectricityMeter {
                        deviceId
                      }
                    }
                  }
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"accountNumber": account_number}
        response = await self.execute(
            query=query, operation_name="AccountQuery", variables=variables, **kwargs
        )
        data = self.get_data(response)
        return AccountQuery.model_validate(data).account

    async def saving_sessions_query(
        self, account_number: str, **kwargs: Any
    ) -> Optional[SavingSessionsQuerySavingSessions]:
        query = gql(
            """
            query SavingSessionsQuery($accountNumber: String!) {
              savingSessions {
                events(getDevEvents: false) {
                  id
                  startAt
                  endAt
                  rewardPerKwhInOctoPoints
                }
                account(accountNumber: $accountNumber) {
                  hasJoinedCampaign
                  joinedEvents {
                    eventId
                    startAt
                    endAt
                  }
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"accountNumber": account_number}
        response = await self.execute(
            query=query,
            operation_name="SavingSessionsQuery",
            variables=variables,
            **kwargs
        )
        data = self.get_data(response)
        return SavingSessionsQuery.model_validate(data).saving_sessions