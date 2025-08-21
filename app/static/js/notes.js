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
});
