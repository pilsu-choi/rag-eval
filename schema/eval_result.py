from dataclasses import asdict, dataclass, field, fields as dc_fields


@dataclass
class EvalResult:
    idx: int | str
    question: str
    ground_truth: str
    retrieved_docs: list
    generated_answer: str
    retrieval_precision: float = field(metadata={"score": True})
    retrieval_recall: float = field(metadata={"score": True})
    generation_faithfulness: float = field(metadata={"score": True})
    generation_factual_correctness: float = field(metadata={"score": True})
    retrieval_precision_reason: str | None = None
    retrieval_recall_reason: str | None = None
    generation_faithfulness_reason: str | None = None
    generation_factual_correctness_reason: str | None = None

    @classmethod
    def score_field_names(cls) -> list[str]:
        return [f.name for f in dc_fields(cls) if f.metadata.get("score")]

    def to_csv_dict(self) -> dict:
        return {f.name: getattr(self, f.name) for f in dc_fields(self) if not f.name.endswith("_reason")}

    def to_json_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def average_row(cls, results: list["EvalResult"]) -> dict:
        n = len(results)
        scores = (
            {name: round(sum(getattr(r, name) for r in results) / n, 4) for name in cls.score_field_names()}
            if n > 0
            else {name: None for name in cls.score_field_names()}
        )
        return {"idx": "average", **scores}
