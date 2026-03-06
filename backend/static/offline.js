// Minimal IndexedDB queue for reports
const DB_NAME = "sch_offline";
const STORE = "reports";

function openDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains(STORE)) {
        db.createObjectStore(STORE, { keyPath: "id" });
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

async function putReport(obj) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE, "readwrite");
    tx.objectStore(STORE).put(obj);
    tx.oncomplete = () => resolve(true);
    tx.onerror = () => reject(tx.error);
  });
}

async function getAllReports() {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE, "readonly");
    const req = tx.objectStore(STORE).getAll();
    req.onsuccess = () => resolve(req.result || []);
    req.onerror = () => reject(req.error);
  });
}

async function deleteReport(id) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE, "readwrite");
    tx.objectStore(STORE).delete(id);
    tx.oncomplete = () => resolve(true);
    tx.onerror = () => reject(tx.error);
  });
}

async function getGeo() {
  return new Promise((resolve) => {
    if (!navigator.geolocation) return resolve(null);
    navigator.geolocation.getCurrentPosition(
      (pos) => resolve({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      () => resolve(null),
      { enableHighAccuracy: true, timeout: 6000 }
    );
  });
}

async function sendToServer(payload) {
  const res = await fetch("/api/student/report", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Server error");
  }
}

async function syncQueue() {
  if (!navigator.onLine) return;
  const items = await getAllReports();
  for (const item of items) {
    try {
      await sendToServer(item.payload);
      await deleteReport(item.id);
    } catch (e) {
      // stop if server fails; try again later
      break;
    }
  }
}

// Public API used by pages
window.SafeReports = {
  submitReport: async ({ title, details }) => {
    const geo = await getGeo();
    const payload = { title, details, ...(geo || {}) };

    if (navigator.onLine) {
      try {
        await sendToServer(payload);
        return;
      } catch (e) {
        // if online but server fails, fallback to queue
      }
    }

    const item = {
      id: "r_" + Date.now(),
      payload,
      queuedAt: Date.now(),
    };
    await putReport(item);
  },
  syncQueue,
};

window.addEventListener("online", () => syncQueue());
setInterval(() => syncQueue(), 8000);