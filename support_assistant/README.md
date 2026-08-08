# Zepto Support Assistant

## 1. About the project

This project is a small support assistant for Zepto. It uses the given Zepto policy documents to answer questions related to delivery, returns, membership, tracking, cancellation, gift cards and support.

The project uses ChromaDB for storing embeddings and LangGraph for deciding whether a question needs document retrieval or not.

The application is also connected to a FastAPI endpoint so that we can send questions using `/ask`.

The default mode is `MOCK_LLM=1`, so no API key or external LLM is required.

---

## 2. Documents and Embeddings

I used the 8 documents provided in the assignment.

They are stored inside:

`support_assistant/docs/`

The files are:

- doc_01.txt
- doc_02.txt
- doc_03.txt
- doc_04.txt
- doc_05.txt
- doc_06.txt
- doc_07.txt
- doc_08.txt

The documents are loaded and processed in `ingest.py`.

For creating embeddings I used:

`all-MiniLM-L6-v2`

The embeddings are stored locally using ChromaDB.

The ChromaDB data is stored inside:

`support_assistant/chroma_db/`

---

## 3. Prompt

The prompt is written in `prompts.py`.

It follows the required role, context, task, format and length structure.

I also added a negative instruction so that the assistant should not use information which is not present in the retrieved context.

A small few-shot example is also included in the prompt.

---

## 4. LangGraph

The graph is implemented in `graph.py`.

There are three main nodes:

- `classify_intent`
- `retrieve_and_answer`
- `direct_answer`

The flow is:

START
  |
  v
classify_intent
  |
  |-- policy_question --> retrieve_and_answer
  |
  |-- general_question --> direct_answer
                              |
                              v
                             END

The `classify_intent` node uses a keyword-based method when `MOCK_LLM=1`.

The policy keywords used are:

- delivery
- return
- refund
- membership
- tracking
- cancel
- gift card
- support hours

If the question contains one of these keywords, it is treated as a `policy_question`.

Otherwise it is treated as a `general_question`.

---

## 5. Retrieval

When the question is a policy question, the `retrieve_and_answer` node creates an embedding for the question and searches the ChromaDB collection.

The top 3 similar chunks are retrieved.

The document IDs of the retrieved chunks are returned in the `sources` field.

For example, for the delivery policy question, the retrieved sources were:

`doc_01`, `doc_05`, `doc_04`

---

## 6. Mock LLM

The assignment requires the default graded version to work without an actual LLM.

For this I used:

`MOCK_LLM=1`

In this mode there is:

- no LLM API key
- no LLM provider network call
- keyword-based intent classification
- real ChromaDB retrieval for policy questions
- deterministic answer generation

The optional real LLM mode can be enabled using:

`MOCK_LLM=0`

but I have used the required mock mode for the graded baseline.

---

## 7. Pydantic Output

The request and response models are written in `models.py`.

The response contains three fields:

- `answer`
- `sources`
- `confidence`

Example:

{
  "answer": "string",
  "sources": [],
  "confidence": 1.0
}

The confidence value is a float between 0 and 1.

The FastAPI response is validated using this Pydantic model.

---

## 8. FastAPI and Testing

The FastAPI application is written in `main.py`.

The endpoint is:

`POST /ask`

The request format is:

{
  "query": "What is Zepto's delivery policy?"
}

I tested the application using the Swagger page:

`http://127.0.0.1:8000/docs`

### Test 1 - Policy Question

Request:

{
  "query": "What is Zepto's delivery policy?"
}

Response:

{
  "answer": "Based on the retrieved context: Delivery Policy: \"Zepto delivers grocery and household essentials to serviceable pin codes within 10 to 30 minutes of order confirmation, depending on the customer's delivery zone and current order volume\"",
  "sources": [
    "doc_01",
    "doc_05",
    "doc_04"
  ],
  "confidence": 1
}

This question was treated as a policy question and retrieval was performed.

### Test 2 - General Question

Request:

{
  "query": "What is the capital of India?"
}

Response:

{
  "answer": "I can only answer questions about Zepto policies right now.",
  "sources": [],
  "confidence": 1
}

This question was treated as a general question, so retrieval was not performed.

Both requests returned HTTP 200 successfully.

---

## 9. Docker

I created a Dockerfile inside the `support_assistant` folder.

The image can be built from the main project folder using:

docker build -f support_assistant/Dockerfile -t zepto-support .

To run the container:

docker run --rm -p 7860:7860 zepto-support

After starting the container, the API can be opened at:

`http://127.0.0.1:7860/docs`

The container uses port `7860`.

I also tested the Docker container and the FastAPI application started successfully inside the container.

---

## 10. Project Structure

The main project structure is:

capstone project/
|
|-- support_assistant/
|   |
|   |-- docs/
|   |   |-- doc_01.txt
|   |   |-- doc_02.txt
|   |   |-- doc_03.txt
|   |   |-- doc_04.txt
|   |   |-- doc_05.txt
|   |   |-- doc_06.txt
|   |   |-- doc_07.txt
|   |   `-- doc_08.txt
|   |
|   |-- chroma_db/
|   |-- __init__.py
|   |-- ingest.py
|   |-- prompts.py
|   |-- models.py
|   |-- graph.py
|   |-- main.py
|   |-- requirements.txt
|   |-- Dockerfile
|   `-- README.md
|
|-- analytics/
|-- data_pipeline/
`-- ...

### File usage

`ingest.py`  
Used for loading the documents, creating embeddings and storing them in ChromaDB.

`prompts.py`  
Contains the structured prompt used for answering policy questions.

`models.py`  
Contains the Pydantic request and response models.

`graph.py`  
Contains the LangGraph nodes, routing and retrieval logic.

`main.py`  
Runs the FastAPI application and provides the `/ask` endpoint.

`Dockerfile`  
Used to build and run the application inside Docker.

`README.md`  
Contains the project explanation, testing results and commands.

---

## Running the project

Install the required packages using:

pip install -r support_assistant/requirements.txt

Run the application locally using:

python -m uvicorn support_assistant.main:app --reload

Then open:

http://127.0.0.1:8000/docs

For Docker:

docker build -f support_assistant/Dockerfile -t zepto-support .

docker run --rm -p 7860:7860 zepto-support

Then open:

http://127.0.0.1:7860/docs

---

## Final Note

The project is using the required `MOCK_LLM=1` mode for the graded baseline.

The documents are embedded locally, stored in ChromaDB, retrieved using similarity search, routed using LangGraph and served through FastAPI.

The Docker image was also built and tested successfully.