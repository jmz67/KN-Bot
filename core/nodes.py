import logging 
import time 

import re, xml.etree.ElementTree as ET
from langchain_openai import ChatOpenAI
from core.state import ChatState
from core.prompts import PLANNER_PROMPT, MANAGER_PROMPT, STAGE_RULES, STAGE_SYSTEM_ZH
from core.tools import reply_stage_n

llm = ChatOpenAI(
    model="Qwen2.5-32B-Instruct",
    api_key="gpustack_35c1d25d2f04a28f_900dccd6cf7d1b5fd4bc99725ce2bb0f",
    base_url="http://211.90.240.240:30001/v1",  
    temperature=0.7  
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# ---------- Planner ----------
def planner(state: ChatState) -> ChatState:
    start = time.perf_counter()
    prompt = PLANNER_PROMPT.format(
        chat_history="\n".join(state.get("chat_history", [])),
        user_input=state["user_input"],
        current_stage=state["current_stage"],
        stage_rules=STAGE_RULES
    )
    xml = llm.invoke(prompt).content.strip()
    
    m = re.search(r"<classification_result>(\d)</classification_result>", xml)
    next_stage = int(m.group(1)) if m else None
    elapsed = time.perf_counter() - start
    logging.info(f"[planner] output:\n {xml}")
    logging.info(f"[planner] next_stage: {next_stage}, elapsed: {elapsed:.3f}s")
    
    return {**state, "planner_plan": xml, "classification_result": next_stage}

# ---------- Manager ----------
def manager(state: ChatState) -> ChatState:
    start = time.perf_counter()
    prompt = MANAGER_PROMPT.format(
        planner_plan=state["planner_plan"],
        current_stage=state["current_stage"]
    )
    decision = llm.invoke(prompt).content.strip()
    elapsed = time.perf_counter() - start
    logging.info(f"[manager] output:\n {decision}")
    logging.info(f"[manager] elapsed: {elapsed:.3f}s")

    # ---------- ① 通过 ----------
    if decision.startswith("<manager_verify>accept"):
        # 抓取数字（支持多位）
        m = re.search(r"<manager_verify>accept\s+(\d+)</manager_verify>", decision)
        next_stage = int(m.group(1)) if m else state["current_stage"]
        return {
            **state,
            "manager_decision": "accept",
            "classification_result": next_stage
        }

    # ---------- ② 驳回 ----------
    elif decision.startswith("<manager_verify>reject"):
        m = re.search(r"<feedback_comment>(.*?)</feedback_comment>", decision, re.S)
        reason = m.group(1).strip() if m else "未提供原因"
        return {
            **state,
            "manager_decision": "reject",
            "manager_reason": reason
        }

    # ---------- ③ 兜底 ----------
    else:
        logging.warning("[manager] 无法解析输出格式，自动 reject")
        return {
            **state,
            "manager_decision": "reject",
            "manager_reason": "无法解析 manager 输出"
        }

# ---------- Stage-N ----------
def make_stage_node(i: int):
    def _node(state: ChatState) -> ChatState:
        start = time.perf_counter()
        # 动态生成阶段专属 prompt
        system_prompt = STAGE_SYSTEM_ZH.get(i, "你是 CBT 咨询师，请合理回复。")
        prompt = f"""{system_prompt}

        【对话历史】
        {chr(10).join(state.get("chat_history", []))}

        【用户输入】
        {state["user_input"]}
        """
        # 用大模型生成回复
        reply_chunks = []
        for chunk in llm.stream(prompt):
            reply_chunks.append(chunk.content)
        reply = "".join(reply_chunks).strip()
        elapsed = time.perf_counter() - start
        # logging.info(f"[stage_{i}] reply:\n {reply}")
        logging.info(f"[stage_{i}] elapsed: {elapsed:.3f}s")
        return {**state, "assistant_reply": reply, "current_stage": i}
    return _node

stage_nodes = {i: make_stage_node(i) for i in range(1, 7)}

# ---------- Aggregator ----------
def aggregator(state: ChatState) -> ChatState:
    start = time.perf_counter()
    state["chat_history"].append(f"Assistant: {state['assistant_reply']}")
    logging.info(f"[aggregator] appended reply to chat_history")
    elapsed = time.perf_counter() - start
    logging.info(f"[aggregator] elapsed: {elapsed:.3f}s")
    print(f"[Stage {state['current_stage']}] : {state['assistant_reply']}")
    return state
