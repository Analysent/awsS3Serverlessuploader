const CONFIG = window.S3_UPLOADER_CONFIG || {};
const API_BASE_URL = (CONFIG.API_BASE_URL || "").replace(/\/$/, "");

const fileInput = document.getElementById("fileInput");
const browseBtn = document.getElementById("browseBtn");
const dropZone = document.getElementById("dropZone");
const uploadQueue = document.getElementById("uploadQueue");
const statusEl = document.getElementById("status");
const refreshBtn = document.getElementById("refreshBtn");
const dashboardEl = document.getElementById("dashboard");
const statsEl = document.getElementById("stats");

function formatBytes(bytes = 0) {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let size = bytes;
  let unitIndex = 0;
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex += 1;
  }
  return `${size.toFixed(size >= 10 || unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`;
}

function isImage(file) {
  return file.type.startsWith("image/");
}

function createUploadCard(file) {
  const wrapper = document.createElement("div");
  wrapper.className = "upload-item";

  const top = document.createElement("div");
  top.className = "upload-top";

  const meta = document.createElement("div");
  meta.className = "file-meta";

  const name = document.createElement("div");
  name.className = "file-name";
  name.textContent = file.name;

  const sub = document.createElement("div");
  sub.className = "file-sub";
  sub.textContent = `${file.type || "unknown"} • ${formatBytes(file.size)}`;

  meta.appendChild(name);
  meta.appendChild(sub);

  if (isImage(file)) {
    const img = document.createElement("img");
    img.className = "preview-image";
    img.alt = file.name;
    img.src = URL.createObjectURL(file);
    top.appendChild(meta);
    top.appendChild(img);
  } else {
    top.appendChild(meta);
  }

  const progressBar = document.createElement("div");
  progressBar.className = "progress-bar";

  const progressFill = document.createElement("div");
  progressFill.className = "progress-bar-fill";
  progressBar.appendChild(progressFill);

  const status = document.createElement("div");
  status.className = "file-sub";
  status.textContent = "Waiting to upload...";

  wrapper.appendChild(top);
  wrapper.appendChild(progressBar);
  wrapper.appendChild(status);

  uploadQueue.appendChild(wrapper);

  return { progressFill, status };
}

async function requestPresignedUrl(file) {
  const response = await fetch(`${API_BASE_URL}/presign`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      fileName: file.name,
      contentType: file.type,
      fileSize: file.size
    })
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Failed to get upload URL");
  }
  return data;
}

function uploadWithProgress(url, file, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("PUT", url);
    xhr.setRequestHeader("Content-Type", file.type);

    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) {
        const percent = Math.round((event.loaded / event.total) * 100);
        onProgress(percent);
      }
    };

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve();
      } else {
        reject(new Error("Upload failed"));
      }
    };

    xhr.onerror = () => reject(new Error("Network error during upload"));
    xhr.send(file);
  });
}

async function handleFiles(files) {
  if (!API_BASE_URL || API_BASE_URL.includes("PASTE_API_BASE_URL_HERE")) {
    statusEl.textContent = "Set frontend/config.js with your deployed API base URL first.";
    return;
  }

  statusEl.textContent = `Uploading ${files.length} file(s)...`;

  for (const file of files) {
    const ui = createUploadCard(file);

    try {
      ui.status.textContent = "Requesting secure upload URL...";
      const presign = await requestPresignedUrl(file);

      ui.status.textContent = "Uploading to S3...";
      await uploadWithProgress(presign.uploadUrl, file, (percent) => {
        ui.progressFill.style.width = `${percent}%`;
        ui.status.textContent = `Uploading... ${percent}%`;
      });

      ui.progressFill.style.width = "100%";
      ui.status.textContent = `Uploaded successfully • ${presign.key}`;
    } catch (error) {
      ui.status.textContent = `Error: ${error.message}`;
    }
  }

  statusEl.textContent = "Upload flow complete.";
  await loadDashboard();
}

async function loadDashboard() {
  if (!API_BASE_URL || API_BASE_URL.includes("PASTE_API_BASE_URL_HERE")) {
    statsEl.innerHTML = "";
    dashboardEl.innerHTML = '<div class="empty-state">Configure <code>frontend/config.js</code> after backend deployment to load dashboard data.</div>';
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/uploads`);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Failed to load uploads");
    }

    const items = data.items || [];
    renderStats(items);
    renderDashboard(items);
  } catch (error) {
    dashboardEl.innerHTML = `<div class="empty-state">Dashboard error: ${error.message}</div>`;
  }
}

function renderStats(items) {
  const totalFiles = items.length;
  const totalBytes = items.reduce((sum, item) => sum + Number(item.file_size || 0), 0);
  const imageCount = items.filter((item) => String(item.content_type || "").startsWith("image/")).length;

  statsEl.innerHTML = `
    <div class="stat-card">
      <div class="stat-label">Total files</div>
      <div class="stat-value">${totalFiles}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Stored size</div>
      <div class="stat-value">${formatBytes(totalBytes)}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Images</div>
      <div class="stat-value">${imageCount}</div>
    </div>
  `;
}

function renderDashboard(items) {
  if (!items.length) {
    dashboardEl.innerHTML = '<div class="empty-state">No processed uploads yet. Upload a file to populate the dashboard.</div>';
    return;
  }

  dashboardEl.innerHTML = items.map((item) => {
    const name = item.file_name || item.object_key || "Unknown file";
    const size = formatBytes(Number(item.file_size || 0));
    const type = item.content_type || "unknown";
    const processedAt = item.processed_at ? new Date(item.processed_at).toLocaleString() : "n/a";
    const aiStatus = item.ai_status || "disabled";
    const aiSummary = item.ai_summary || "No AI summary available.";

    return `
      <article class="dashboard-card">
        <div class="dashboard-top">
          <div>
            <p class="dashboard-title">${name}</p>
            <p class="dashboard-subtitle">${type} • ${size}</p>
          </div>
          <span class="badge">${aiStatus}</span>
        </div>
        <p class="dashboard-footer">Object key: ${item.object_key || "n/a"}</p>
        <p class="dashboard-footer">Processed: ${processedAt}</p>
        <p class="dashboard-footer">${aiSummary}</p>
      </article>
    `;
  }).join("");
}

browseBtn.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", () => handleFiles([...fileInput.files]));

dropZone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropZone.classList.remove("dragover");
  const files = [...event.dataTransfer.files];
  handleFiles(files);
});

refreshBtn.addEventListener("click", loadDashboard);

loadDashboard();
