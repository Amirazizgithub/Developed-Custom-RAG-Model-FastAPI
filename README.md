# Developed-Custom-RAG-Model-FastAPI

I've developed a custom RAG model that enables users to upload files (.pdf, .docx, & .txt) and scrape web content for querying. You can then query either your uploaded files (via a knowledge graph) or leverage AI LLMs, including Gemini, OpenAI, and Llama.

## Developed custom Retrieval-Augmented Generation (RAG) Model

This RAG model includes two key functionalities to provide efficient querying:

### 1. File Upload Support:
- Users can upload files in various formats, such as .pdf, .docx, and .txt. The system processes these files and builds a knowledge graph, enabling structured representation of the extracted content. Users can directly query this knowledge graph to retrieve relevant information.

### 2. Web Scraping Capability:
- The model incorporates web scraping tools to gather dynamic and up-to-date information from the internet, complementing the knowledge graph with live content for broader retrieval options.

### 3. Flexible Query Options:
Users can choose between:
- Knowledge Graph Querying: Extract information exclusively from uploaded files using the organized content representation.
- AI Language Models: Employ advanced generative models, such as Gemini, OpenAI, or Llama, to handle queries with contextual depth and reasoning, offering broader and more sophisticated results.

This system bridges structured document knowledge with cutting-edge AI capabilities, providing users with a versatile platform for both static and dynamic content retrieval.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/Developed-Custom-RAG-Model-FastAPI.git
    ```
    ```sh
    cd Developed-Custom-RAG-Model-FastAPI
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    ```
    Activate the virtual environment:
    ```sh
    source venv/bin/activate
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up environment variables:
    - Create a `.env` file in the root directory and add the following:
        ```env
        MONGODB_CONNECTION_STRING_URI=your_mongodb_connection_string
        CHATGPT_API_KEY=your_openai_api_key
        GEMINI_API_KEY=your_gemini_api_key
        LLAMA_MODEL_API_KEY=your_llama_api_key
        ```

## Usage

1. Start the FastAPI server:
    ```sh
    uvicorn index:app --reload
    ```

2. Access the API documentation:
    - Open your browser and navigate to `http://127.0.0.1:8000/docs` to explore the available endpoints.

### Endpoints

- **Upload Files and Extract Text:**
    - Endpoint: `/rag_model/read_upload_file`
    - Method: `POST`
    - Description: Upload a file and extract text to store embeddings in MongoDB.
    - Example:
        ```sh
        curl -X POST "http://127.0.0.1:8000/rag_model/read_upload_file" -F "file_path=@path/to/your/file.pdf"
        ```

- **Web Scraping:**
    - Endpoint: `/rag_model/web_scraping`
    - Method: `POST`
    - Description: Scrape a web page or website (100 direct urls only) and store the extracted text in MongoDB.
    - Example:
        ```sh
        curl -X POST "http://127.0.0.1:8000/rag_model/web_scraping" -H "Content-Type: application/json" -d '{"url": "https://example.com"}'
        ```

- **Query Response:**
    - Endpoint: `/rag_model/query_response`
    - Method: `POST`
    - Description: Get a response to a user query using the specified AI model.
    - Example:
        ```sh
        curl -X POST "http://127.0.0.1:8000/rag_model/query_response" -H "Content-Type: application/json" -d '{"ai_model": "openai", "user_query": "What is the capital of France?", "temperature": 0.7, "model_type": "AI"}'
        ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.