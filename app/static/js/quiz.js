let currentQuizId = null;

async function loadNotes() {
  try {
    let res = await fetch("/api/notes");
    let notes = await res.json();
    let sel = document.getElementById("note-select");
    sel.innerHTML = "";
    if (!notes.length) {
      sel.innerHTML = `<option value="">No notes available</option>`;
      return;
    }
    notes.forEach(n => {
      sel.innerHTML += `<option value="${n.id}">${n.title}</option>`;
    });
  } catch (err) {
    console.error("Error loading notes:", err);
    document.getElementById("quiz-msg").textContent = "⚠️ Failed to load notes.";
  }
}

async function generateQuiz() {
  let noteId = document.getElementById("note-select").value;
  let count = document.getElementById("count-input").value || 5;
  let form = document.getElementById("quiz-form");
  let msg = document.getElementById("quiz-msg");

  form.innerHTML = "";
  msg.textContent = "";

  if (!noteId) {
    msg.textContent = "⚠️ Please select a note first!";
    return;
  }

  msg.textContent = "⏳ Generating quiz…";

  try {
    let res = await fetch("/quizzes/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ note_id: noteId, count: count })
    });

    let data = await res.json();
    msg.textContent = "";

    if (!data.ok) {
      msg.textContent = "⚠️ " + data.msg;
      return;
    }

    currentQuizId = data.quiz_id;

    data.quiz.forEach((q, i) => {
      form.innerHTML += `
        <div class="mb-3 p-3 border rounded-lg bg-gray-700">
          <p class="font-medium">Q${i + 1}: ${q.question}</p>
          <div class="mt-2 space-y-1">
            ${q.options
              .map(
                o => `
              <label class="block">
                <input type="radio" name="q${i}" value="${o}" class="mr-2">
                ${o}
              </label>
            `
              )
              .join("")}
          </div>
        </div>
      `;
    });

    document.getElementById("submit-btn").classList.remove("hidden");
  } catch (err) {
    console.error("Error generating quiz:", err);
    msg.textContent = "⚠️ Failed to generate quiz.";
  }
}

async function submitQuiz() {
  let answers = {};
  document.querySelectorAll("#quiz-form div").forEach((div, i) => {
    let selected = div.querySelector("input[type=radio]:checked");
    if (selected) {
      answers[i + 1] = selected.value;
    }
  });

  let box = document.getElementById("quiz-result");
  box.innerHTML = "";
  box.textContent = "⏳ Submitting…";

  try {
    let res = await fetch("/quizzes/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quiz_id: currentQuizId, answers: answers })
    });

    let data = await res.json();
    box.textContent = "";

    if (!data.ok) {
      box.innerHTML = `<div class="text-red-400">⚠️ ${data.msg}</div>`;
      return;
    }

    box.innerHTML = `
      <div class="p-3 bg-gray-700 rounded-lg">
        <p>✅ Score: <b>${data.score}</b> / ${data.total}</p>
        <p>📉 Weak Topics: ${data.wrong_topics.join(", ") || "None 🎉"}</p>
      </div>
    `;
  } catch (err) {
    console.error("Error submitting quiz:", err);
    box.innerHTML = `<div class="text-red-400">⚠️ Failed to submit quiz.</div>`;
  }
}

// Attach events
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("gen-btn").addEventListener("click", generateQuiz);
  document.getElementById("submit-btn").addEventListener("click", submitQuiz);
  loadNotes();
});
