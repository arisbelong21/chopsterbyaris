const PORTS = [18421, 18422, 18423, 18424, 18425];
const EXPECTED_PRODUCT_ID = "chopster-by-aris";

async function sendUrl(url) {
  let lastError = "Chopster tidak merespons";
  for (const port of PORTS) {
    try {
      const res = await fetch(`http://127.0.0.1:${port}/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      if (!res.ok) { lastError = "Chopster menolak tautan"; continue; }
      const payload = await res.json().catch(() => ({}));
      if (payload.product_id !== EXPECTED_PRODUCT_ID) {
        lastError = "Port dipakai aplikasi lain";
        continue;
      }
      return { ok: true };
    } catch (err) {
      lastError = "Pastikan Chopster sedang berjalan";
    }
  }
  return { ok: false, error: lastError };
}

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "send-to-chopster",
    title: "Kirim ke Chopster",
    contexts: ["link", "page", "video"],
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const url = info.linkUrl || info.srcUrl || (tab && tab.url);
  if (!url) return;
  await sendUrl(url);
});

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg && msg.type === "send") {
    sendUrl(msg.url).then(sendResponse);
    return true;
  }
  if (msg && msg.type === "status") {
    (async () => {
      for (const port of PORTS) {
        try {
          const r = await fetch(`http://127.0.0.1:${port}/status`);
          if (!r.ok) continue;
          const payload = await r.json().catch(() => ({}));
          if (payload.product_id === EXPECTED_PRODUCT_ID) return sendResponse({ ok: true });
        } catch {}
      }
      sendResponse({ ok: false });
    })();
    return true;
  }
  return false;
});
