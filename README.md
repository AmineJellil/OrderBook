# FX Trading Game
## Presentation

This project contains the code to run a simulated environment for algorithmic trading.
It is composed of:
* A [library](app/lib) containing the models and core application logic.
* A [server](app/sbin) acting as a Foreign eXchange (FX) trading platform responsible for:
  * Calculating and providing the current spot price for the designated currency.
  * Providing an API for traders to buy/sell the designated currency.
  * Keeping track of every trader's positions, even after a bounce of the server.
* A [client](app/cbin) which could be:
  * A [headless client](app/cbin/client) representing a trading algorithm.
  * A [GUI](app/cbin/gui) used mainly for display purposes but also containing some basic trading capabilities.

## Running from IDE

1. Ensure you have installed all the necessary [package dependencies](app/requirements.txt).
2. Start by launching the server using [api-server.py](app/sbin/api-server.py).
3. Once the server has started, list the available endpoint by clicking 'List Operations' at http://localhost:443/api/spec.html
4. Start the GUI via [gui-client.py](app/cbin/gui/gui-client.py).
5. Once the GUI has started, it is available at http://localhost:80.
6. To start trading, one must create at least one trader either via the provided script [create_traders.py](app/cbin/client/create_traders.py) or through the flask API.
7. Once the address of the server and the unique trader ID replaced in [client.py](app/cbin/client/client.py), it can be run to print the current price and trade once.

## Running on Azure

See [AzureDeployment.md](AzureDeployment.md).

## Example Scenario

* See [Trading Game - Student Brief](https://drive.google.com/file/d/1YgvjhZ83UgR1BQLR2eb-hY1A6pTnbY77/view?usp=sharing).
* See [Trading Game - Student Deck](https://docs.google.com/presentation/d/1ReLGsmMzjP_Ld1-5_6O_srezWOKjSQZDJXYgJ3DEq-8/edit?usp=share_link).
   

# Running an event
When running an event you should first have followed the above instructions have have the IP address or base URL from Azure to reach the API and GUI.

### The API
Stuendents are expected to interact with the API to trade, see positions and collect price values for analysis.    
You can show them how to see and use Swagger by navigating to `your_api_url_or_ip:443/api/specs.html` - here you can find all of the endpoints and see the template schemas.   

### Chronoligal events

 1. Start the activity at any time, the API can have been running for some time already, it does not matter.
 1. You can use the `/priceReset` endpoint to reset the price to about `0.86` and you can disable or enable trading via `/enableTrading` - these are admin endpoint which by default use the `Hackathon19` secret.
 1. Once trading is enabled, let students get accustomed to the API and play around with it, in the Discord you will find a few suggestions for strategies but also a basic explanation of the minimum set of actions to take to make some profits.
 1. Define a time when you start the challenge, when will crash the price, a later time when you will bounce it and the end time. Communicate these beforehand and on Discord as you move the price.
 1. Crash the price via `/priceSetter/EURGBP` and set it to about `1.20`, bounce itm later by setting it to about `0.60`
 1. You can use the `get_leaderboard.sh` unix script at the end of the game OR display this in a simple format via `cbin/client/display_price_leaderboard.py`

 