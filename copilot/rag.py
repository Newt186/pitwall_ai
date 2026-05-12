from sentence_transformers import SentenceTransformer
import faiss as fs
import os
import numpy as np
import joblib
from groq import Groq
import sys
sys.path.append('.')
from config import GROQ_API_KEY


read_indx = fs.read_index('models/faiss.index') #read_indx to store faiss index model 
jb = joblib.load('models/chunks.pkl') # jb use to store joblib model 
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
client = Groq(api_key = GROQ_API_KEY)

def retrieve(question):
    Q_encode = model.encode([question]) #wrapped into listby []
    encoded_question = np.array(Q_encode, dtype=np.float32)
    _, idx = read_indx.search(encoded_question, 4) 
    return "\n\n ".join(jb[i] for i in idx[0])    #used list comprehension

def ask_copilot(question, history):
    context = retrieve(question)
    
    system_message = {
        "role": "system",
        "content": f"You are an expert F1 commentator and analyst. Use the following context to answer the fan's question in simple plain English. Keep answers concise and engaging.\n\nContext:\n{context}"
    }
    
    user_message = {
        "role": "user",
        "content": question
    }
    
    messages = [system_message] + history + [user_message]
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    
    return completion.choices[0].message.content
    

if __name__ == "__main__":
    history = []
    response = ask_copilot("What is an undercut?", history)
    print(response)


