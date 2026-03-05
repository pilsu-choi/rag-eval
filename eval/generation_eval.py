from llm_client import LLMClient
from prompts import faithfulness_prompt, factual_correctness_prompt


class GenerationEvaluation:

    def __init__(self, question, answer, retrieved_docs, ground_truth, llm: LLMClient = None):
        self.question = question
        self.answer = answer
        self.retrieved_docs = retrieved_docs
        self.ground_truth = ground_truth
        self.llm = llm or LLMClient(provider="openai", model="gpt-4o-mini")

    async def faithfulness_evaluation(self) -> dict:
        """
        Faithfulness 평가

        생성된 답변이 retrieval context에 기반해서 생성되었는지 평가
        → context에 없는 내용을 생성하면 hallucination

        예시
        context:
        - 파리는 프랑스의 수도이다

        answer:
        - 파리는 프랑스의 수도이며 인구는 200만 명이다

        claim 2개 중
        - 수도 정보 → context 존재
        - 인구 정보 → context 없음

        faithfulness = context 기반 claim / 전체 claim
                     = 1 / 2 = 0.5
        """
        prompt = faithfulness_prompt.format(
            question=self.question,
            answer=self.answer,
            retrieved_docs=self.retrieved_docs,
        )
        raw = await self.llm.invoke(prompt)
        return LLMClient.parse_json(raw)

    async def factual_correctness_evaluation(self) -> dict:
        """
        Factual Correctness 평가

        생성된 답변이 실제 정답(ground truth)과 일치하는지 평가

        예시
        ground truth:
        - 파리는 프랑스의 수도이다

        answer:
        - 파리는 프랑스의 수도이다

        factual correctness = 정답과 일치하는 claim / 전체 claim
                            = 1 / 1 = 1.0
        """
        prompt = factual_correctness_prompt.format(
            question=self.question,
            answer=self.answer,
            ground_truth=self.ground_truth,
        )
        raw = await self.llm.invoke(prompt)
        return LLMClient.parse_json(raw)
