# Kubernetes LLM Assistant

This project is a **Kubernetes cluster assistant** that combines:

- **Flask (Python)** as the backend web server  
- **Kubernetes Python client** to fetch cluster resources (Pods, Services, Deployments)  
- **Amazon Bedrock (Claude LLM)** for natural language reasoning about the cluster state  
- **LangGraph** to orchestrate decision workflows  
- **HTML + JavaScript frontend** for interactive UI  

With this system, you can either:

- View raw Kubernetes resources (pods, services, deployments), or  
- Ask natural language questions like *“How many pods are running in default namespace?”* and get an answer from Claude.  

---

## Features

- List Kubernetes **Pods, Services, and Deployments** by namespace  
- Ask **natural language questions** about cluster state  
- Automatic decision logic → only fetches resources relevant to the question  
- Interactive **web frontend with HTML + JavaScript**  
- Works **locally (kubeconfig)** or **in-cluster (service account)**  
- Uses **AWS Bedrock (Claude)** for safe, grounded answers  

---

##  Frontend (JavaScript)

JavaScript runs inside the browser once the page (`index.html`) is loaded. It:

- Reads input from the user (**namespace**, **natural language query**)  
- Makes **AJAX calls (`fetch`)** to Flask API endpoints:  
  - `/api/pods`  
  - `/api/services`  
  - `/api/deployments`  
  - `/api/query`  
- Displays the results in the UI (`#output` for raw JSON, `#llm-answer` for LLM answers)  

---

### Example: Pods Button

```javascript
document.getElementById("btn-pods").addEventListener("click", async () => {
  const ns = nsInput.value || "default";
  const r = await fetch(`/api/pods?namespace=${encodeURIComponent(ns)}`);
  const j = await r.json();
  show(j);
});

```

Similar is for svc, deployment 


