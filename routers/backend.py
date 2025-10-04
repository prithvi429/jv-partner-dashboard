from fastapi import FastAPI
from routers import deals, outreaches, meetings, analytics

app = FastAPI(title="JV Partner Identification API")

app.include_router(deals.router)
app.include_router(outreaches.router)
app.include_router(meetings.router)
app.include_router(analytics.router)

# Add root endpoint for health check
@app.get("/")
def root():
    return {"message": "JV Partner Identification API is running"}
