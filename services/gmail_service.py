from utils import send_gmail_message

class GmailService:
    def send(self, to: str, subject: str, body: str):
        return send_gmail_message(to, subject, body)

gmail = GmailService()
