import requests

while True:
    url = "http://finalsqlite-servicebotusingsqllite.apps.rhocp.com"
    res = requests.get(url)
    print(res.text)

