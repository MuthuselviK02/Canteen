import urllib.request
import json

login_data = json.dumps({"email": "sharan@gmail.com", "password": "sharan@1230"}).encode("utf-8")
req = urllib.request.Request(
    "http://localhost:8000/api/auth/login",
    data=login_data,
    headers={"Content-Type": "application/json"}
)
resp = urllib.request.urlopen(req)
data = json.loads(resp.read().decode("utf-8"))
token = data["access_token"]
print("TOKEN", token[:20])
req2 = urllib.request.Request(
    "http://localhost:8000/api/analytics/dashboard?start_date=2026-04-08&end_date=2026-04-08",
    headers={"Authorization": f"Bearer {token}"}
)
resp2 = urllib.request.urlopen(req2)
analytics = json.loads(resp2.read().decode("utf-8"))
print(json.dumps(analytics, indent=2))
