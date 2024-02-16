import asyncio

from .graphql_client.client import Client


async def test():
    client = Client("https://api.octopus.energy/v1/graphql/", headers={"User-Agent": "Test"})
    response = await client.authenticate("")
    client = Client(
        "https://api.octopus.energy/v1/graphql/", headers={"User-Agent": "Test", "Authorization": response.token}
    )
    # client.headers["Authorization"] = f"{response.token}"
    # print(response.token)
    # print(client.headers)
    response = await client.account_query("")
    print(response)
    # response = await client.saving_sessions_query("")
    # print(response)


loop = asyncio.get_event_loop()
loop.run_until_complete(test())
