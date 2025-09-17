// static/js/app.js
document.addEventListener("DOMContentLoaded", () => {
  const nsInput = document.getElementById("namespace");
  const out = document.getElementById("output");
  const llmOut = document.getElementById("llm-answer");

  function show(obj) {
    out.textContent = JSON.stringify(obj, null, 2);
  }

  document.getElementById("btn-pods").addEventListener("click", async () => {
    const ns = nsInput.value || "default";
    const r = await fetch(`/api/pods?namespace=${encodeURIComponent(ns)}`);
    const j = await r.json();
    show(j);
  });

  document.getElementById("btn-svcs").addEventListener("click", async () => {
    const ns = nsInput.value || "default";
    const r = await fetch(`/api/services?namespace=${encodeURIComponent(ns)}`);
    const j = await r.json();
    show(j);
  });

  document.getElementById("btn-deps").addEventListener("click", async () => {
    const ns = nsInput.value || "default";
    const r = await fetch(`/api/deployments?namespace=${encodeURIComponent(ns)}`);
    const j = await r.json();
    show(j);
  });

  document.getElementById("btn-ask").addEventListener("click", async () => {
    const ns = nsInput.value || "default";
    const question = document.getElementById("nlq-question").value;
    llmOut.textContent = "Thinking...";
    const r = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, namespace: ns })
    });
    const j = await r.json();
    llmOut.textContent = JSON.stringify(j, null, 2);
  });
});

