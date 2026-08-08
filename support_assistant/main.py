from fastapi import FastAPI

from support_assistant.models import SupportRequest, SupportResponse
from support_assistant.graph import graph


app = FastAPI(
    title="Zepto Support Assistant"
)


@app.post(
    "/ask",
    response_model=SupportResponse
)
def ask(request: SupportRequest):

    result = graph.invoke({
        "query": request.query
    })

    return SupportResponse(
        answer=result["answer"],
        sources=result["sources"],
        confidence=result["confidence"]
    )