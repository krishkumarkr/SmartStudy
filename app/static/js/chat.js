document.addEventListener("DOMContentLoaded", () => {
  const chatBox = document.getElementById("chat-box");
  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-input");

  // function scrollToBottom() {
  //   chatBox.scrollTop = chatBox.scrollHeight;
  // }

  function scrollToBottom() {
    chatBox.scrollTo({
        top: chatBox.scrollHeight,
        behavior: "smooth"
    });
  }

  function addMessage(text, type) {
    const msg = document.createElement("div");
    msg.classList.add(type === "user" ? "user-msg" : "bot-msg");
    msg.textContent = text;
    chatBox.prepend(msg); // append at bottom
    scrollToBottom();
  }

  function showTyping() {
    const typingDiv = document.createElement("div");
    typingDiv.classList.add("bot-msg");
    typingDiv.id = "typing-indicator";
    typingDiv.innerHTML = `<span class="typing"></span><span class="typing"></span><span class="typing"></span>`;
    chatBox.prepend(typingDiv); // append at bottom
    scrollToBottom();
  }

  function removeTyping() {
    const typingDiv = document.getElementById("typing-indicator");
    if (typingDiv) typingDiv.remove();
  }

  function showPostLoginOptions() {
    const optionsDiv = document.createElement("div");
    // Center align buttons and add spacing from chat input
    optionsDiv.classList.add("flex", "justify-center", "space-x-4", "mb-2", "mt-2");

    const homeBtn = document.createElement("button");
    homeBtn.textContent = "Home";
    homeBtn.classList.add("px-3", "py-1", "bg-gray-500", "text-white", "rounded-lg", "hover:bg-green-700");
    homeBtn.addEventListener("click", () => window.location.href = "/dashboard");

    const logoutBtn = document.createElement("button");
    logoutBtn.textContent = "Logout";
    logoutBtn.classList.add("px-3", "py-1", "bg-gray-600", "text-white", "rounded-lg", "hover:bg-red-900");
    logoutBtn.addEventListener("click", () => {
      fetch("/logout")
        .then(res => res.json())
        .then(data => {
          alert(data.reply);
          window.location.reload();
        });
      scrollToBottom();
    });

    optionsDiv.prepend(homeBtn);
    optionsDiv.prepend(logoutBtn);
    chatBox.prepend(optionsDiv);
    scrollToBottom();
  }

  function sendMessageToBackend(message) {
    // Delay 0.2s before showing typing animation
    setTimeout(() => {
        showTyping(); // show the animated dots

        // Delay a bit more for the bot to "type" before showing response
        setTimeout(() => {
            fetch("/auth_chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message })
            })
            .then(res => res.json())
            .then(data => {
                removeTyping();
                addMessage(data.reply, "bot");

                // Show post-login buttons if applicable
                if (data.reply.includes("✅ You're logged in")) {
                    showPostLoginOptions();
                }
            });
        }, 1000); // bot typing delay
    }, 500); // initial 0.2s delay after user message
  }

  // ---------------- INITIAL LOAD ----------------
  sendMessageToBackend(""); // This will fetch session info and show proper first message

  // Handle form submit
  chatForm.addEventListener("submit", e => {
    e.preventDefault();
    const userMsg = chatInput.value.trim();
    if (!userMsg) return;

    addMessage(userMsg, "user");
    chatInput.value = "";
    sendMessageToBackend(userMsg);
  });
});
