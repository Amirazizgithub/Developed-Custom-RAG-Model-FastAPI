import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from fastapi.responses import JSONResponse


# To extract all the text from given website url
class Website_Scraper:
    def __init__(self, url: str):
        self.url = url

    # Find all the URLs on the website
    def get_all_urls(self) -> list:
        response = requests.get(self.url)
        response.raise_for_status()

        # Check if the request was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a", href=True)
            urls = [urljoin(self.url, link["href"]) for link in links]
            urls = list(set(urls))

        return urls

    # write python code to remove indirect hyperlinks urls from the extracted urls
    def separate_direct_urls(self, all_urls: list) -> list:
        direct_urls = []
        # Check if the URL starts with the base URL
        for url in all_urls:
            if url.startswith(self.url):
                direct_urls.append(url)
        return direct_urls

    # Extract the text from the each webpage of the website
    def scrape_and_accumulate(self, accumulated_text: str, url: str) -> str:
        # Send a GET request to the URL
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Check if the request was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Extract the relevant data from the webpage
            data = soup.get_text()
            # Remove extra white spaces and accumulate text
            encoded_text = " ".join(data.split())
            accumulated_text += encoded_text + "\n\n"

        return accumulated_text

    # clean the extracted text
    def remove_header_footer_and_clean_text(self, accumulated_text: str) -> str:
        # Split the text into lines
        lines = accumulated_text.split("\n")

        # Join the remaining lines back together
        cleaned_text = "\n".join(lines)

        # Remove extra white spaces
        cleaned_text = " ".join(cleaned_text.split())

        return cleaned_text

    # Call the all functions to extract text from the website
    def extract_text_from_website(self):
        try:
            all_urls = self.get_all_urls()
            if len(all_urls) < 100:
                direct_urls = self.separate_direct_urls(all_urls)
            else:
                return JSONResponse(
                    content={
                        "message": "This website having more than 100 URLs to scrape"
                    },
                    status_code=200,
                )

            accumulated_text = ""
            for url in direct_urls:
                accumulated_text += self.scrape_and_accumulate(accumulated_text, url)

            clean_text = self.remove_header_footer_and_clean_text(accumulated_text)
            return clean_text
        except Exception as e:
            return JSONResponse(content={"message": str(e)}, status_code=400)
