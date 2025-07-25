const chatbotToggler = document.querySelector(".chatbot-toggler");
const closeBtn = document.querySelector(".close-btn");
const chatbox = document.querySelector(".chatbox");
const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");
const micBtn = document.getElementById("mic-btn");
const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.lang = "de-DE"; // Use "en-US" for English
recognition.interimResults = false;
recognition.maxAlternatives = 1;

function setInputState(enabled) {
  chatInput.disabled = !enabled;
  micBtn.style.pointerEvents = enabled ? "auto" : "none";
  micBtn.style.opacity = enabled ? "1" : "0.5";
  sendChatBtn.style.pointerEvents = enabled ? "auto" : "none";
  sendChatBtn.style.opacity = enabled ? "1" : "0.5";
}

let userMessage = null; // Variable to store user's message
const inputInitHeight = chatInput.scrollHeight;

// API configuration
const API_KEY = "PASTE-YOUR-API-KEY"; // Your API key here
// const API_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${API_KEY}`;
const API_URL = window.location.origin + "/chat";

let sessionId = null;

const createChatLi = (message, className) => {
  // Create a chat <li> element with passed message and className
  const chatLi = document.createElement("li");
  chatLi.classList.add("chat", `${className}`);
  let chatContent =
    className === "outgoing"
      ? `<p></p>`
      : `<span class="material-symbols-outlined" translate="no">smart_toy</span><p></p>`;
  chatLi.innerHTML = chatContent;
  chatLi.querySelector("p").textContent = message;
  return chatLi; // return chat <li> element
};

const generateResponse = async (chatElement) => {
  const messageElement = chatElement.querySelector("p");

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        message: userMessage,
      }),
    });

    const data = await response.json();

    // Save session ID for continuity
    if (data.session_id) {
      sessionId = data.session_id;
    }

    const cleanedReply = (data.reply || "Keine Antwort erhalten.")
      .replace(/【\d+:\d+†[^】]*】/gu, "")
      .replace(/\s*\n\s*/g, "\n") // trim whitespace around line breaks
      .trim();
    messageElement.textContent = cleanedReply.trim();
  } catch (error) {
    messageElement.classList.add("error");
    messageElement.textContent = "Fehler: " + error.message;
  } finally {
    chatbox.scrollTo(0, chatbox.scrollHeight);
    setInputState(true); // Re-enable input after response
    chatInput.focus();
  }
};

const handleChat = () => {
  userMessage = chatInput.value.trim(); // Get user entered message and remove extra whitespace
  if (!userMessage) return;

  setInputState(false);

  // Clear the input textarea and set its height to default
  chatInput.value = "";
  chatInput.style.height = `${inputInitHeight}px`;

  // Append the user's message to the chatbox
  chatbox.appendChild(createChatLi(userMessage, "outgoing"));
  chatbox.scrollTo(0, chatbox.scrollHeight);

  setTimeout(() => {
    // Display "Thinking..." message while waiting for the response
    const incomingChatLi = createChatLi("Denken...", "incoming");
    chatbox.appendChild(incomingChatLi);
    chatbox.scrollTo(0, chatbox.scrollHeight);
    generateResponse(incomingChatLi);
  }, 600);
};

chatInput.addEventListener("input", () => {
  // Adjust the height of the input textarea based on its content
  chatInput.style.height = `${inputInitHeight}px`;
  chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", (e) => {
  // If Enter key is pressed without Shift key and the window
  // width is greater than 800px, handle the chat
  if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
    e.preventDefault();
    handleChat();
  }
});

micBtn.addEventListener("click", () => {
  recognition.start();
  micBtn.classList.add("mic-active");
});

recognition.onend = () => {
  micBtn.classList.remove("mic-active");
};

recognition.onresult = (event) => {
  const voiceText = event.results[0][0].transcript;
  chatInput.value = voiceText;
  chatInput.dispatchEvent(new Event("input"));
  handleChat();
};

recognition.onerror = (event) => {
  console.error("Spracherkennungsfehler:", event.error);
  micBtn.classList.remove("mic-active");
};

sendChatBtn.addEventListener("click", handleChat);

closeBtn.addEventListener("click", () =>
  document.body.classList.remove("show-chatbot")
);
chatbotToggler.addEventListener("click", () =>
  document.body.classList.toggle("show-chatbot")
);
micBtn.addEventListener("click", () => {
  recognition.start();
});
