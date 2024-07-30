#Use Accuweather API to get current weather conditions at the observatory
# then post relevant information on Discord.

import asyncio
import logging
import nest_asyncio
nest_asyncio.apply()

from aiohttp import ClientError, ClientSession

from accuweather import (
    AccuWeather,
    ApiError,
    InvalidApiKeyError,
    InvalidCoordinatesError,
    RequestsExceededError,
)

from discord import SyncWebhook

#______________________________________________________________________________
# Observatory name: somewhere in Texas
LATITUDE = 30.1234567 # Negative for Southern hemisphere
LONGITUDE = -95.1234567 # Negative for West of Greenwhich

# Accuweather API key: to generate API key go to 
# https://developer.accuweather.com/user/register 
# and after registration create an app.
API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

logging.basicConfig(level=logging.DEBUG)

# Web hook for the telescope Discord server
# Get Webhook from Discord>Server settings>Integration>webhooks
webhook=SyncWebhook.from_url(r"https://discord.com/api/webhooks/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

# Verbosity: 0=quiet, 1 st dout, 2 std out and discord
verbosity=2


#______________________________________________________________________________
def Talk(verbosity, message, webhook=None):
    if verbosity >= 1:
        print(message)
    if verbosity >= 2 and webhook is not None:  
       try:
           webhook.send(message)
       except Exception as e:
           print("Exception while posting to Discord",e,message)
           
#______________________________________________________________________________
async def main():
    """Run main function."""
    async with ClientSession() as websession:
        try:
            accuweather = AccuWeather(
                API_KEY,
                websession,
                latitude=LATITUDE,
                longitude=LONGITUDE,
                language="en",
            )
            global current_conditions
            current_conditions = await accuweather.async_get_current_conditions()
            # forecast_daily = await accuweather.async_get_daily_forecast(
            #     days=5, metric=True
            # )
            # forecast_hourly = await accuweather.async_get_hourly_forecast(
            #     hours=12, metric=True
            # )
        except (
            ApiError,
            InvalidApiKeyError,
            InvalidCoordinatesError,
            ClientError,
            RequestsExceededError,
        ) as error:
            print(f"Error: {error}")
        else:
            print(f"Location: {accuweather.location_name} ({accuweather.location_key})")
            print(f"Requests remaining: {accuweather.requests_remaining}")
            print(f"Current: {current_conditions}")
            #print(f"Forecast: {forecast_daily}")
            #print(f"Forecast hourly: {forecast_hourly}")

loop = asyncio.new_event_loop()
loop.run_until_complete(main())
loop.close()

message="Current weather conditions at Prairie Sky Astro are:\n Cloud cover: "+\
        str(current_conditions['CloudCover'])+" percent"+\
        "\n Visibility: "+str(current_conditions['Visibility']['Metric']['Value'])+" km"+\
        "\n Current Weather: "+current_conditions['WeatherText']

Talk(verbosity, message, webhook)

