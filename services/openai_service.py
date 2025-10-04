"""
OpenAI service for AI features (emails, summaries, classification).
Easy to change: Swap model or add prompts here.
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_ai_email(stakeholder_name: str, company_name: str, product_name: str) -> str:
    """
    Generate personalized outreach email.
    Returns: Email text or default on error.
    """
    if not client.api_key:
        return "Dear [Name],\nWe're interested in JV opportunities with [Company] on [Product].\nBest,\nYour Team"
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional BD expert. Write concise, personalized JV outreach emails (under 200 words)."},
                {"role": "user", "content": f"Email to {stakeholder_name} ({company_name}) about JV on {product_name}. Highlight mutual benefits."}
            ],
            max_tokens=250,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI email generation error: {e}")
        return "Default email template."

def summarize_jv_fit(product_desc: str, company_industry: str) -> str:
    """
    Summarize why JV makes sense.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Provide 3-5 sentence summaries of JV fit."},
                {"role": "user", "content": f"Product desc: {product_desc}. Company industry: {company_industry}."}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI summary error: {e}")
        return "Strong alignment due to complementary capabilities."

def classify_response(response_text: str) -> str:
    """
    Classify response: 'interested', 'not-interested', 'no-response', 'follow-up-needed'.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Classify JV responses briefly."},
                {"role": "user", "content": f"Classify: {response_text}. Output only: interested/not-interested/no-response/follow-up-needed."}
            ],
            max_tokens=10
        )
        tag = response.choices[0].message.content.strip().lower()
        if 'interested' in tag:
            return 'interested'
        elif 'not' in tag:
            return 'not-interested'
        elif 'follow' in tag:
            return 'follow-up-needed'
        return 'no-response'
    except Exception as e:
        print(f"OpenAI classification error: {e}")
        return 'no-response'