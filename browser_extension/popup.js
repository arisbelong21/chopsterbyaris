const statusEl = document.getElementById("status");
async function checkStatus() {
  for (const port of [18421,18422,18423,18424,18425]) {
    try {
      const r = await fetch(`http://127.0.0.1:${port}/status`, { method: "GET" });
      if (!r.ok) continue;
      const payload = await r.json().catch(() => ({}));
      if (payload.product_id === "chopster-by-aris") { statusEl.textContent = "Chopster v8.5.5 terhubung."; statusEl.style.color = "#0F9F6E"; return; }
    } catch {}
  }
  statusEl.textContent = "Chopster tidak berjalan.";
  statusEl.style.color = "#D64545";
}
checkStatus();
document.getElementById("send").addEventListener("click", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab || !tab.url) {
    statusEl.textContent = "Tidak ada tautan di tab ini.";
    return;
  }
  statusEl.textContent = "Mengirim...";
  statusEl.style.color = "#5B6B82";
  chrome.runtime.sendMessage({ type: "send", url: tab.url }, (res) => {
    if (res && res.ok) { statusEl.textContent = "Terkirim ke Chopster."; statusEl.style.color = "#0F9F6E"; }
    else { statusEl.textContent = (res && res.error) || "Gagal mengirim."; statusEl.style.color = "#D64545"; }
  });
});
