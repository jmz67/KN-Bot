from typing_extensions import TypedDict, List, Optional 

class ChatState(TypedDict, total=False):

    # 本轮用户消息
    user_input: str
    # 完整的对话历史
    chat_history: List[str]
    # 当前阶段
    current_stage: int 
    planner_plan: str 
    classification_result: Optional[int]
    manager_decision: str 
    manager_reason: Optional[str]
    assistant_reply: Optional[str] 