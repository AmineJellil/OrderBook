# python -m pip install requests

import json
import requests

URL = "http://20.76.107.117:443"

team_no = 17

traders = {
    "Team1": "FleVpNywpK5LvyZ5eoXkfwsYIPDAXa32",
    "Team2": "fd99AHzCT77106su5QujoLZDs4JF4Qig",
    "Team3": "UT5z9mn7NdXsjIFzrDq7vx6cETbE48tG",
    "Team4": "sQWbxtxYaFdqSrSETIvdsbmBV4vjLWy5",
    "Team5": "gwfCWTWtZmo34SNlxYLuuV7T2bTILu20",
    "Team6": "fqGUTcgAWYTlKOB4J28oP0WDc2HgxC6u",
    "Team7": "3gf0TWnlx3tUMAb0bcQp1ewOswBJK82Q",
    "Team8": "XI4hF0XP1LAPa1qGT61AZ7KqQN6D0in5",
    "Team9": "dn9xVRL8kyWALFgF8cYNQj4XQp4jaiXC",
    "Team10": "cXg72dE9KziTqbqDSGhBDFpj9T0Ri8YS",
    "Team11": "l58pVjXeLEAI6zcr9o0vTw1Vjw8QOHdd",
    "Team12": "ieEspEc0zVJd20XnUJn6rgApEvDYCEhs",
    "Team13": "lYd6gY9wAj8TU0MTlK9x9XFVFxDHcI9l",
    "Team14": "3tr50ahEg5isMS3sbT5COkjOxE9HPUJu",
    "Team15": "tVaFSXfW2r6JhfFNJWJqLpoFLLST5nMU",
    "Team16": "XMEENUrrsLjR3U54WEI547YQ1ulT4p7L",
    "Team17": "zzdlfWqKN7Nf3SCOr86foSeXgldTMGGQ",
}

def create_traders_from_json():
    api_url = URL + "/trader"
    for team_name,secret in traders.items():
        print('Creating trader ' + team_name)
      
        res = requests.post(api_url, json={"user_name": team_name, "secret": "Hackathon19","trader_id":secret})
        if res.status_code == 200:
            resp_json = json.loads(res.content.decode('utf-8'))
            print(team_name + ', ' + resp_json["trader_id"])
        else:
            print('Failed with response: ' + str(res))

def create_traders():
    api_url = URL + "/trader"
    for i in range(team_no):
        print('Creating trader ' + str(i))
        team_name = "Team" + str(i+1)
        res = requests.post(api_url, json={"user_name": team_name, "secret": "Hackathon19"})
        if res.status_code == 200:
            resp_json = json.loads(res.content.decode('utf-8'))
            print(team_name + ', ' + resp_json["trader_id"])
        else:
            print('Failed with response: ' + str(res))

if __name__ == '__main__':
    print('Creating new traders')
    create_traders()
    # Edit the JSON above and uncomment the below line (commenting the above one) if you want to create traders from existing IDs
    # create_traders_from_json()
