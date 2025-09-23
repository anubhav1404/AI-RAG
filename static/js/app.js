document.addEventListener("DOMContentLoaded", () => {
  const nsInput = document.getElementById("namespace");
  const llmOut = document.getElementById("llm-answer");

  function renderTable(data) {
    if (!Array.isArray(data)) {
      return `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    }
    if (data.length === 0) {
      return "<p>No resources found.</p>";
    }
    const keys = Object.keys(data[0]);
    const header = `<tr>${keys.map(k => `<th>${k}</th>`).join("")}</tr>`;
    const rows = data.map(item =>
      `<tr>${keys.map(k => `<td>${item[k] ?? ""}</td>`).join("")}</tr>`
    ).join("");
    return `<table><thead>${header}</thead><tbody>${rows}</tbody></table>`;
  }

  // Sidebar button handlers -> fetch via natural query instead of raw JSON
  document.querySelectorAll(".sidebar button").forEach(btn => {
    btn.addEventListener("click", async () => {
      const ns = nsInput.value || "default";
      const action = btn.dataset.action;
      let question = "";

      if (action === "pods") question = `List all pods in ${ns} namespace`;
      if (action === "services") question = `List all services in ${ns} namespace`;
      if (action === "deployments") question = `List all deployments in ${ns} namespace`;

      llmOut.textContent = "Loading...";
      const r = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, namespace: ns })
      });
      const j = await r.json();

      if (Array.isArray(j.answer) && j.answer.length > 0 && typeof j.answer[0] === "object") {
        llmOut.innerHTML = renderTable(j.answer);
      } else {
        llmOut.textContent = typeof j.answer === "string"
          ? j.answer
          : JSON.stringify(j.answer, null, 2);
      }
    });
  });

  // Ask button handler
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

    if (Array.isArray(j.answer) && j.answer.length > 0 && typeof j.answer[0] === "object") {
      llmOut.innerHTML = renderTable(j.answer);
    } else {
      llmOut.textContent = typeof j.answer === "string"
        ? j.answer
        : JSON.stringify(j.answer, null, 2);
    }
  });
});

