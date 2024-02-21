# Generated by ariadne-codegen
# Source: custom_components/solar_battery_forecast/octopus_api/queries.graphql

from typing import Optional

from pydantic import Field

from .base_model import BaseModel


class Authenticate(BaseModel):
    obtain_kraken_token: Optional["AuthenticateObtainKrakenToken"] = Field(
        alias="obtainKrakenToken"
    )


class AuthenticateObtainKrakenToken(BaseModel):
    token: str
