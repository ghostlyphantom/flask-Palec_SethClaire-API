import requests

url = "https://flask-palec-sethclaire-api.onrender.com/course"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()

    print("Course:", data["course"])
    print("Instructor:", data["instructor"])
    print("Schedule:", data["schedule"])

else:
    print("Request failed.")
    print("Status Code:", response.status_code)