# graph.py
from langgraph.graph import StateGraph, END
from llm_bedrock import bedrock_invoke
from k8s_client import list_pods, list_services, list_deployments

def build_graph():
    """
    Build a LangGraph workflow:
    1. Decide which K8s resources to fetch
    2. Call Bedrock to answer
    """

    graph = StateGraph(dict)

    # Node: decide what to fetch
    def decide_node(state):
        ns = state.get("namespace", "default")
        q = state["question"].lower()

        if "pod" in q:
            state["pods"] = list_pods(namespace=ns)
        if "service" in q or "svc" in q:
            state["services"] = list_services(namespace=ns)
        if "deployment" in q:
            state["deployments"] = list_deployments(namespace=ns)

        return state

    graph.add_node("decide", decide_node)

    # Node: call LLM
    def llm_node(state):
        cluster_snapshot = {
            "namespace": state.get("namespace", "default"),
            "pods": state.get("pods", []),
            "services": state.get("services", []),
            "deployments": state.get("deployments", []),
        }

        prompt = f"""
You are a Kubernetes assistant.
Here is the cluster snapshot (JSON):
{cluster_snapshot}

User question:
{state['question']}

Answer concisely and clearly.
"""
        state["answer"] = bedrock_invoke(prompt)
        return state

    graph.add_node("llm", llm_node)

    # Wire nodes
    graph.set_entry_point("decide")
    graph.add_edge("decide", "llm")
    graph.add_edge("llm", END)

    return graph.compile()

