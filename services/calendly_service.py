from utils import schedule_calendly

class CalendlyService:
    def schedule(self, invitee_email: str, start_time: str):
        return schedule_calendly(invitee_email, start_time)

calendly = CalendlyService()
