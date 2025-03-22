import requests
from models.webpage_scrapping import Webpage_Scraper
from models.web_scrapping import Website_Scraper
from urllib.parse import urlparse
from config.mongo_db import mongo_db
import pytz
from datetime import datetime
from langchain.schema import Document
from fastapi.responses import JSONResponse
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)


# To extract all the text from given website url
class WebScraper(Webpage_Scraper, Website_Scraper):
    def __init__(self, url: str):
        self.url = url
        self.db = mongo_db["RAG_DB"]
        self.docs_collection = self.db["Upload_Docs"]
        self.embedding_model = SentenceTransformerEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        self.time = self.current_time_and_date()

    ## Function for Current Time & Date as per timezone
    def current_time_and_date(self) -> tuple:
        try:
            # Define the user's timezone
            user_tz = pytz.timezone("Asia/Kolkata")

            # Get the current UTC time
            current_utc_time = datetime.now(tz=pytz.UTC)

            # Convert the current UTC time to the user's timezone
            current_datetime_in_tz = current_utc_time.astimezone(user_tz)

            # Format the current date and time in the specified format
            formatted_datetime = current_datetime_in_tz.strftime("%d-%m-%Y %I:%M %p")

            return formatted_datetime
        except Exception:
            return "00-00-0000 00:00 AM"

    # write python code to check the url is given by user is clickable or not
    def is_url_clickable(self):
        try:
            # Ensure URL starts with 'https://'
            check_url = (
                self.url if self.url.startswith("https://") else "https://" + self.url
            )

            # Check if the status code is in the range of successful responses
            response = requests.get(check_url, allow_redirects=True)
            return True if response.status_code < 400 else False

        except requests.RequestException as e:
            return JSONResponse(content={"message": f"Error: {str(e)}"})

    # Extract the text from the particular webpage url
    def extract_and_clean_text(self):
        try:
            # Parse the URL
            parsed_url = urlparse(self.url)

            # Get the path component of the URL
            path = parsed_url.path

            # Check if it's the landing page or about-us page
            if path == "/" or path == "":
                return self.extract_text_from_website()
            else:
                return self.extract_text_from_webpage()

        except Exception as e:
            return JSONResponse(
                content={
                    "message": "Retry it! May be website has protected to restriction of scrapping",
                    "error": str(e),
                },
                status_code=400,
            )

    # Split the cleaned text into chunks of 500 characters and load into documents
    def split_and_load_text_into_documents(self, chunk_size=500):
        try:
            cleaned_text = self.extract_and_clean_text()
            words = cleaned_text.split()
            chunks = [
                " ".join(words[i : i + chunk_size])
                for i in range(0, len(words), chunk_size)
            ]
            documents = [Document(page_content=chunk) for chunk in chunks]
            return documents
        except Exception as e:
            return JSONResponse(
                content={
                    "message": "Retry it! May be website has protected to restriction of scrapping",
                    "error": str(e),
                },
                status_code=400,
            )

    # Generate embeddings for text chunks and store in MongoDB
    def store_embeddings_in_mongodb(self, documents: list):
        try:
            for chunk in documents:
                embedding = self.embedding_model.embed_documents([chunk.page_content])[
                    0
                ]
                document = {
                    "url": self.url,
                    "text": chunk.page_content,
                    "embedding": embedding,
                    "date": self.time[0],
                    "time": self.time[1],
                    "status": 1,
                }
                self.docs_collection.insert_one(document)
            return JSONResponse(
                content={"message": "Web Scraping Successfully"}, status_code=200
            )
        except Exception:
            return JSONResponse(
                content={"message": "Retry it! Server Error"}, status_code=400
            )

    # Extract the text from the each webpage of the website and store in MongoDB
    def extracted_text_and_stored(self):
        try:
            if self.is_url_clickable() is True:
                documents = self.split_and_load_text_into_documents()
                self.store_embeddings_in_mongodb(documents)
                return JSONResponse(
                    content={"message": "Web Scraping Successfully"}, status_code=200
                )
            else:
                return JSONResponse(
                    content={
                        "message": "URL is not clickable. Copied it from the browser carefully"
                    },
                    status_code=400,
                )
        except Exception:
            return JSONResponse(
                content={"message": "Retry it! Server Error"}, status_code=400
            )
