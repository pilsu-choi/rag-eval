# RAG Eval

RAG 파이프라인 및 Full Text Search(키워드 검색)의 검색·생성 품질을 자동으로 평가하는 프레임워크입니다.

---

## 프로젝트 구조

```
rag-eval/
├── genarate_testsets/          # 테스트셋 생성
│   ├── fts_testsets_generator.py   # Full Text Search 테스트셋 생성
│   ├── rag_testsets_generator.py   # RAG 파이프라인 테스트셋 생성
│   └── files/
│       ├── fts/                # FTS 원본 문서 및 생성된 testsets/
│       └── rag/                # RAG 원본 문서 및 생성된 testsets/
├── retrieve/                   # 검색 서버 API 연동
│   ├── full_text_search.py     # 키워드 검색 API 요청
│   └── similarity_search.py    # 유사도 검색 + 답변 생성
├── eval/                       # 평가 로직
│   ├── retriever_eval.py       # Retrieval 평가 (Precision, Recall)
│   ├── generation_eval.py      # Generation 평가 (Faithfulness, Factual Correctness)
│   └── results/                # 평가 결과 저장 경로
│       ├── eval_full_text_search_results.csv
│       ├── eval_full_text_search_results.json
│       ├── eval_rag_pipeline_results.csv
│       └── eval_rag_pipeline_results.json
├── schema/
│   ├── eval_result.py          # 평가 결과 데이터 클래스
│   └── keyword_search_response.py  # 검색 API 요청/응답 스키마
├── utils/
│   ├── config.py               # 경로 및 서버 URL 설정
│   ├── llm_client.py           # LLM 호출 클라이언트
│   └── prompts.py              # 평가용 LLM 프롬프트
├── full_text_search_judge.py   # FTS 평가 실행 엔트리포인트
└── rag_pipeline_judge.py       # RAG 파이프라인 평가 실행 엔트리포인트
```

---

## 평가 흐름

### 1단계: 테스트셋 생성

평가에 사용할 `question` / `ground_truth` 데이터셋을 LLM 에이전트(`deepagents`)로 자동 생성합니다.

- **FTS용**: `genarate_testsets/files/fts/`에 원본 JSON 파일 배치 후 실행
  ```bash
  python genarate_testsets/fts_testsets_generator.py
  ```
  → `genarate_testsets/files/fts/testsets/`에 testset 저장

- **RAG용**: `genarate_testsets/files/rag/`에 원본 JSON 파일 배치 후 실행
  ```bash
  python genarate_testsets/rag_testsets_generator.py
  ```
  → `genarate_testsets/files/rag/testsets/`에 testset 저장

testset 포맷:
```json
[
  {
    "question": "6조 규정 내용 알려줘",
    "ground_truth": ["6조 규정 내용 1", "6조 규정 내용 2"],
    "file_name": "원본파일명.json"
  }
]
```

### 2단계: 평가 실행

```bash
# Full Text Search 평가 (Retrieval 지표만)
python full_text_search_judge.py

# RAG 파이프라인 평가 (Retrieval + Generation 지표)
python rag_pipeline_judge.py
```

---

## 평가 지표

| 구분 | 지표 | 설명 |
|------|------|------|
| Retrieval | **Precision** | 검색된 문서 중 유효한 문서 비율 (유효 검색 문서 / 전체 검색 문서) |
| Retrieval | **Recall** | 정답 문서 중 검색된 문서 비율 (유효 검색 문서 / 정답 문서) |
| Generation | **Faithfulness** | 생성 답변이 검색 context에 근거하는지 여부 (hallucination 탐지) |
| Generation | **Factual Correctness** | 생성 답변이 ground truth와 일치하는지 여부 |

> Precision 낮음 → retriever 문제 / Recall 낮음 → embedding·chunk 문제

---

## 평가 결과

결과 파일은 `eval/results/`에 저장됩니다.

| 파일 | 내용 |
|------|------|
| `eval_full_text_search_results.csv` | FTS 평가 점수 (score만) |
| `eval_full_text_search_results.json` | FTS 평가 점수 + LLM 판단 근거 |
| `eval_rag_pipeline_results.csv` | RAG 평가 점수 (score만) |
| `eval_rag_pipeline_results.json` | RAG 평가 점수 + LLM 판단 근거 |

각 파일의 마지막 행에 전체 평균(average)이 포함됩니다.

---

## 설정

`utils/config.py`에서 경로와 서버 URL을 설정합니다.

```python
SERVER_URL = "http://localhost:8003/api/search"
```

검색 서버 API의 request/response 파라미터가 변경되면 아래 파일을 수정하세요.
- `retrieve/full_text_search.py`
- `retrieve/similarity_search.py`

---

## 환경 설정

```bash
# 의존성 설치 (uv 사용)
uv sync

# 또는 pip
pip install -e .
```

`.env` 파일에 OpenAI API 키를 설정하세요.
```
OPENAI_API_KEY=sk-...
```

---

## Remaining

- RAG 검색 서버 연동 및 평가 (`retrieve/similarity_search.py`의 `rag_request` 연결)
