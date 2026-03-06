import requests
from schema.keyword_search_response import KeywordSearchRequest, TotalSearchResponse
from utils.config import SERVER_URL


# example 구현
async def full_text_search(question):
    retrieved_docs = ["doc1", "doc2", "doc3"]
    return {
        "question": question,
        "retrieved_docs": retrieved_docs,
    }


async def keyword_search_request(question: str) -> dict:
    KEYWORD_SEARCH_END_POINT = f"{SERVER_URL}/total"
    body = KeywordSearchRequest(
        query=question,
        search_type="SEARCH",
        page=1,
        page_size=10,
        result_type=None,
    ).model_dump()
    response = requests.post(KEYWORD_SEARCH_END_POINT, json=body)
    response.raise_for_status()
    response_json = TotalSearchResponse.model_validate(response.json())
    retrieved_docs = response_json.results.model_dump()
    return {
        "question": question,
        "retrieved_docs": retrieved_docs,
    }
