import asyncio
import csv
import json
import logging

from config import eval_result_csv_path, eval_result_json_path, test_set_path
from eval.generation_eval import GenerationEvaluation
from eval.retriever_eval import RetrievalEvaluation
from llm_client import LLMClient
from retrieve.similarity_search import similarity_search

logger = logging.getLogger(__name__)

MAX_CONCURRENCY = 10  # OpenAI API 동시 요청 수 제한


async def evaluate_one(idx: int, test_case: dict, llm: LLMClient, semaphore: asyncio.Semaphore) -> dict:
    async with semaphore:
        question = test_case["question"]
        ground_truth = test_case["ground_truth"]
        rag_result = await similarity_search(question, llm)

        retrieval_eval = RetrievalEvaluation(question, rag_result["retrieved_docs"], ground_truth, llm)
        generation_eval = GenerationEvaluation(question, rag_result["generated_answer"], rag_result["retrieved_docs"], ground_truth, llm)

        # 4개 평가 지표 병렬 실행
        (
            precision,
            recall,
            faithfulness,
            factual_correctness,
        ) = await asyncio.gather(
            retrieval_eval.retrieved_docs_precision_evaluation(),
            retrieval_eval.retrieved_docs_recall_evaluation(),
            generation_eval.faithfulness_evaluation(),
            generation_eval.factual_correctness_evaluation(),
        )

        csv_row = {
            "idx": idx,
            "question": question,
            "ground_truth": ground_truth,
            "retrieved_docs": rag_result["retrieved_docs"],
            "generated_answer": rag_result["generated_answer"],
            "retrieval_precision": precision["score"],
            "retrieval_recall": recall["score"],
            "generation_faithfulness": faithfulness["score"],
            "generation_factual_correctness": factual_correctness["score"],
        }

        json_row = {
            **csv_row,
            "retrieval_precision_reason": precision.get("reason"),
            "retrieval_recall_reason": recall.get("reason"),
            "generation_faithfulness_reason": faithfulness.get("reason"),
            "generation_factual_correctness_reason": factual_correctness.get("reason"),
        }

        return csv_row, json_row


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    with open(test_set_path, "r") as f:
        test_cases = json.load(f)

    llm = LLMClient(provider="openai", model="gpt-4o-mini")
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    raw_results = await asyncio.gather(
        *[evaluate_one(idx, tc, llm, semaphore) for idx, tc in enumerate(test_cases)],
        return_exceptions=True,
    )

    csv_rows, json_rows = [], []
    for idx, result in enumerate(raw_results):
        if isinstance(result, Exception):
            logger.error(f"test case {idx} 평가 실패: {result}")
        else:
            csv_row, json_row = result
            csv_rows.append(csv_row)
            json_rows.append(json_row)

    # CSV: score만 저장
    fieldnames = [
        "idx",
        "question",
        "ground_truth",
        "retrieved_docs",
        "generated_answer",
        "retrieval_precision",
        "retrieval_recall",
        "generation_faithfulness",
        "generation_factual_correctness",
    ]
    with open(eval_result_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    # JSON: score + reason 전체 저장
    with open(eval_result_json_path, "w", encoding="utf-8") as f:
        json.dump(json_rows, f, ensure_ascii=False, indent=4)

    print(
        f"평가 완료: {len(csv_rows)}/{len(test_cases)}개 결과 저장\n"
        f"  - eval_results.csv (score만)\n"
        f"  - eval_results.json (score + reason)"
    )


if __name__ == "__main__":
    asyncio.run(main())
