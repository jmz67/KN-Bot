

def reply_stage_n(stage: int, chat_history: str, user_input: str) -> str:
    """不同阶段的回复模板，可接 LangChain PromptTemplate."""
    
    RESPONSES = {
        1: "嗨！很高兴见到你。感觉今天心情如何呢？",
        2: "我理解你的困扰。我们先集中在你最想解决的问题上，好吗？",
        3: "好的，让我们一起梳理一下想法-情绪-行为的关系……",
        4: "有些知识可以帮助你理解这种行为，让我解释一下：",
        5: "我们来尝试一个小练习，作为本周的家庭作业，你觉得如何？",
        6: "今天聊得很好，期待下次跟进！加油💪",
    }
    return RESPONSES[stage]
