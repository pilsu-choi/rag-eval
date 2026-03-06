import asyncio
import csv
import json
import logging
import os

from utils.config import (
    eval_rag_pipeline_result_csv_path,
    eval_rag_pipeline_result_json_path,
    test_rag_pipeline_set_path,
)
from eval.generation_eval import GenerationEvaluation
from eval.retriever_eval import RetrievalEvaluation
from schema.eval_result import EvalResult
from utils.llm_client import LLMClient
from retrieve.similarity_search import similarity_search

logger = logging.getLogger(__name__)

MAX_CONCURRENCY = 10  # OpenAI API 동시 요청 수 제한


async def evaluate_one(
    idx: int | str, test_case: dict, llm: LLMClient, semaphore: asyncio.Semaphore
) -> EvalResult:
    async with semaphore:
        question = test_case["question"]
        ground_truth = test_case["ground_truth"]
        rag_result = await similarity_search(question, llm)

        retrieval_eval = RetrievalEvaluation(
            question, rag_result["retrieved_docs"], ground_truth, llm
        )
        generation_eval = GenerationEvaluation(
            question,
            rag_result["generated_answer"],
            rag_result["retrieved_docs"],
            ground_truth,
            llm,
        )

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

        return EvalResult(
            idx=idx,
            question=question,
            ground_truth=ground_truth,
            retrieved_docs=rag_result["retrieved_docs"],
            generated_answer=rag_result["generated_answer"],
            retrieval_precision=precision["score"],
            retrieval_recall=recall["score"],
            generation_faithfulness=faithfulness["score"],
            generation_factual_correctness=factual_correctness["score"],
            retrieval_precision_reason=precision.get("reason"),
            retrieval_recall_reason=recall.get("reason"),
            generation_faithfulness_reason=faithfulness.get("reason"),
            generation_factual_correctness_reason=factual_correctness.get("reason"),
        )


async def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    json_files = sorted(
        f for f in os.listdir(test_rag_pipeline_set_path) if f.endswith(".json")
    )
    if not json_files:
        logger.error(
            f"testsets 디렉토리에 JSON 파일이 없습니다: {test_rag_pipeline_set_path}"
        )
        return

    llm = LLMClient(provider="openai", model="gpt-4o-mini")
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    all_results: list[EvalResult] = []
    total_cases = 0

    for json_file in json_files:
        file_path = os.path.join(test_rag_pipeline_set_path, json_file)
        file_stem = os.path.splitext(json_file)[0]

        with open(file_path, "r") as f:
            test_cases = json.load(f)

        total_cases += len(test_cases)
        logger.info(f"[{json_file}] 평가 시작: {len(test_cases)}개 test case")

        raw_results = await asyncio.gather(
            *[
                evaluate_one(f"{file_stem}-{idx}", tc, llm, semaphore)
                for idx, tc in enumerate(test_cases)
            ],
            return_exceptions=True,
        )

        for idx, result in enumerate(raw_results):
            if isinstance(result, Exception):
                logger.error(f"[{json_file}] test case {idx} 평가 실패: {result}")
            else:
                all_results.append(result)

    results = all_results

    # CSV: score만 저장
    csv_dicts = [r.to_csv_dict() for r in results]
    fieldnames = list(csv_dicts[0].keys()) if csv_dicts else []

    # eval_result 디렉토리 없으면 생성
    for path in (eval_rag_pipeline_result_csv_path, eval_rag_pipeline_result_json_path):
        dir_ = os.path.dirname(path)
        if dir_ and not os.path.exists(dir_):
            os.makedirs(dir_)

    with open(
        eval_rag_pipeline_result_csv_path, "w", newline="", encoding="utf-8-sig"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_dicts)
        writer.writerow(EvalResult.average_row(results))

    # JSON: score + reason 전체 저장
    with open(eval_rag_pipeline_result_json_path, "w", encoding="utf-8") as f:
        json.dump(
            [r.to_json_dict() for r in results] + [EvalResult.average_row(results)],
            f,
            ensure_ascii=False,
            indent=4,
        )

    print(
        f"평가 완료: {len(results)}/{total_cases}개 결과 저장 ({len(json_files)}개 파일)\n"
        f"  - {eval_rag_pipeline_result_csv_path} (score만)\n"
        f"  - {eval_rag_pipeline_result_json_path} (score + reason)"
    )


if __name__ == "__main__":
    asyncio.run(main())
