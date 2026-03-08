# export TRADING_SERVER=http://some_ip

echo "Team,Capital,nTrades"

for trader in "Team 1" "Team 2" "Team 3" "Team 4" "Team 5" "Team 6" "Team 7" "Team 8" "Team 9" "Team 10"; do

export trader=$trader

trader_id=$(curl -s $TRADING_SERVER:$TRADING_SERVER_PORT/traderQuery -H 'Content-Type: application/json' -d '{"user_name": "'"$trader"'", "secret": "'$SECRET'"}' | jq -r .trader_id)

capitals=$(curl -s $TRADING_SERVER:$TRADING_SERVER_PORT/normalizedCapitals)

curl -s $TRADING_SERVER:$TRADING_SERVER_PORT/tradeHistory > /tmp/trade_history.json

numTrades=$(cat /tmp/trade_history.json | jq --arg t "$trader" '.[] | select(.user_name==$t)' | grep "{" | wc -l)

echo "$trader, $(echo $capitals | jq '.[$ENV.trader']), $numTrades"

done
