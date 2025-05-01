document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.createElement("button");
    toggleBtn.textContent = "AI Help";
    toggleBtn.id = "chat-toggle-btn";
    document.body.appendChild(toggleBtn);

    const chatBox = document.createElement("div");
    chatBox.id = "chat-box";
    chatBox.innerHTML = `
        <div id="chat-messages"></div>
        <input type="text" id="chat-input" placeholder="Ask something..." />
        <button id="chat-send">Send</button>
    `;
    document.body.appendChild(chatBox);
    chatBox.style.display = "none";

    toggleBtn.addEventListener("click", () => {
        chatBox.style.display = chatBox.style.display === "none" ? "block" : "none";
    });

    document.getElementById("chat-send").addEventListener("click", () => {
        const message = document.getElementById("chat-input").value;
        if (!message) return;

        const msgContainer = document.getElementById("chat-messages");
        msgContainer.innerHTML += `<div class="user-msg">${message}</div>`;

        fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message }),
        })
        .then((res) => res.json())
        .then((data) => {
            if (data.response) {
                msgContainer.innerHTML += `<div class="ai-msg">${data.response}</div>`;
            } else {
                msgContainer.innerHTML += `<div class="error-msg">Error: ${data.error}</div>`;
            }
        });

        document.getElementById("chat-input").value = "";
    });
});
