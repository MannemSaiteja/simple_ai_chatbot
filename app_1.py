""""
FastAPI is a modern Python web framework used to build high-performance APIs.
It provides automatic data validation using Pydantic, supports asynchronous programming, and
 generates interactive API documentation using Swagger UI.
"""
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
import os
from openai import OpenAI
import google.generativeai as genai


app = FastAPI() # fastapi object/create fastapi app

# @app.get("/")
# def hello_world():
#     return {"message": "Hello worlds"}

load_dotenv()  # This reads your .env file like:
# openai_client = OpenAI(api_key=os.getenv("api_key")) # Initialize OpenAI Client

genai.configure(api_key=os.getenv("g_key"))

model = genai.GenerativeModel("gemini-2.5-flash")

# In-memory storage/state data is stored in ram (session_id -> messages)
chat_conv = {}

class ChatRequest(BaseModel):   # Request Body
    message: str
    session_id: str # Session storage - Storing user-specific data

@app.post("/chat")
def chat(request: ChatRequest):
    # response = openai_client.responses.create(
    #     model="gpt-4o-mini",
    #     input=request.message
    # )
    try:
        if request.session_id not in chat_conv:
            chat_conv[request.session_id] = []
        chat_conv[request.session_id].append(f'User: {request.message}')
        # Prepare full conversation
        conversation = '\n'.join(chat_conv[request.session_id])
        # send convo to gemini
        # response = model.generate_content(f"You are a helpful career assistant.\n{conversation}") # Model Initialization
        response = model.generate_content(f"\n{conversation}") # Model Initialization
        ai_rply = response.text
        chat_conv[request.session_id].append(f'ai_rply: {ai_rply}')
        print(chat_conv)
        # print(conversation)
        return {
            "response": ai_rply
        }
    except Exception as e:
        return {"response": str(e)}


# get chat history
@app.get("/history/{session_id}")
def get_history(session_id: str):
    try:
        if session_id not in chat_conv:
            print(session_id)
            print(chat_conv)
            return {"response": "no session_id found "}
        return {'response': chat_conv[session_id]}
    except Exception as e:
        return {'response': f'error: {str(e)}'}

# clear chat history
@app.delete("/clear/{session_id}")
def clear_chat(session_id: str):
    try:
        if session_id not in chat_conv:
            return {"response": "session_id not found"}
        del chat_conv[session_id]
        return {'response': 'successfully deleted chat history'}
    except Exception as e:
        print(str(e))




if __name__ == "__main__":
    uvicorn.run("app_1:app") # here if we use reload = True the temporary memory which we used
    # chat_conv dict will become empty list bcz the uvicorn restarts the server everytime it detect
    # changes