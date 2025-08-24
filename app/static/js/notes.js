document.addEventListener("DOMContentLoaded", () => {
  const textForm = document.getElementById("note-text-form");
  const textMsg = document.getElementById("text-form-msg");
  const pdfForm = document.getElementById("note-pdf-form");
  const pdfMsg = document.getElementById("pdf-form-msg");
  


//   // Save manual note
  textForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    textMsg.textContent = "Saving…";

    const formData = new FormData(textForm);

    const res = await fetch("/notes/save_text", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    textMsg.textContent = data.msg || "Done";
    if (data.ok) setTimeout(() => window.location.reload(), 1000);
  });


  // Upload & extract PDF
  pdfForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    pdfMsg.textContent = "Uploading…";
    const formData = new FormData(pdfForm);

    const res = await fetch("/notes/upload_pdf", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    pdfMsg.textContent = data.msg || "Done";
    if (data.ok) setTimeout(() => window.location.reload(), 1000);
  });


  const deepseekBtn = document.getElementById("deepseek-btn");
  const msg = document.getElementById("deepseek-msg");

  deepseekBtn?.addEventListener("click", async () => {
    const noteSelect = document.getElementById("note-select");
    const noteId = Number(noteSelect.value);
    if (!noteId) {
      alert("No note selected");
      return;
    }

    // const btn = document.getElementById("deepseek-btn");
    deepseekBtn.disabled = true;
    deepseekBtn.textContent = "Processing…";
    if(msg) msg.textContent = "Sending note to DeepSeek…";

    try {
      const formData = new FormData();
      formData.append("note_id", noteId);

      const res = await fetch("/notes/process_deepseek", {
        method: "POST",
        body: formData
      });
      const data = await res.json();

      if (data.ok) {
        if (msg) msg.textContent = `✅ ${data.msg}`;
      } else {
        if (msg) msg.textContent = `❌ ${data.msg}`;
      }
    } catch (err) {
      console.error(err);
      if (msg) msg.textContent = "Error connecting to DeepSeek API.";
    } finally {
      deepseekBtn.disabled = false;
      deepseekBtn.textContent = "Process with DeepSeek";
    }
});



});
