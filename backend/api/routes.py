from fastapi import APIRouter
from pydantic import BaseModel

from graph.graph import app


router = APIRouter(
    prefix="/api",
    tags=["Research"],
)


class ResearchRequest(BaseModel):
    company_name: str


@router.post("/research")
def research_company(request: ResearchRequest):

    thread_id = f"{request.company_name.lower()}-research"

    result = app.invoke(
        {
            "company_name": request.company_name,
            "thread_id": thread_id,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Research {request.company_name} "
                        "as an investment opportunity."
                    ),
                }
            ],
        },
        config={
            "configurable": {
                "thread_id": thread_id
            }
        },
    )

    return {
        "company_name": request.company_name,
        "result": result,
    }