from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uvicorn import run as app_run

APP_HOST = "0.0.0.0"
APP_PORT = 8080

app = FastAPI()

# Ensure the static directory is correctly mounted
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["authentication"])
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/submit_query")
async def submit_query(
    request: Request,
    ai_model: str = Form(...),
    model_type: str = Form(...),
    temperature: float = Form(...),
    user_query: str = Form(...)
):
    # Process the form data here
    # For now, just return the received data as a response
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "ai_model": ai_model,
            "model_type": model_type,
            "temperature": temperature,
            "user_query": user_query,
        },
    )

if __name__ == "__main__":
    app_run(app, host=APP_HOST, port=APP_PORT)