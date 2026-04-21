import requests
url = "https://kai-xiu2026-a.vercel.app/about"
Data = requests.get(url)
print(Data.text)
