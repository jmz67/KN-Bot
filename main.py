import logging 
import asyncio
from core.graph import workflow
from core.state import ChatState

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

async def chat():
    state: ChatState = {
        "user_input": "",
        "chat_history": [],
        "current_stage": 1,
    }
    print("👋 欢迎使用 CBT 机器人！输入 'quit' 结束。\n")
    while True:
        user = input("你: ")
        if user.lower() == "quit":
            break
        state["user_input"] = user
        # state = workflow.invoke(state)
        # 使用 langGraph 的 stream 方法
        async for step in workflow.astream(state):
            state = step 
            
        print()  

if __name__ == "__main__":
    asyncio.run(chat())
