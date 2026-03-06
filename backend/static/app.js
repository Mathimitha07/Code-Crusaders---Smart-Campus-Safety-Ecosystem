// app.js — tiny shared helpers (safe to keep even if you don't use everything)
<script src="https://unpkg.com/html5-qrcode"></script>
// 1) Simple toast notifications (optional but nice UX)
(function () {
  const TOAST_ID = "sch-toast-root";

  function ensureRoot() {
    let root = document.getElementById(TOAST_ID);
    if (!root) {
      root = document.createElement("div");
      root.id = TOAST_ID;
      root.style.position = "fixed";
      root.style.right = "16px";
      root.style.bottom = "16px";
      root.style.zIndex = "9999";
      root.style.display = "flex";
      root.style.flexDirection = "column";
      root.style.gap = "10px";
      document.body.appendChild(root);
    }
    return root;
  }

  function toast(message, type = "info", ms = 2500) {
    const root = ensureRoot();
    const el = document.createElement("div");

    // Tailwind-like class styling without needing JS framework
    const base =
      "min-width:220px; max-width:340px; padding:12px 14px; border-radius:14px; " +
      "border:1px solid; box-shadow:0 10px 20px rgba(2,6,23,0.08); " +
      "font-size:14px; line-height:1.2; background:#fff;";

    const variants = {
      info: "border-color:#e2e8f0; color:#0f172a;",
      success: "border-color:#bbf7d0; color:#166534; background:#f0fdf4;",
      error: "border-color:#fecaca; color:#991b1b; background:#fef2f2;",
      warn: "border-color:#fde68a; color:#92400e; background:#fffbeb;"
    };

    el.setAttribute("style", base + (variants[type] || variants.info));
    el.textContent = message;

    root.appendChild(el);

    setTimeout(() => {
      el.style.opacity = "0";
      el.style.transform = "translateY(6px)";
      el.style.transition = "all 200ms ease";
      setTimeout(() => el.remove(), 220);
    }, ms);
  }

  // Expose globally
  window.SCH = window.SCH || {};
  window.SCH.toast = toast;
})();

// 2) Small helper: confirm dialog for buttons with data-confirm
document.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-confirm]");
  if (!btn) return;
  const msg = btn.getAttribute("data-confirm") || "Are you sure?";
  if (!confirm(msg)) e.preventDefault();
});

// 3) Network badge helper (optional)
window.SCH = window.SCH || {};
window.SCH.netText = () => (navigator.onLine ? "Online ✅" : "Offline ⚠️");
// 4) QR Scanner helper (forces BACK camera on mobile)
// Requires html5-qrcode library on the scan page:
// <script src="https://unpkg.com/html5-qrcode"></script>
window.SCH = window.SCH || {};

window.SCH.startQrScanner = async function ({
  elementId = "qr-reader",
  onScanText = (text) => console.log("QR:", text),
  fps = 10,
  qrbox = 250
} = {}) {
  try {
    if (typeof Html5Qrcode === "undefined") {
      window.SCH.toast?.("Scanner lib missing: include html5-qrcode", "error", 3500);
      throw new Error("Html5Qrcode not found. Add <script src='https://unpkg.com/html5-qrcode'></script>");
    }

    const devices = await Html5Qrcode.getCameras();
    if (!devices || devices.length === 0) {
      window.SCH.toast?.("No camera found", "error", 3000);
      return null;
    }

    // ✅ Pick back camera if possible (most reliable)
    let back = devices.find(d => /back|rear|environment/i.test(d.label));
    if (!back) back = devices[devices.length - 1]; // fallback: usually back camera

    const scanner = new Html5Qrcode(elementId);

    await scanner.start(
      // Use device id to force back camera
      { deviceId: { exact: back.id } },
      { fps, qrbox, rememberLastUsedCamera: true },
      (decodedText) => {
        // stop to avoid multiple scans
        scanner.stop().catch(() => {});
        onScanText(decodedText);
      },
      () => {} // ignore scan errors
    );

    window.SCH.toast?.("Back camera opened ✅", "success", 1500);
    return scanner;
  } catch (e) {
    console.error(e);

    // Fallback: facingMode environment (some browsers prefer this)
    try {
      const scanner = new Html5Qrcode(elementId);
      await scanner.start(
        { facingMode: "environment" }, // ✅ back camera hint
        { fps, qrbox, rememberLastUsedCamera: true },
        (decodedText) => {
          scanner.stop().catch(() => {});
          onScanText(decodedText);
        },
        () => {}
      );
      window.SCH.toast?.("Back camera opened ✅", "success", 1500);
      return scanner;
    } catch (e2) {
      console.error(e2);
      window.SCH.toast?.("Camera blocked. Use HTTPS (ngrok) + allow camera permission.", "error", 4500);
      return null;
    }
  }
};