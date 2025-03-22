from config.mongo_db import mongo_db
from fastapi.responses import JSONResponse
import pytz
from datetime import datetime
import numpy as np
import os
from huggingface_hub import InferenceClient
from sklearn.metrics.pairwise import cosine_similarity
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from dotenv import load_dotenv

load_dotenv()


class Llama_Model:
    def __init__(self, data: dict):
        self.db = mongo_db["RAG_DB"]
        self.docs_collection = self.db["Upload_Docs"]
        self.history_collection = self.db["RAG_History"]
        self.llama_client = InferenceClient(
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            token=os.getenv("LLAMA_MODEL_API_KEY"),
        )
        self.SentenceTransformerEmbeddings = SentenceTransformerEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        self.user_query = data["user_query"]
        self.temperature = data["temperature"]
        self.model_type = data["model_type"]
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
            formatted_date = current_datetime_in_tz.strftime("%d-%m-%Y")
            formatted_time = current_datetime_in_tz.strftime("%H:%M:%S")

            return formatted_date, formatted_time
        except Exception:
            return "00-00-0000", "00:00:00"

    def generate_query_embedding(self):
        try:
            embedding_model = self.SentenceTransformerEmbeddings
            user_query_embedding = embedding_model.embed_documents([self.user_query])
            return user_query_embedding
        except Exception:
            return JSONResponse(
                content={"message": "Network issue! Retry it"}, status_code=400
            )

    def find_similar_documents(self, user_query_embedding, threshold=0.5, top_k=10):
        try:
            cursor = self.docs_collection.find({})
            documents = []
            for doc in cursor:
                documents.append({"text": doc["text"], "embedding": doc["embedding"]})

            if documents:
                embeddings = [doc["embedding"] for doc in documents]
                cos_sim = cosine_similarity(user_query_embedding, embeddings)[0]
                top_k_indices = np.argsort(cos_sim)[-top_k:][::-1]
                top_documents = [
                    documents[i]["text"]
                    for i in top_k_indices
                    if cos_sim[i] >= threshold
                ]
                return top_documents
            else:
                return []
        except Exception:
            return JSONResponse(
                content={"message": "Network issue! Retry it"}, status_code=400
            )

    def generate_response_from_llama_01(self, top_documents) -> str:
        context = " ".join([doc for doc in top_documents])
        specific_prompt = (
            f"You are a helpful assistant which generates a response to the user query from the given context. Provide the response in the html format like <!DOCTYPE html> <html> <body> <h3> <h3> <p></p> </body> </html>. \n"
            f"If the user query's meaningful response is not found in the context, then generate a good and meaningful response on your own.\n"
            f"The response should be in a tone like neutral, style like informative.\n"
            f"Ensure the response starts with a strong and relevant opening sentence but not include in response like Opening Sentence.\n"
            f"Handle follow-up queries like explain more, explain in detail, explaint pointwise, explain in n numnber of words, etc.\n"
            f"User Query: {self.user_query}\n"
            f"Context: {context}\n"
            f"Response:"
        )

        response_content = ""
        for message in self.llama_client.chat_completion(
            messages=[
                {"role": "system", "content": specific_prompt},
                {"role": "user", "content": self.user_query},
            ],
            max_tokens=2000,
            temperature=self.temperature,
            stream=True,
        ):
            response_content += message["choices"][0]["delta"]["content"]

        return response_content

    def generate_response_from_llama_02(self) -> str:
        specific_prompt = (
            f"You are a helpful assistant which generates a response to the user query. Provide the response in the html format like <!DOCTYPE html> <html> <body> <h3> <h3> <p></p> </body> </html>.\n"
            f"The response should be in a tone like neutral, style like informative.\n"
            f"Ensure the response starts with a strong and relevant opening sentence but not include in response like Opening Sentence.\n"
            f"User Query: {self.user_query}\n"
            f"Response:"
        )

        response_content = ""
        for message in self.llama_client.chat_completion(
            messages=[
                {"role": "system", "content": specific_prompt},
                {"role": "user", "content": self.user_query},
            ],
            max_tokens=2000,
            temperature=self.temperature,
            stream=True,
        ):
            response_content += message["choices"][0]["delta"]["content"]

        return response_content

    def get_user_recent_history(self):
        try:
            data = (
                self.history_collection.find(
                    {}, {"_id": 0, "user_query": 1, "response": 1, "top_documents": 1}
                )
                .sort("_id", -1)
                .limit(1)
            )
            recent_history = list(data)
            return recent_history
        except Exception:
            return None

    def generate_response_embedding(self, previous_response, response):
        try:
            embedding_model = self.SentenceTransformerEmbeddings
            previous_response_embedding = embedding_model.embed_documents(
                [previous_response]
            )
            response_embedding = embedding_model.embed_documents([response])
            return previous_response_embedding, response_embedding
        except Exception:
            return None

    # Store the session history in MongoDB
    def session_history(self, response, top_documents) -> None:
        responseData = {
            "user_query": self.user_query,
            "response": response,
            "top_documents": top_documents,
            "date": self.time[0],
            "time": self.time[1],
            "del": 0,
        }
        self.history_collection.insert_one(responseData)
        return None

    def response_to_user_from_knowledge_graph(self):
        try:
            user_query_embedding = self.generate_query_embedding()
            top_documents = self.find_similar_documents(
                user_query_embedding, threshold=0.6, top_k=10
            )

            # If the user query is found in the context
            if top_documents:
                response = self.generate_response_from_llama_01(top_documents)
                response = response.replace("\n", "")
                if response:
                    self.session_history(response, top_documents)
                    return JSONResponse(content={"message": response}, status_code=200)
                return JSONResponse(
                    content={
                        "message": "Please, Give the feedback for the better response."
                    },
                    status_code=200,
                )

            # If the user query is not found in the context
            elif not top_documents:
                recent_history = self.get_user_recent_history()
                if recent_history:
                    previous_response = recent_history[0]["response"]
                    previuos_top_documents = recent_history[0]["top_documents"]
                    response = self.generate_response_from_llama_01(
                        previuos_top_documents
                    )
                    response = response.replace("\n", "")
                    previous_response_embedding, response_embedding = (
                        self.generate_response_embedding(previous_response, response)
                    )
                    cos_sim = cosine_similarity(
                        previous_response_embedding, response_embedding
                    )[0]
                    if cos_sim > 0.6:
                        self.session_history(response, previuos_top_documents)
                        return JSONResponse(
                            content={"message": response}, status_code=200
                        )
                    elif cos_sim < 0.6:
                        return JSONResponse(
                            content={
                                "message": "No relevant documents found in the PDF collection."
                            },
                            status_code=200,
                        )
                else:
                    return JSONResponse(
                        content={
                            "message": "No relevant documents found in the PDF collection."
                        },
                        status_code=200,
                    )

            return JSONResponse(
                content={
                    "message": "No relevant documents found in the PDF collection."
                },
                status_code=200,
            )
        except Exception as e:
            return JSONResponse(
                content={"message": "Failed to generate a response.", "error": str(e)},
                status_code=500,
            )

    def response_to_user_from_knowledge_graph_and_Llama(self):
        try:
            user_query_embedding = self.generate_query_embedding()
            top_documents = self.find_similar_documents(
                user_query_embedding, threshold=0.5, top_k=10
            )

            if top_documents:
                response = self.generate_response_from_llama_01(top_documents)
                response = response.replace("\n", "")
                if response:
                    return JSONResponse(
                        content={
                            "message": response,
                        },
                        status_code=200,
                    )
                return JSONResponse(
                    content={
                        "message": "Please, Give the feedback for the better response"
                    },
                    status_code=200,
                )

            elif not top_documents:
                recent_history = self.get_user_recent_history()
                if recent_history:
                    previous_response = recent_history[0]["response"]
                    previuos_top_documents = recent_history[0]["top_documents"]
                    response = self.generate_response_from_llama_01(
                        previuos_top_documents
                    )
                    response = response.replace("\n", "")
                    previous_response_embedding, response_embedding = (
                        self.generate_response_embedding(previous_response, response)
                    )
                    cos_sim = cosine_similarity(
                        previous_response_embedding, response_embedding
                    )[0]
                    if cos_sim > 0.5:
                        return JSONResponse(
                            content={
                                "message": response,
                            },
                            status_code=200,
                        )
                    elif cos_sim < 0.5:
                        response = self.generate_response_from_llama_02()
                        response = response.replace("\n", "")
                        return JSONResponse(
                            content={
                                "message": response,
                            },
                            status_code=200,
                        )
            return JSONResponse(
                content={
                    "message": "Please, Give the feedback for the better response"
                },
                status_code=200,
            )
        except Exception as e:
            return JSONResponse(
                content={"message": "Failed to generate a response.", "error": str(e)},
                status_code=500,
            )

    def response_to_user_from_Llama(self):
        try:
            response = self.generate_response_from_llama_02()
            response = response.replace("\n", "")
            return JSONResponse(
                content={"message": response},
                status_code=200,
            )
        except Exception as e:
            return JSONResponse(
                content={"message": "Failed to generate a response.", "error": str(e)},
                status_code=500,
            )

    def response_to_user_from_llama_model(self):
        try:
            if self.model_type == "knowledge_graph":
                return self.response_to_user_from_knowledge_graph()
            elif self.model_type == "knowledge_graph_and_AI":
                return self.response_to_user_from_knowledge_graph_and_Llama()
            elif self.model_type == "AI":
                return self.response_to_user_from_Llama()
        except Exception:
            return JSONResponse(
                content={"message": "Invalid model type"}, status_code=400
            )
