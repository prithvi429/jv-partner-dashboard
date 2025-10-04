from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import deals, outreaches, meetings, analytics

app = FastAPI(title="JV Partner Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(deals.router, prefix="/deals", tags=["deals"])
app.include_router(outreaches.router, prefix="/outreaches", tags=["outreaches"])
app.include_router(meetings.router, prefix="/meetings", tags=["meetings"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

@app.get("/")
async def root():
    return {"message": "JV Partner Dashboard API"}
