# graph.py
from langgraph.graph import StateGraph, END
from llm_bedrock import bedrock_invoke
from k8s_client import (
    list_pods, list_services, list_deployments,
    list_pods_all, list_services_all, list_deployments_all
)
import json

def build_graph():
    """
    Build a LangGraph workflow:
    1. Decide which K8s resources to fetch
    2. If it's a plain 'list' query, return raw data
    3. Otherwise, call Bedrock to summarize/answer
    """

    graph = StateGraph(dict)

    # Node: decide what to fetch
    def decide_node(state):
        ns = state.get("namespace", "default")
        q = state["question"].lower()

        all_ns = ns == "all" or "all namespaces" in q

        # If the user explicitly asks to "list" something -> return raw data
        if "list" in q and "pod" in q:
            state["pods"] = list_pods_all() if all_ns else list_pods(namespace=ns)
            state["answer"] = state["pods"]
            state["skip_llm"] = True
            return state

        if "list" in q and ("service" in q or "svc" in q):
            state["services"] = list_services_all() if all_ns else list_services(namespace=ns)
            state["answer"] = state["services"]
            state["skip_llm"] = True
            return state

        if "list" in q and "deployment" in q:
            state["deployments"] = list_deployments_all() if all_ns else list_deployments(namespace=ns)
            state["answer"] = state["deployments"]
            state["skip_llm"] = True
            return state

        # Otherwise, prepare snapshot for LLM
        if "pod" in q:
            state["pods"] = list_pods_all() if all_ns else list_pods(namespace=ns)
        if "service" in q or "svc" in q:
            state["services"] = list_services_all() if all_ns else list_services(namespace=ns)
        if "deployment" in q:
            state["deployments"] = list_deployments_all() if all_ns else list_deployments(namespace=ns)

        return state

    graph.add_node("decide", decide_node)

    # Node: call LLM
    def llm_node(state):
        # If flagged as skip, bypass LLM and return directly
        if state.get("skip_llm"):
            return state

        cluster_snapshot = {
            "namespace": state.get("namespace", "default"),
            "pods": state.get("pods", []),
            "services": state.get("services", []),
            "deployments": state.get("deployments", []),
        }

        prompt = f"""
You are a Kubernetes assistant.

Here is the live cluster snapshot (JSON):
{json.dumps(cluster_snapshot, indent=2)}

RULES:
- Only use this snapshot to answer the user's question.
- Explicitly include namespaces (like kube-system, default, etc.) if present.
- Do NOT suggest kubectl commands.
- If the information is not in the snapshot, reply exactly: "I don't have enough information from the snapshot."

User question:
{state['question']}

Answer concisely using ONLY the snapshot.
"""
        state["answer"] = bedrock_invoke(prompt)
        return state

    graph.add_node("llm", llm_node)

    # Wire nodes
    graph.set_entry_point("decide")
    graph.add_edge("decide", "llm")
    graph.add_edge("llm", END)

    return graph.compile()

