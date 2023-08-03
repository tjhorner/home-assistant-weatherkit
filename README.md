# Home Assistant Apple WeatherKit Integration

This is a Home Assistant custom component which provides current weather and a daily forecast from Apple WeatherKit. If you are coming from Dark Sky, this is the closest you will get to the same data.

## Requirements

You will need a paid Apple Developer Program account to use the WeatherKit API. Unfortunately, this means you will need to pay the US$99/yr fee to use this integration. If you don't have one, maybe a kind friend with an account will let you use theirs.

## Installation

You can install this integration with HACS. Add this repository as a custom repository and install the "Apple WeatherKit" integration.

## Configuration

You will need to obtain the appropriate credentials which you will use to connect to Apple WeatherKit. We need to register a few things in your Apple Developer account:

1. Go to Certificates, Identifiers & Profiles in your Apple Developer account.
2. In the [Keys](https://developer.apple.com/account/resources/authkeys/list) section, add a new key.
    1. Name it whatever you want.
    2. Select "WeatherKit" from the list.
    3. Download the `.p8` file provided. This is your **Private Key**.
    4. Write down the **Key ID**. You will need it later.
3. In the [Identifiers](https://developer.apple.com/account/resources/identifiers/list) section, add a new identifier.
    1. Select "Services IDs" from the list.
    2. Write whatever you want for the description.
    3. For the identifier, I recommend using a reverse-DNS style name, like `com.example.homeassistant`.
    4. Save the identifier you used. This is your **Service ID**.

Now that you have all the credentials, you can add a new WeatherKit integration entry. This is done via the Home Assistant UI. Using the details from earlier, it should look something like this:

- **Key ID**: `ABC123DEFG`
- **Service ID**: `com.example.homeassistant`
- **Apple Team ID**: `ABC123DEFG`
  - This value can be found in the top-right of the Apple Developer website.
- **Private Key**: `-----BEGIN PRIVATE KEY----- [...]`
  - Open the `.p8` file you downloaded earlier in a text editor and copy the contents into this field.

Set the desired name, latitude, and longitude (by default they reflect your home's location) and submit. If all goes well, then you should see the new entry and weather entity in Home Assistant.

## A note regarding API limits

The WeatherKit API does have limits in place &mdash; by default each Apple Developer account can request 500,000 calls per month for free. This is quite a generous limit, and the entity only refreshes every 15 minutes, so it's very unlikely you will ever hit it, but it's worth knowing about if you are using WeatherKit for other projects, or have multiple WeatherKit integrations set up.