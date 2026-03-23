const API_URL = "REPLACE_WITH_API_URL";

async function upload() {
  const file = document.getElementById("fileInput").files[0];
  const status = document.getElementById("status");

  if (!file) {
    status.innerText = "Select a file";
    return;
  }

  const res = await fetch(API_URL, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ fileName: file.name, contentType: file.type })
  });

  const data = await res.json();

  await fetch(data.uploadUrl, {
    method: "PUT",
    headers: {"Content-Type": file.type},
    body: file
  });

  status.innerText = "Upload successful";
}