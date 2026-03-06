"""
Request / Response 스키마 모델
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ============================================================
# Request 스키마
# ============================================================
class KeywordSearchRequest(BaseModel):
    """키워드 검색 요청"""

    query: str = Field(..., description="검색어")
    search_type: str = Field(..., description="검색 유형 (일반검색=SEARCH/AI검색=AI)")
    page: int = Field(..., ge=1, description="조회할 페이지 번호 (1부터 시작)")
    page_size: int = Field(
        ..., ge=1, le=100, description="페이지당 결과 수 (키워드 검색 시 사용)"
    )
    result_type: Optional[str] = Field(
        None,
        description="상세검색 대상(hr/board/krule). /api/search/keyword에서 사용, "
        "전체검색(/api/search/total)에서는 미사용",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "전명훈",
                "search_type": "SEARCH",
                "page": 1,
                "page_size": 10,
                "result_type": "hr",
            }
        }


# ============================================================
# Response 스키마
# ============================================================
class EmployeeResult(BaseModel):
    """직원 검색 결과 항목"""

    emp_nm: Optional[str] = Field(None, description="직원 성명")
    emp_no: Optional[str] = Field(None, description="사번")
    dept_nm: Optional[str] = Field(None, description="부서명")
    chag_duty: Optional[str] = Field(None, description="업무 내용")
    telno_offc: Optional[str] = Field(None, description="구내 전화번호")
    celpon_no: Optional[str] = Field(None, description="휴대 전화번호")
    email_id: Optional[str] = Field(None, description="이메일 주소")
    img_link: Optional[str] = Field(None, description="직원 이미지 URL")

    class Config:
        json_schema_extra = {
            "example": {
                "emp_nm": "전명훈",
                "emp_no": "A1023",
                "dept_nm": "연구기획팀",
                "chag_duty": "AI 기반 검색 시스템 설계 및 운영",
                "telno_offc": "042-123-4567",
                "celpon_no": "010-9876-5432",
                "email_id": "jiyu.seo@example.com",
                "img_link": "/images/employees/A1023.jpg",
            }
        }


class BoardResult(BaseModel):
    """게시판 검색 결과 항목"""

    brd_name: Optional[str] = Field(None, description="게시판명")
    title: Optional[str] = Field(None, description="제목")
    content: Optional[str] = Field(None, description="본문")
    body_path: Optional[str] = Field(None, description="본문 경로")
    poster_name: Optional[str] = Field(None, description="게시자명")
    post_date: Optional[str] = Field(None, description="최초생성일")
    modify_date: Optional[str] = Field(None, description="최초수정일")

    class Config:
        json_schema_extra = {
            "example": {
                "brd_name": "공지사항",
                "title": "검색 시스템 정기 점검 안내",
                "content": "검색 시스템 정기 점검으로 인하여 22:00~24:00 동안 서비스가 중단됩니다.",
                "body_path": "/board/notice/2025/000123",
                "poster_name": "정보전산팀",
                "post_date": "2025-02-01",
                "modify_date": "2025-02-02",
            }
        }


class KruleResult(BaseModel):
    """규정집 검색 결과 항목"""

    title: Optional[str] = Field(None, description="문서명")
    state_name: Optional[str] = Field(None, description="현행 여부")
    text: Optional[str] = Field(None, description="원문")
    revcd: Optional[str] = Field(None, description="개정구분")
    revcha: Optional[str] = Field(None, description="개정차수")
    promul_dt: Optional[str] = Field(None, description="공포일")
    start_dt: Optional[str] = Field(None, description="시행일")
    upload_dt: Optional[str] = Field(None, description="등록일")
    download_file_url: Optional[str] = Field(None, description="규정 URL")
    bbscd: Optional[str] = Field(None, description="게시판 종류")
    writer: Optional[str] = Field(None, description="작성자")
    dept_name: Optional[str] = Field(None, description="부서명")
    page_range: Optional[str] = Field(None, description="페이지범위")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "정보보안 규정",
                "state_name": "현행",
                "text": "이 규정은 정보보안 관리에 관한 기본 원칙과 절차를 정함을 목적으로 한다.",
                "revcd": "개정",
                "revcha": "3",
                "promul_dt": "2024-01-01",
                "start_dt": "2024-02-01",
                "upload_dt": "2024-02-10",
                "download_file_url": "https://rules.example.com/SEC-001.pdf",
                "bbscd": "SEC",
                "writer": "규정관리팀",
                "dept_name": "경영기획실",
                "page_range": "1-10",
            }
        }


class PagingInfo(BaseModel):
    """페이징 정보"""

    page: int = Field(..., description="현재 페이지")
    page_size: int = Field(..., description="페이지당 결과 수")
    total_count: Optional[int] = Field(None, description="검색 결과 전체 건수")
    total_pages: Optional[int] = Field(None, description="전체 페이지 수")
    has_next: Optional[bool] = Field(None, description="다음 페이지 존재 여부")


class KeywordSearchResponse(BaseModel):
    """키워드 검색 응답"""

    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="결과 메시지")
    query: str = Field(..., description="검색 키워드")
    query_timestamp: int = Field(..., description="검색 요청 시간 (epoch ms)")
    search_type: str = Field(..., description="검색 유형 (일반검색=SEARCH/AI검색=AI)")
    result_vars: List[str] = Field(..., description="결과 변수 목록")
    result_names: List[str] = Field(..., description="결과 이름 목록")
    result_timestamp: int = Field(..., description="검색 결과 생성 시각 (epoch ms)")
    paging: PagingInfo = Field(..., description="페이징 정보")
    results: List[Dict[str, Any]] = Field(
        ..., description="선택된 검색 대상(result_type)의 결과 목록"
    )
    nouns: Optional[str] = Field(None, description="추출된 명사")
    filter_expr: Optional[str] = Field(None, description="필터 조건문")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "SUCCESS",
                "query": "검색 시스템",
                "query_timestamp": 1770101252580,
                "search_type": "SEARCH",
                "result_vars": ["board"],
                "result_names": ["게시판"],
                "result_timestamp": 1770101256414,
                "paging": {
                    "page": 1,
                    "page_size": 10,
                    "total_count": 5,
                    "total_pages": 1,
                    "has_next": False,
                },
                "results": [
                    {
                        "brd_name": "공지사항",
                        "title": "검색 시스템 정기 점검 안내",
                        "content": "검색 시스템 정기 점검으로 인하여 22:00~24:00 동안 서비스가 중단됩니다.",
                        "body_path": "/board/notice/2025/000123",
                        "poster_name": "정보전산팀",
                        "post_date": "2025-02-01",
                        "modify_date": "2025-02-02",
                    }
                ],
            }
        }


class TotalSearchResults(BaseModel):
    """전체검색 결과 컨테이너"""

    hr: List[EmployeeResult] = Field(
        default_factory=list, description="직원검색 결과 목록(top-3)"
    )
    board: List[BoardResult] = Field(
        default_factory=list, description="게시판 검색 결과 목록(top-3)"
    )
    krule: List[KruleResult] = Field(
        default_factory=list, description="규정집 검색 결과 목록(top-3)"
    )


class TotalSearchResponse(BaseModel):
    """전체검색 응답 (top-3, 페이징 없음)"""

    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="결과 메시지")
    query: str = Field(..., description="검색 키워드")
    query_timestamp: int = Field(..., description="검색 요청 시간 (epoch ms)")
    search_type: str = Field(..., description="검색 유형 (일반검색=SEARCH/AI검색=AI)")
    result_vars: List[str] = Field(..., description="결과 변수 목록")
    result_names: List[str] = Field(..., description="결과 이름 목록")
    result_counts: List[int] = Field(
        ..., description="검색대상별 검색 결과 수 (result_vars와 동일한 순서)"
    )
    result_timestamp: int = Field(..., description="검색 결과 생성 시각 (epoch ms)")
    results: TotalSearchResults = Field(..., description="검색 결과 목록")
    nouns: Optional[str] = Field(None, description="추출된 명사")
    filter_expr: Optional[str] = Field(None, description="필터 조건문")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "SUCCESS",
                "query": "검색 시스템",
                "query_timestamp": 1770101252580,
                "search_type": "SEARCH",
                "result_vars": ["hr", "board", "krule"],
                "result_names": ["직원검색", "게시판", "규정집"],
                "result_counts": [3, 2, 1],
                "result_timestamp": 1770101256414,
                "results": {
                    "hr": [
                        {
                            "emp_nm": "전명훈",
                            "emp_no": "31159",
                            "dept_nm": "정보전산팀",
                            "chag_duty": "업무",
                            "telno_offc": "5610",
                            "celpon_no": "",
                            "email_id": "a@b.com",
                            "img_link": "https://...",
                        }
                    ],
                    "board": [
                        {
                            "brd_name": "공지사항",
                            "title": "검색 시스템 정기 점검 안내",
                            "content": "검색 시스템 정기 점검으로 인하여 22:00~24:00 동안 서비스가 중단됩니다.",
                            "body_path": "/board/notice/2025/000123",
                            "poster_name": "정보전산팀",
                            "post_date": "2025-02-01",
                            "modify_date": "2025-02-02",
                        }
                    ],
                    "krule": [
                        {
                            "title": "정보보안 규정",
                            "state_name": "현행",
                            "text": "이 규정은 정보보안 관리에 관한 기본 원칙과 절차를 정함을 목적으로 한다.",
                            "revcd": "개정",
                            "revcha": "3",
                            "promul_dt": "2024-01-01",
                            "start_dt": "2024-02-01",
                            "upload_dt": "2024-02-10",
                            "download_file_url": "https://rules.example.com/SEC-001.pdf",
                            "bbscd": "SEC",
                            "writer": "규정관리팀",
                            "dept_name": "경영기획실",
                            "page_range": "1-10",
                        }
                    ],
                },
            }
        }


class ErrorResponse(BaseModel):
    """에러 응답"""

    success: bool = Field(False, description="성공 여부")
    message: str = Field(..., description="에러 메시지")
    detail: Optional[str] = Field(None, description="상세 에러 정보")


class SearchResult(BaseModel):
    """search 응답"""

    results: Any = Field(..., description="검색 결과")
    nouns: Optional[str] = Field(None, description="추출된 명사")
    filter_expr: Optional[str] = Field(None, description="필터 조건문")
