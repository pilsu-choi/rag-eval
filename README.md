{
"query": "6조 규정 내용 알려줘",
"ground_truth": ["6조 규정 내용 1", "6조 규정 내용 2", "6조 규정 내용 3"],
}

'''

1. testset generation - 질문, 정답 데이터셋 생성
2. RAG - 질문에 대한 응답과 검색 문서 추출

총 4개 지표 평가. Retrieval 2개, Generation 2개

Retrieval 평가 3. precision(유효 검색 문서/전체 검색 문서), recall(유효 검색 문서/정답 문서) 계산 - ex) 정답 문서 3개, 검색 문서 10개, 유효 검색 문서 2개 -> precision: 2/10, recall: 2/3

Generation 평가
Faithfulness FactualCorrectness
기준 retrieved context ground truth answer
목적 hallucination 탐지 실제 정답 여부
'''

'''

1. 밀버스 적재
2. 테스트 데이터셋 순회하며 query 실행
3. 질문 응답과 검색 문서 추출
4. prompt 조합

'''
