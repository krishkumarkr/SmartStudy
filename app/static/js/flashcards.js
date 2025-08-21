document.addEventListener("DOMContentLoaded", () => {
    const noteSelect = document.getElementById("note-select");
    const countInput = document.getElementById("count-input");
    const genBtn = document.getElementById("gen-btn");
    const flashMsg = document.getElementById("flash-msg");
    const cardsGrid = document.getElementById("cards");

    // Load notes for dropdown
    fetch("/api/notes")
        .then(r => r.json())
        .then(notes => {
            noteSelect.innerHTML = `<option value="">-- choose a note --</option>`;
            notes.forEach(n => {
                const opt = document.createElement("option");
                opt.value = n.id;
                opt.textContent = n.title;
                noteSelect.appendChild(opt);
            });
        });

    // When note changes, load existing flashcards
    noteSelect.addEventListener("change", () => {
        const id = noteSelect.value;
        cardsGrid.innerHTML = "";
        flashMsg.textContent = "";
        if (!id) return;
        fetch(`/api/flashcards?note_id=${id}`)
            .then(r => r.json())
            .then(data => {
                if (data.ok) {
                    renderCards(data.cards);
                    flashMsg.textContent = data.cards.length ? `Loaded ${data.cards.length} cards.` : `No cards yet.`;
                } else {
                    flashMsg.textContent = data.msg || "Failed to load flashcards.";
                }
            });
    });

    // Generate flashcards
    genBtn.addEventListener("click", () => {
        const note_id = Number(noteSelect.value);
        if (!note_id) {
            flashMsg.textContent = "Please choose a note.";
            return;
        }
        const count = Number(countInput.value) || 8;

        genBtn.disabled = true;
        genBtn.textContent = "Generating…";
        flashMsg.textContent = "Thinking…";

        fetch("/flashcards/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ note_id, count })
        })
            .then(r => r.json())
            .then(data => {
                if (!data.ok) {
                    flashMsg.textContent = data.msg || "Failed to generate.";
                    return;
                }
                flashMsg.textContent = data.msg;
                renderCards(data.cards);
            })
            .catch(() => {
                flashMsg.textContent = "Error generating flashcards.";
            })
            .finally(() => {
                setTimeout(() => {
                    genBtn.disabled = false;
                    genBtn.textContent = "Generate";
                }, 700);
            });
    });

    // Render function: flip cards
    function renderCards(cards) {
        cardsGrid.innerHTML = "";
        cards.forEach(c => {
            const wrapper = document.createElement("div");
            wrapper.className = "group perspective w-full ";

            wrapper.innerHTML = `
                <div class="flip-inner relative h-72 preserve-3d cursor-pointer">
                    <div class="absolute inset-0 bg-blue-50 border rounded-xl p-3 backface-hidden flex items-center overflow-auto">
                    <p class="text-sm text-gray-900 font-medium break-words">${escapeHTML(c.question || c.question_text || "")}</p>
                    </div>
                    <div class="absolute inset-0 bg-emerald-50 border rounded-xl p-3 rotate-y-180 backface-hidden flex items-center overflow-auto">
                    <p class="text-gray-900 text-sm break-words">${escapeHTML(c.answer || c.answer_text || "")}</p>
                    </div>
                </div>
            `;
            cardsGrid.appendChild(wrapper);
        });
    }

    function escapeHTML(s) {
        return (s || "").replace(/[&<>"']/g, m => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
        }[m]));
    }
});
