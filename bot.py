from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import yt_dlp
import uuid
import os

app = Flask(__name__, static_url_path='/static')

# Twilio credentials from environment variables
account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.form.get("Body")
    from_number = request.form.get("From")

    if "http" in incoming_msg:
        filename = f"{uuid.uuid4()}.mp4"
        out_path = f"static/{filename}"

        ydl_opts = {'outtmpl': out_path, 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([incoming_msg])
            except Exception as e:
                resp = MessagingResponse()
                resp.message("❌ Download failed: " + str(e))
                return str(resp)

        file_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/static/{filename}"
        client.messages.create(
            body="✅ Here is your video:",
            from_="whatsapp:+14155238886",
            to=from_number,
            media_url=[file_url]
        )

    resp = MessagingResponse()
    return str(resp)

@app.route('/')
def home():
    return "✅ WhatsApp Video Bot is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
