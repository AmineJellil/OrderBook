# export TRADING_SERVER=http://some_ip
# export SECRET 


# remember that a price crash causes the price of EURGBP to rise, and vice-versa

#price crash
# PRICE=1.244
#curl -X POST -H 'Content-Type: application/json' -d '{"secret": "'${SECRET}'", "price": "'${PRICE}'"}' $TRADING_SERVER:$TRADING_SERVER_PORT/priceSetter/EURGBP



#price surge
# PRICE=0.622
#curl -X POST -H 'Content-Type: application/json' -d '{"secret": "'${SECRET}'", "price": "'${PRICE}'"}' $TRADING_SERVER:$TRADING_SERVER_PORT/priceSetter/EURGBP
