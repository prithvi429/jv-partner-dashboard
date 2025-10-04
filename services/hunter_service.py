from utils import fetch_hunter_email

class HunterService:
    def lookup_domain(self, domain: str):
        return fetch_hunter_email(domain)

hunter = HunterService()
