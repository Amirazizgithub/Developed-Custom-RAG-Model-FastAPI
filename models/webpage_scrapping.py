import requests
from bs4 import BeautifulSoup
from fastapi.responses import JSONResponse


# extract text from website or webpage
class Webpage_Scraper:
    def __init__(self, url: str):
        self.url = url

    # Extract the text from the particular webpage url
    def extract_text_from_particular_webpage(self):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            }
            response = requests.get(self.url, headers=headers)
            response.raise_for_status()  # Check for request errors
            soup = BeautifulSoup(response.content, "html.parser")
            all_text = soup.get_text()
            return all_text

        except requests.exceptions.RequestException as e:
            return JSONResponse(content={"message": str(e)}, status_code=400)

    # clean the extracted text
    def remove_header_footer_and_clean_text(self, all_text: str) -> str:
        # Split the text into lines
        lines = all_text.split("\n")

        # Join the remaining lines back together
        cleaned_text = "\n".join(lines)

        # Remove extra white spaces
        cleaned_text = " ".join(cleaned_text.split())

        return cleaned_text

    # Call the all functions to extract text from the website
    def extract_text_from_webpage(self):
        try:
            all_text = self.extract_text_from_particular_webpage()
            cleaned_text = self.remove_header_footer_and_clean_text(all_text)
            return cleaned_text
        except Exception as e:
            return JSONResponse(content={"message": str(e)}, status_code=400)
