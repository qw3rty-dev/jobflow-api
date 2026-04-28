import requests
from dotenv import load_dotenv
import os


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

CHAT_ID = os.getenv("CHAT_ID")

def send_telegram_alert(new_jobs):
    
    message= "New jobs:\n\n"
    

    for i,job in enumerate(new_jobs[:20],1):
        message+= f"{i}. {job['title']} at {job['company']}\nLocation: {job['location']}\n{job['link']}\n\n"
    url= f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(url,data={"chat_id": CHAT_ID,
                                "text":message})
    
