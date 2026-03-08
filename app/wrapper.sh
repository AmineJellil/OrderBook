#bin/bash

python3 sbin/api-server.py &
status=$?
if [ $status -ne 0 ]; then
	echo "Failed to start server: $status"
	exit $status
fi

sleep 10

python3 cbin/gui/gui-client.py &
status=$?
if [ $status -ne 0 ]; then
	echo "Failed to start client: $status"
	exit $status
fi

python3 discord/discord_bot.py &
status=$?
if [ $status -ne 0 ]; then
	echo "Failed to start the discord bot: $status"
	exit $status
fi

control_c() {
	pkill -f "python3 sbin/api-server.py"
	pkill -f "cbin/gui/gui-client.py"
	pkill -f "discord/discord_bot.py"
}

trap control_c SIGINT

while sleep 60; do
	ps aux | grep api-server.py | grep -q -v grep
	SERVER_STATUS=$?
	ps aux | grep gui-client.py | grep -q -v grep
	CLIENT_STATUS=$?
	if [$SERVER_STATUS -ne 0 -o $CLIENT_STATUS -ne 0]; then
		echo "client or server exited"
		exit 1
	fi
done
