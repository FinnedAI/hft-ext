import alpaca_trade_api as tradeapi
import config as CONFIG

account = tradeapi.REST(
  key_id=CONFIG.ALPACA_PUBLIC_KEY,
  secret_key=CONFIG.ALPACA_SECRET_KEY,
  base_url="https://paper-api.alpaca.markets",
  api_version="v2"
)

# Get a list of all of our positions.
portfolio = account.list_positions()

# Print the quantity of shares for each position.
print(portfolio)