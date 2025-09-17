# app.py
import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from k8s_client import list_pods, list_services, list_deployments
from llm_bedrock import answer_cluster_question

load_dotenv()
app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route("/")
def index():
    return render_template("index.html")

# API to list pods
@app.route("/api/pods")
def api_pods():
    ns = request.args.get("namespace", "default")
    result = list_pods(namespace=ns)
    return jsonify(result)

@app.route("/api/services")
def api_services():
    ns = request.args.get("namespace", "default")
    result = list_services(namespace=ns)
    return jsonify(result)

@app.route("/api/deployments")
def api_deployments():
    ns = request.args.get("namespace", "default")
    result = list_deployments(namespace=ns)
    return jsonify(result)

# Natural language query about cluster
@app.route("/api/query", methods=["POST"])
def api_query():
    body = request.json or {}
    question = body.get("question")
    namespace = body.get("namespace", "default")
    # Build a small snapshot: pods, services, deployments for the namespace
    pods = list_pods(namespace=namespace)
    services = list_services(namespace=namespace)
    deployments = list_deployments(namespace=namespace)
    cluster_snapshot = {
        "namespace": namespace,
        "pods": pods,
        "services": services,
        "deployments": deployments
    }
    llm_answer = answer_cluster_question(question, cluster_snapshot)
    return jsonify({"answer": llm_answer})

if __name__ == "__main__":
    # allow binding to 0.0.0.0 for EC2
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)

