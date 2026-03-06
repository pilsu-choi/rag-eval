import os
from deepagents.backends import FilesystemBackend
from langchain.tools import tool
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()

#########################################
## FULL TEXT SEARCH TESTSETS GENERATOR ##
#########################################

# Checkpointer is REQUIRED for human-in-the-loop
checkpointer = MemorySaver()

model = init_chat_model(model="gpt-4.1", api_key=os.getenv("OPENAI_API_KEY"))
agent = create_deep_agent(
    model=model,
    backend=FilesystemBackend(root_dir="./files/fts", virtual_mode=True),
    # interrupt_on={
    #     "ls": True,  # Default: approve, edit, reject
    #    "read_file": True,
    #    "write_file": True,
    #    "delete_file": True,
    #    "edit_file": True,
    #    "glob": True,
    #    "grep": True,
    # },
    checkpointer=checkpointer,  # Required!
)


import uuid
from langgraph.types import Command

config = {"configurable": {"thread_id": str(uuid.uuid4())}}

print("대화를 시작합니다. 종료하려면 'exit' 또는 'quit'을 입력하세요.\n")

result = None

prompt = """
너는 Full Text Search evaluation을 위한 데이터를 준비하는 에이전트야.

아래의 내용을 참고해서 작업을 수행해.

   - 파일 목록 내의 모든 json 파일을 읽고 1개당 10개의 testcase를 생성해줘.
   - testcase는 question, ground_truth, file_name 를 dict 형태로 작성해줘.
   - ground_truth는 list 형태로 작성해줘. 최대 5개까지 작성해줘.
   - testcase는 testsets/ 경로의 json 파일로 저장해줘. indent 4로 저장해.
   - 중간에 사용자에게 확인을 요청하지 말고, 필요한 툴을 연속으로 실행해서 완성까지 진행해.
"""
idx = 0
while True:
    # 인터럽트 상태가 아닐 때만 사용자 입력을 받음
    if result is None or not result.get("__interrupt__"):
        if idx == 0:
            user_input = prompt
            print("초기 입력: ", user_input)
        else:
            user_input = input("You: ").strip()

        if user_input.lower() in ("exit", "quit"):
            print("종료합니다.")
            break
        if not user_input:
            continue

        result = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]}, config=config
        )
        idx += 1

    # 인터럽트 처리
    if result.get("__interrupt__"):
        interrupts = result["__interrupt__"][0].value
        action_requests = interrupts["action_requests"]
        review_configs = interrupts["review_configs"]

        config_map = {cfg["action_name"]: cfg for cfg in review_configs}
        decisions = []

        for action in action_requests:
            name = action["name"]
            args = action["args"]
            allowed = config_map[name]["allowed_decisions"]

            print("\nTool execution requires approval")
            print(f"Tool: {name}")
            print(f"Arguments: {args}")
            print(f"Allowed decisions: {allowed}")

            input_to_decision = {"y": "approve", "n": "reject", "edit": "edit"}

            while True:
                decision_input = (
                    input("실행 여부를 입력하세요. (y/n/edit): ").strip().lower()
                )
                decision_type = input_to_decision.get(decision_input)

                if decision_type is None or decision_type not in allowed:
                    readable_allowed = [
                        {"approve": "y", "reject": "n", "edit": "edit"}.get(a, a)
                        for a in allowed
                    ]
                    print(f"Invalid decision. Allowed: {readable_allowed}")
                    continue

                if decision_type == "edit":
                    new_path = input("Enter new path: ")
                    decisions.append(
                        {
                            "type": "edit",
                            "edited_action": {"name": name, "args": {"path": new_path}},
                        }
                    )
                else:
                    decisions.append({"type": decision_type})
                break

        # 동일한 thread_id로 재개
        result = agent.invoke(Command(resume={"decisions": decisions}), config=config)

    else:
        # 일반 응답 출력 후 다음 사용자 입력 대기
        print(f"\nAgent: {result['messages'][-1].content}\n")
        result = None
