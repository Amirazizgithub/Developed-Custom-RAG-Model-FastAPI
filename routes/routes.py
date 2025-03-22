# Path: routes/routes.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from models.read_upload_file import TextProcessor
from models.scrapping import WebScraper
from models.openai_model import OpenAI_Model
from models.gemini_model import Gemini_Model
from models.llama_model import Llama_Model

## Global Route
router = APIRouter()


# Endpoint to upload files
@router.post("/read_upload_file")
async def read_file_and_extract_text(request: Request):
    data = await request.form()
    file_path = data["file_path"]
    try:
        return TextProcessor(file_path).read_file_and_store_embeddings()
    except Exception as e:
        return JSONResponse(
            content={"message": "API Error", "Error": str(e)}, status_code=200
        )


# Endpoint to web scrapping
@router.post("/web_scraping")
async def web_scrapping(request: Request):
    data = await request.json()
    url = data["url"]
    try:
        web_scraper_obj = WebScraper(url)
        return web_scraper_obj.extracted_text_and_stored()
    except Exception as e:
        return JSONResponse(
            content={"message": "API Error", "Error": str(e)}, status_code=200
        )


# Endpoint to response of user query
@router.post("/query_response")
async def response_of_user_query(request: Request):
    data = await request.json()
    ai_model = data["ai_model"]
    try:
        if ai_model == "openai":
            OpenAI_Model_obj = OpenAI_Model(data=data)
            return OpenAI_Model_obj.response_to_user_from_oepnai_model()
        elif ai_model == "gemini":
            Gemini_Model_obj = Gemini_Model(data=data)
            return Gemini_Model_obj.response_to_user_from_gemini_model()
        elif ai_model == "llama":
            Llama_Model_obj = Llama_Model(data=data)
            return Llama_Model_obj.response_to_user_from_llama_model()
        else:
            return JSONResponse(
                content={"message": "Invalid model type"}, status_code=400
            )
    except Exception as e:
        return JSONResponse(
            content={"message": "API Error", "Error": str(e)}, status_code=200
        )
 