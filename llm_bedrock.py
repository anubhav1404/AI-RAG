# llm_bedrock.py
import os
import json
import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID",
    "anthropic.claude-3-haiku-20240307-v1:0"  # default model
)

def bedrock_invoke(prompt, model_id=None, max_tokens=512):
    """
    Invoke an LLM on Amazon Bedrock using boto3 runtime client.
    Supports Anthropic Claude-style models.
    """
    model = model_id or BEDROCK_MODEL_ID
    client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

    # For Anthropic models, the correct request schema uses "messages"
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": prompt}]}
        ]
    }

    response = client.invoke_model(
        modelId=model,
        body=json.dumps(payload),
        accept="application/json",
        contentType="application/json",
    )

    body = response["body"].read().decode("utf-8")
    try:
        parsed = json.loads(body)
        # Anthropic Bedrock responses put text under content[0].text
        if "content" in parsed and len(parsed["content"]) > 0:
            return parsed["content"][0].get("text", "")
        return parsed
    except Exception:
        return body

def build_cluster_prompt(question, cluster_snapshot):
    """
    Build a prompt that includes the cluster snapshot (pods/services/deployments)
    and the user question, asking the model to answer concisely.
    """
    snapshot_text = json.dumps(cluster_snapshot, indent=2)
    prompt = f"""
You are a helpful assistant that answers questions about a Kubernetes cluster.
The following JSON is the current cluster snapshot (pods / services / deployments).
Use only the information in the snapshot to answer the user's question.
If the answer is not present, say you don't have enough information.

Cluster snapshot:
{snapshot_text}

User question:
{question}

Answer concisely and clearly.
"""
    return prompt.strip()

def answer_cluster_question(question, cluster_snapshot):
    prompt = build_cluster_prompt(question, cluster_snapshot)
    return bedrock_invoke(prompt)

