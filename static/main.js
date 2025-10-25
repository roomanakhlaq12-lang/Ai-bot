const promptEl = document.getElementById("prompt");
const modelEl = document.getElementById("model");
const submitBtn = document.getElementById("submit");
const clearBtn = document.getElementById("clear");
const responseEl = document.getElementById("response");
const loaderEl = document.getElementById("loader");
const statusEl = document.getElementById("status");
const copyBtn = document.getElementById("copy");

function setLoading(on){
  loaderEl.classList.toggle("hidden", !on);
  submitBtn.disabled = on;
  statusEl.textContent = on ? "Waiting for response..." : "";
}

submitBtn.addEventListener("click", async () => {
  const prompt = promptEl.value.trim();
  const model = modelEl.value;
  if (!prompt) {
    statusEl.textContent = "Please enter a prompt.";
    return;
  }

  setLoading(true);
  responseEl.textContent = "";

  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, model })
    });

    if (!res.ok) {
      const text = await res.text();
      responseEl.textContent = `Error ${res.status}: ${text}`;
      statusEl.textContent = "Error from server.";
    } else {
      const data = await res.json();
      if (data.response) {
        responseEl.textContent = data.response;
        statusEl.textContent = "Response received.";
      } else {
        responseEl.textContent = JSON.stringify(data, null, 2);
        statusEl.textContent = "Response received (raw).";
      }
    }
  } catch (err) {
    responseEl.textContent = `Network error: ${err.message}`;
    statusEl.textContent = "Network error.";
  } finally {
    setLoading(false);
  }
});

clearBtn.addEventListener("click", () => {
  promptEl.value = "";
  responseEl.textContent = "";
  statusEl.textContent = "";
});

copyBtn.addEventListener("click", async () => {
  const text = responseEl.textContent;
  if (!text) {
    statusEl.textContent = "Nothing to copy.";
    return;
  }
  try {
    await navigator.clipboard.writeText(text);
    statusEl.textContent = "Copied to clipboard!";
  } catch (e) {
    statusEl.textContent = "Copy failed.";
  }
});
