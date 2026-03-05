precision_prompt = """
You are an evaluator.

Given a question, retrieved_docs, and ground_truth, evaluate the precision of the retrieved_docs.

Precision = (number of retrieved docs relevant to the ground truth) / (total number of retrieved docs)

question:
{question}

retrieved_docs:
{retrieved_docs}

ground_truth:
{ground_truth}

Return JSON only. Do not include any other text.
한글로 설명해줘.

{{
    "metric": "precision",
    "score": <a float between 0 and 1>,
    "reason": "explain briefly"
}}
"""

recall_prompt = """
You are an evaluator.

Given a question, retrieved_docs, and ground_truth, evaluate the recall of the retrieved_docs.

Recall = (number of ground truth items covered by retrieved docs) / (total number of ground truth items)

question:
{question}

retrieved_docs:
{retrieved_docs}

ground_truth:
{ground_truth}

Return JSON only. Do not include any other text.
한글로 설명해줘.

{{
    "metric": "recall",
    "score": <a float between 0 and 1>,
    "reason": "explain briefly"
}}
"""


faithfulness_prompt = """
You are an evaluator.

Given a question, answer, and retrieved_docs, evaluate whether the answer is faithful to the retrieved_docs.

Faithfulness = (number of claims in the answer that are supported by retrieved_docs) / (total number of claims in the answer)

question:
{question}

answer:
{answer}

retrieved_docs:
{retrieved_docs}

Return JSON only. Do not include any other text.
한글로 설명해줘.

{{
    "metric": "faithfulness",
    "score": <a float between 0 and 1>,
    "reason": "explain briefly"
}}
"""

factual_correctness_prompt = """
You are an evaluator.

Given a question, an answer, and a ground_truth, evaluate whether the answer is factually correct compared to the ground_truth.

Factual Correctness = (number of claims in the answer that match the ground_truth) / (total number of claims in the answer)

question:
{question}

answer:
{answer}

ground_truth:
{ground_truth}

Return JSON only. Do not include any other text.
한글로 설명해줘.

{{
    "metric": "factual_correctness",
    "score": <a float between 0 and 1>,
    "reason": "explain briefly"
}}
"""
