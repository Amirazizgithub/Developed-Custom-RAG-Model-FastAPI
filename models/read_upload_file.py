from config.mongo_db import mongo_db
from datetime import datetime
from fastapi.responses import JSONResponse
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
import warnings
warnings.filterwarnings("ignore")

class TextProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.db = mongo_db["RAG_DB"]
        self.docs_collection = self.db["Upload_Docs"]
        self.text_chunks = []

    ## Extract the text from pdf, docx & text files
    def extract_text(self):
        try:
            ## Load the data from pdf file
            if self.file_path.lower().endswith(".pdf"):
                loader = PyPDFLoader(self.file_path)
                documents = loader.load_and_split()
                text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=10)
                text = text_splitter.split_documents(documents)
                self.text_chunks += text
                return self.text_chunks

            ## Load the data from text file
            elif self.file_path.lower().endswith(".txt"):
                loader = TextLoader(self.file_path)
                documents = loader.load()
                text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=10)
                text = text_splitter.split_documents(documents)
                self.text_chunks += text
                return self.text_chunks

            ## Load the data from docx file
            elif self.file_path.lower().endswith(".docx"):
                loader = Docx2txtLoader(self.file_path)
                documents = loader.load()
                text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=10)
                text = text_splitter.split_documents(documents)
                self.text_chunks += text
                return self.text_chunks
        
            ## File format not supported
            else:
                return JSONResponse(
                    content={"message": "File format not supported. Please upload pdf, docx or txt file."}, status_code=400
                )
        except Exception as e:
            return JSONResponse(
                content={"message": "Retry it! File not read and extract text from it.", "error": str(e)}, status_code=400
            )

    # Generate embeddings for text chunks and store in MongoDB
    def store_embeddings_in_mongodb(self) -> None:
        embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        for chunk in self.text_chunks:
            embedding = embedding_model.embed_documents([chunk.page_content])[0]
            document = {
                "text": chunk.page_content,
                "embedding": embedding,
                "timestamp": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                "status": 1
            }
            self.docs_collection.insert_one(document)
        return None
    
    # Read the file and store the embeddings in MongoDB
    def read_file_and_store_embeddings(self):
        try:
            self.extract_text()
            self.store_embeddings_in_mongodb()
            return JSONResponse(
                content={"message": "File read and embeddings stored successfully."}, status_code=200
            )
        except Exception as e:
            return JSONResponse(
                content={"message": "Retry it! File not read and store embeddings in MongoDB.", "error": str(e)}, status_code=400
            )
