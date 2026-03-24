import requests

res = requests.post('http://127.0.0.1:8000/chat', json={'session_id': "user1", 'message': 'hi gemini what is my name'})
print(res.json()['response'])