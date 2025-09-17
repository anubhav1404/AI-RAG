# app.py
import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from k8s_client import list_pods, list_services, list_deployments
from graph import build_graph

load_dotenv()
app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/pods")
def api_pods():
    ns = request.args.get("namespace", "default")
    return jsonify(list_pods(namespace=ns))

@app.route("/api/services")
def api_services():
    ns = request.args.get("namespace", "default")
    return jsonify(list_services(namespace=ns))

@app.route("/api/deployments")
def api_deployments():
    ns = request.args.get("namespace", "default")
    return jsonify(list_deployments(namespace=ns))

@app.route("/api/query", methods=["POST"])
def api_query():
    body = request.json or {}
    question = body.get("question")
    namespace = body.get("namespace", "default")

    graph = build_graph()
    result = graph.invoke({"question": question, "namespace": namespace})
    return jsonify({"answer": result["answer"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)

