import json
import re
from pathlib import Path

from utils.llm_client import LLMClient
from utils.config import test_corpus_path
TOP_K = 3

_STOPWORDS = {"이", "가", "은", "는", "을", "를", "의", "에", "에서", "로", "으로", "와", "과", "도", "만", "어떻게", "어떤", "알려줘", "알려주세요", "어디", "뭐야", "뭔가요", "인가요", "하면", "되나요", "해야", "있어", "있나요"}


def _load_corpus() -> list[dict]:
    with open(test_corpus_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _extract_keywords(text: str) -> list[str]:
    """질문에서 의미 있는 키워드를 추출합니다."""
    tokens = re.findall(r"[가-힣a-zA-Z0-9]+", text)
    return [t for t in tokens if len(t) >= 2 and t not in _STOPWORDS]


def _regex_search(question: str, corpus: list[dict], top_k: int = TOP_K) -> list[str]:
    """키워드 기반 정규식 스코어링으로 관련 문서를 반환합니다."""
    keywords = _extract_keywords(question)
    if not keywords:
        return [doc["content"] for doc in corpus[:top_k]]

    scored = []
    for doc in corpus:
        content = doc["content"]
        score = sum(len(re.findall(kw, content)) for kw in keywords)
        scored.append((score, doc["content"]))

    scored.sort(key=lambda x: x[0], reverse=True)

    # score > 0인 문서만 반환, 없으면 상위 top_k 반환
    matched = [content for score, content in scored if score > 0]
    return matched[:top_k] if matched else [content for _, content in scored[:top_k]]


async def _generate_answer(question: str, retrieved_docs: list[str], llm: LLMClient) -> str:
    docs_text = "\n".join(f"- {doc}" for doc in retrieved_docs)
    prompt = f"""다음 문서들을 참고하여 질문에 간결하게 답하세요. 문서에 없는 내용은 답하지 마세요.

문서:
{docs_text}

질문: {question}

답변:"""
    return await llm.invoke(prompt)


async def similarity_search(question: str, llm: LLMClient = None) -> dict:
    corpus = _load_corpus()
    retrieved_docs = _regex_search(question, corpus)

    _llm = llm or LLMClient(provider="openai", model="gpt-4o-mini")
    generated_answer = await _generate_answer(question, retrieved_docs, _llm)

    return {
        "question": question,
        "retrieved_docs": retrieved_docs,
        "generated_answer": generated_answer,
    }
