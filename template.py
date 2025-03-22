import os
from pathlib import Path

# Define the project name
Project_Name = "Developed_Custom_RAG_Model"

# Define the list of files to be created in the project
list_of_files = [
    "config/__init__.py",
    "config/mongo_db.py",
    "models/__init__.py",
    "models/read_upload_file.py",
    "models/scrapping.py",
    "models/web_scrapping.py",
    "models/webpage_scrapping.py",
    "models/openai_model.py",
    "models/gemini_model.py",
    "models/llama_model.py",
    "routes/__init__.py",
    "routes/routes.py",
    "index.py",
    "requirements.txt",
    "README.md",
    ".gitignore",
    ".env",
    "setup.py",
]

# Create the directories of the folder and write the files if they do not exist
for file in list_of_files:
    file_path = Path(file)
    if not file_path.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file, "w") as f:
            f.write("# Path: " + file)
print("Project structure created successfully!")
