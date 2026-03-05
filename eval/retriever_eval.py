from utils.llm_client import LLMClient
from utils.prompts import precision_prompt, recall_prompt


class RetrievalEvaluation:

    def __init__(self, question, retrieved_docs, ground_truth, llm: LLMClient = None):
        self.question = question
        self.retrieved_docs = retrieved_docs
        self.ground_truth = ground_truth
        self.llm = llm or LLMClient(provider="openai", model="gpt-4o-mini")

    async def retrieved_docs_precision_evaluation(self) -> dict:
        # precision 낮음 → retriever 문제
        # precision(유효 검색 문서 / 전체 검색 문서)
        prompt = precision_prompt.format(
            question=self.question,
            retrieved_docs=self.retrieved_docs,
            ground_truth=self.ground_truth,
        )
        raw = await self.llm.invoke(prompt)
        return LLMClient.parse_json(raw)

    async def retrieved_docs_recall_evaluation(self) -> dict:
        # recall 낮음 → embedding / chunk 문제
        # recall(유효 검색 문서 / 정답 문서)
        prompt = recall_prompt.format(
            question=self.question,
            retrieved_docs=self.retrieved_docs,
            ground_truth=self.ground_truth,
        )
        raw = await self.llm.invoke(prompt)
        return LLMClient.parse_json(raw)
