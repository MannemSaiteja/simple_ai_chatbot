import requests

res = requests.get('http://127.0.0.1:8000/history/user1')
print(res.json()['response'])

# res1 = requests.delete('http://127.0.0.1:8000/clear/user1')
# print(res1.json()['response'])