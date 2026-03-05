import json
import os

from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    """
    sLLM도 사용 가능하지만 default는 openai
    """

    def __init__(self, provider="openai", model="gpt-4o-mini"):
        self.provider = provider
        self.model = model
        self.llm = None
        self._validate_and_init()

    def _validate_and_init(self):
        if self.provider == "openai":
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
            self.llm = AsyncOpenAI(api_key=api_key)

        # 다른 provider 추가 시 여기에 추가

    async def invoke(self, prompt: str) -> str:
        if self.provider == "openai":
            response = await self.llm.responses.create(model=self.model, input=prompt)
            return response.output_text

        # 다른 provider 추가 시 여기에 추가
        return None

    @staticmethod
    def parse_json(text: str) -> dict:
        """LLM 응답에서 JSON 블록을 파싱합니다."""
        text = text.strip()
        if text.startswith("```"):
            # ```json ... ``` 형식 처리
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
