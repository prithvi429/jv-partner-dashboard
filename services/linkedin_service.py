from utils import linkedin_search

class LinkedInService:
    def search(self, name: str):
        return linkedin_search(name)

linkedin = LinkedInService()
