# AI-ML Capstone Project

This repository contains my AI-ML capstone project. The project is divided into three main modules: Analytics, Data Pipeline, and Support Assistant.

The main purpose of the project is to work with data, build a machine learning pipeline, and finally build a small GenAI based application using retrieval and an API.

## Project Structure

```text
AI-ML-capstone-project/
│
├── analytics/
│   ├── plots/
│   ├── 01_eda.ipynb
│   ├── 02_modeling.ipynb
│   └── README.md
│
├── data_pipeline/
│   └── README.md
│
├── support_assistant/
│   ├── docs/
│   │   ├── doc_01.txt
│   │   ├── doc_02.txt
│   │   ├── doc_03.txt
│   │   ├── doc_04.txt
│   │   ├── doc_05.txt
│   │   ├── doc_06.txt
│   │   ├── doc_07.txt
│   │   └── doc_08.txt
│   │
│   ├── chroma_db/
│   ├── graph.py
│   ├── ingest.py
│   ├── main.py
│   ├── models.py
│   ├── prompts.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md
│
├── .gitignore
├── books.db
└── README.md

## Module 1 - Analytics

The Analytics module contains exploratory data analysis and machine learning work.

The EDA notebook is used to understand the dataset, check the data, perform analysis and create visualizations.

The modeling notebook is used for preparing the data for machine learning, training models and checking their performance.

The generated plots and analysis results are also kept inside the analytics module.

## Module 2 - Data Pipeline

The Data Pipeline module is used to handle the data processing part of the project.

It focuses on taking the input data, processing it and preparing it for further analysis or machine learning tasks.

The pipeline helps keep the data preparation steps organized instead of doing everything manually.

## Module 3 - Support Assistant

The Support Assistant is a small RAG-based GenAI application created for Zepto support questions.

It uses the given Zepto policy documents as its knowledge base.

The documents cover topics such as:

1.Delivery policy
2.Returns and refunds
3.Membership
4.Order tracking
5.Order cancellation
6.Damaged or missing items
7.Gift cards
8.Customer support hours

## How the Support Assistant works
# The basic flow of the application is:

Zepto Documents
      |
      v
Document Ingestion
      |
      v
Embeddings using all-MiniLM-L6-v2
      |
      v
ChromaDB
      |
      v
User Question
      |
      v
LangGraph
      |
      +----------------------+
      |                      |
      v                      v
Policy Question        General Question
      |                      |
      v                      v
Retrieve relevant       Direct Answer
chunks from ChromaDB
      |
      v
Generate Answer
      |
      v
Pydantic JSON Response
      |
      v
FastAPI /ask
Document Ingestion

The eight provided Zepto documents are stored inside the support_assistant/docs folder.

The ingest.py file loads the documents, creates embeddings using the all-MiniLM-L6-v2 model and stores the vectors in a ChromaDB collection.

This allows the application to search for information related to a user's question.

LangGraph

The application uses LangGraph to control the flow.

There are three main nodes:

1.classify_intent
2.retrieve_and_answer
3.direct_answer

The classify_intent node decides whether the question is related to a Zepto policy.

For policy questions, the application retrieves relevant chunks from ChromaDB.

For general questions, it gives a fixed response without retrieving documents.

The default graded mode uses the deterministic mock LLM path, so the application can run without an API key or network access.

## Structured Response

The final response is validated using a Pydantic model.

The response contains:

{
  "answer": "...",
  "sources": [],
  "confidence": 1.0
}

For policy questions, the sources field contains the document IDs used for the answer.

For general questions, the sources list is empty.

FastAPI

The Support Assistant is exposed through a FastAPI application.

The main endpoint is:

POST /ask

Example request:

{
  "query": "What is Zepto's delivery policy?"
}

The API returns a structured JSON response containing the answer, sources and confidence.

The application can also be tested using the automatically generated Swagger UI at:

http://127.0.0.1:8000/docs
Docker

A Dockerfile is included inside the support_assistant module.

The Dockerfile installs the required dependencies, copies the application into the container and starts the FastAPI application using Uvicorn.

The application is configured to run on:
0.0.0.0:7860

01.Technologies Used
02.Python
03.Pandas
04.NumPy
05.Scikit-learn
06.Sentence Transformers
07.all-MiniLM-L6-v2
08.ChromaDB
09.LangGraph
10.Pydantic
11.FastAPI
12.Uvicorn
13.Docker
14.Git and GitHub
15.Jupyter Notebook

## Running the Support Assistant

Go to the project directory and install the required packages.

pip install -r support_assistant/requirements.txt

Run the FastAPI application:

uvicorn support_assistant.main:app --reload

Then open:

http://127.0.0.1:8000/docs

Use the /ask endpoint to test the assistant.

Example:

{
  "query": "What is Zepto's delivery policy?"
}

A general question can also be tested:

{
  "query": "What is the capital of India?"
}

The first question should trigger retrieval, while the second question should be treated as a general question.

## GitHub

The complete capstone project is maintained in this GitHub repository:

https://github.com/SampathSriVasthav-web/AI-ML-capstone-project

## Conclusion

This project combines data analysis, data processing, machine learning and a RAG-based GenAI application in one capstone repository.

The Support Assistant demonstrates how documents can be converted into embeddings, stored in a vector database, retrieved based on a user's question and returned through a structured FastAPI service.


### Then do this

Since you're already at the root of the project in VS Code:

**1. Open the root `README.md`** — the one outside `analytics`, `data_pipeline`, and `support_assistant`.

**2. `Ctrl + A` → delete old content.**

**3. Paste the above content.**

**4. Save:**

```text
Ctrl + S