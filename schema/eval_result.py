from dataclasses import asdict, dataclass, field, fields as dc_fields


@dataclass
class EvalResult:
    idx: int | str
    question: str
    ground_truth: str
    retrieved_docs: list
    generated_answer: str | None = field(default=None)
    retrieval_precision: float | None = field(default=None, metadata={"score": True})
    retrieval_recall: float | None = field(default=None, metadata={"score": True})
    generation_faithfulness: float | None = field(
        default=None, metadata={"score": True}
    )
    generation_factual_correctness: float | None = field(
        default=None, metadata={"score": True}
    )
    retrieval_precision_reason: str | None = None
    retrieval_recall_reason: str | None = None
    generation_faithfulness_reason: str | None = None
    generation_factual_correctness_reason: str | None = None

    @classmethod
    def score_field_names(cls) -> list[str]:
        return [f.name for f in dc_fields(cls) if f.metadata.get("score")]

    def to_csv_dict(self) -> dict:
        return {
            f.name: getattr(self, f.name)
            for f in dc_fields(self)
            if not f.name.endswith("_reason")
        }

    def to_json_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def average_row(cls, results: list["EvalResult"]) -> dict:
        def _avg(values: list) -> float | None:
            valid = [v for v in values if v is not None]
            return round(sum(valid) / len(valid), 4) if valid else None

        scores = {
            name: _avg([getattr(r, name) for r in results])
            for name in cls.score_field_names()
        }
        return {"idx": "average", **scores}
