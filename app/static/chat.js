"use strict";


/* =========================================================
   CONFIGURATION
   ========================================================= */

const API_BASE = "/api/v1";

let accessToken = localStorage.getItem("vehicle_service_token");

let sessionId = null;

let websocket = null;


/* =========================================================
   DOM ELEMENTS
   ========================================================= */

const loginScreen =
    document.getElementById("login-screen");

const chatScreen =
    document.getElementById("chat-screen");

const loginForm =
    document.getElementById("login-form");

const loginButton =
    document.getElementById("login-button");

const loginError =
    document.getElementById("login-error");

const logoutButton =
    document.getElementById("logout-button");

const chatMessages =
    document.getElementById("chat-messages");

const chatForm =
    document.getElementById("chat-form");

const questionInput =
    document.getElementById("question-input");

const sendButton =
    document.getElementById("send-button");

const loadingIndicator =
    document.getElementById("loading-indicator");

const chatError =
    document.getElementById("chat-error");

const connectionStatus =
    document.getElementById("connection-status");

const statusDot =
    document.getElementById("status-dot");


/* =========================================================
   PAGE INITIALIZATION
   ========================================================= */

document.addEventListener("DOMContentLoaded", async () => {

    if (accessToken) {

        const valid =
            await verifyToken();

        if (valid) {

            showChatScreen();

            await createSession();

            return;
        }

        clearAuthentication();
    }

    showLoginScreen();
});


/* =========================================================
   LOGIN
   ========================================================= */

loginForm.addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();

        clearLoginError();

        const email =
            document
                .getElementById("email")
                .value
                .trim();

        const password =
            document
                .getElementById("password")
                .value;

        if (!email || !password) {

            showLoginError(
                "Please enter your email and password."
            );

            return;
        }

        setLoginLoading(true);

        try {

            /*
             * FastAPI OAuth2PasswordRequestForm expects
             * application/x-www-form-urlencoded data.
             */

            const formData =
                new URLSearchParams();

            formData.append(
                "username",
                email
            );

            formData.append(
                "password",
                password
            );

            const response =
                await fetch(
                    `${API_BASE}/auth/login`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/x-www-form-urlencoded"
                        },

                        body: formData
                    }
                );

            const data =
                await response.json();

            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Login failed."
                );
            }

            if (!data.access_token) {

                throw new Error(
                    "Login succeeded but no access token was returned."
                );
            }

            accessToken =
                data.access_token;

            localStorage.setItem(
                "vehicle_service_token",
                accessToken
            );

            showChatScreen();

            const created =
                await createSession();

            if (!created) {

                showChatError(
                    "Login successful, but chat session could not be created."
                );
            }

        } catch (error) {

            console.error(
                "Login error:",
                error
            );

            showLoginError(
                error.message ||
                "Unable to login."
            );

        } finally {

            setLoginLoading(false);
        }
    }
);


/* =========================================================
   VERIFY TOKEN
   ========================================================= */

async function verifyToken() {

    try {

        const response =
            await fetch(
                `${API_BASE}/auth/me`,
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${accessToken}`
                    }
                }
            );

        return response.ok;

    } catch (error) {

        console.error(
            "Token verification error:",
            error
        );

        return false;
    }
}


/* =========================================================
   CREATE CHAT SESSION
   ========================================================= */

async function createSession() {

    try {

        setConnectionStatus(
            "connecting",
            "Creating session..."
        );

        const response =
            await fetch(
                `${API_BASE}/chat/sessions`,
                {
                    method: "POST",

                    headers: {
                        "Authorization":
                            `Bearer ${accessToken}`
                    }
                }
            );

        if (response.status === 401) {

            handleAuthenticationFailure();

            return false;
        }

        const data =
            await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Could not create chat session."
            );
        }

        sessionId =
            data.session_id;

        if (!sessionId) {

            throw new Error(
                "Server did not return a session ID."
            );
        }

        connectWebSocket();

        return true;

    } catch (error) {

        console.error(
            "Session creation error:",
            error
        );

        setConnectionStatus(
            "offline",
            "Session error"
        );

        showChatError(
            error.message ||
            "Could not create chat session."
        );

        return false;
    }
}


/* =========================================================
   WEBSOCKET CONNECTION
   ========================================================= */

function connectWebSocket() {

    if (!sessionId || !accessToken) {

        return;
    }

    closeWebSocket();

    setConnectionStatus(
        "connecting",
        "Connecting..."
    );

    const protocol =
        window.location.protocol === "https:"
            ? "wss:"
            : "ws:";

    const host =
        window.location.host;

    const websocketUrl =
        `${protocol}//${host}/ws/chat/${sessionId}` +
        `?token=${encodeURIComponent(accessToken)}`;

    console.log(
        "Connecting to WebSocket:",
        websocketUrl.replace(
            accessToken,
            "[TOKEN]"
        )
    );

    websocket =
        new WebSocket(
            websocketUrl
        );


    websocket.onopen = () => {

        console.log(
            "WebSocket connected."
        );

        setConnectionStatus(
            "online",
            "Connected"
        );

        clearChatError();
    };


    websocket.onmessage = (event) => {

        try {

            const data =
                JSON.parse(event.data);

            handleWebSocketMessage(data);

        } catch (error) {

            console.error(
                "Invalid WebSocket message:",
                error
            );

            hideLoading();

            showChatError(
                "Received an invalid response from the server."
            );
        }
    };


    websocket.onerror = (error) => {

        console.error(
            "WebSocket error:",
            error
        );

        hideLoading();

        setConnectionStatus(
            "offline",
            "Connection error"
        );
    };


    websocket.onclose = (event) => {

        console.log(
            "WebSocket closed:",
            event.code,
            event.reason
        );

        hideLoading();

        if (event.code === 1008) {

            setConnectionStatus(
                "offline",
                "Authentication failed"
            );

            showChatError(
                "Your session is no longer valid. Please login again."
            );

            return;
        }

        setConnectionStatus(
            "offline",
            "Disconnected"
        );
    };
}


/* =========================================================
   WEBSOCKET MESSAGE HANDLER
   ========================================================= */

function handleWebSocketMessage(data) {

    switch (data.type) {

        case "connected":

            setConnectionStatus(
                "online",
                "Connected"
            );

            break;


        case "message":

            hideLoading();

            addAssistantMessage(
                data.answer,
                data.sources || [],
                Boolean(data.safety_flag)
            );

            break;


        case "error":

            hideLoading();

            showChatError(
                data.message ||
                "An error occurred while processing your message."
            );

            break;


        default:

            console.warn(
                "Unknown WebSocket message type:",
                data
            );
    }
}


/* =========================================================
   SEND CHAT MESSAGE
   ========================================================= */

chatForm.addEventListener(
    "submit",
    (event) => {

        event.preventDefault();

        sendMessage();
    }
);


async function sendMessage() {

    const question =
        questionInput.value.trim();

    if (!question) {

        return;
    }

    if (!websocket ||
        websocket.readyState !== WebSocket.OPEN) {

        showChatError(
            "Chat connection is not available. Please reconnect."
        );

        return;
    }

    clearChatError();

    addUserMessage(question);

    questionInput.value = "";

    autoResizeTextarea();

    showLoading();

    sendButton.disabled = true;

    try {

        websocket.send(
            JSON.stringify({
                question: question
            })
        );

    } catch (error) {

        console.error(
            "Send error:",
            error
        );

        hideLoading();

        showChatError(
            "Unable to send your message."
        );

    } finally {

        sendButton.disabled = false;

        questionInput.focus();
    }
}


/* =========================================================
   USER MESSAGE
   ========================================================= */

function addUserMessage(question) {

    const message =
        document.createElement("div");

    message.className =
        "message user-message";

    message.innerHTML = `
        <div class="message-avatar">
            👤
        </div>

        <div class="message-content">

            <div class="message-name">
                You
            </div>

            <div class="message-bubble"></div>

        </div>
    `;

    const bubble =
        message.querySelector(
            ".message-bubble"
        );

    bubble.textContent =
        question;

    chatMessages.appendChild(
        message
    );

    scrollToBottom();
}


/* =========================================================
   ASSISTANT MESSAGE
   ========================================================= */

function addAssistantMessage(
    answer,
    sources,
    safetyFlag
) {

    const message =
        document.createElement("div");

    message.className =
        "message assistant-message";

    const content =
        document.createElement("div");

    content.className =
        "message-content";


    const avatar =
        document.createElement("div");

    avatar.className =
        "message-avatar";

    avatar.textContent =
        "🤖";


    const name =
        document.createElement("div");

    name.className =
        "message-name";

    name.textContent =
        "Vehicle Service AI";


    const bubble =
        document.createElement("div");

    bubble.className =
        "message-bubble";


    /*
     * Use textContent for the actual AI answer.
     * This prevents HTML injection from model output.
     */

    const answerParagraph =
        document.createElement("p");

    answerParagraph.textContent =
        answer;

    bubble.appendChild(
        answerParagraph
    );


    /*
     * Safety warning
     */

    if (safetyFlag) {

        const warning =
            document.createElement("div");

        warning.className =
            "safety-warning";

        const strong =
            document.createElement("strong");

        strong.textContent =
            "⚠ Safety Warning";

        const warningText =
            document.createElement("div");

        warningText.textContent =
            "This response concerns a potentially dangerous vehicle condition. Do not continue driving if the vehicle may be unsafe. Contact a qualified technician or roadside assistance.";

        warning.appendChild(
            strong
        );

        warning.appendChild(
            warningText
        );

        bubble.appendChild(
            warning
        );
    }


    /*
     * Source references
     */

    if (Array.isArray(sources) &&
        sources.length > 0) {

        const sourcesContainer =
            document.createElement("div");

        sourcesContainer.className =
            "sources";


        const title =
            document.createElement("div");

        title.className =
            "sources-title";

        title.textContent =
            "📚 Sources";

        sourcesContainer.appendChild(
            title
        );


        sources.forEach(
            (source) => {

                const sourceItem =
                    document.createElement("div");

                sourceItem.className =
                    "source-item";


                let text =
                    source.filename ||
                    "Approved knowledge document";


                if (
                    source.page !== null &&
                    source.page !== undefined
                ) {

                    text +=
                        ` — Page ${source.page}`;
                }


                if (
                    source.score !== null &&
                    source.score !== undefined
                ) {

                    const score =
                        Number(source.score);

                    if (!Number.isNaN(score)) {

                        text +=
                            ` — Relevance ${score.toFixed(2)}`;
                    }
                }


                sourceItem.textContent =
                    text;

                sourcesContainer.appendChild(
                    sourceItem
                );
            }
        );


        bubble.appendChild(
            sourcesContainer
        );
    }


    content.appendChild(
        name
    );

    content.appendChild(
        bubble
    );

    message.appendChild(
        avatar
    );

    message.appendChild(
        content
    );

    chatMessages.appendChild(
        message
    );

    scrollToBottom();
}


/* =========================================================
   LOADING
   ========================================================= */

function showLoading() {

    loadingIndicator.classList.remove(
        "hidden"
    );

    scrollToBottom();
}


function hideLoading() {

    loadingIndicator.classList.add(
        "hidden"
    );
}


/* =========================================================
   UI HELPERS
   ========================================================= */

function scrollToBottom() {

    setTimeout(() => {

        chatMessages.scrollTop =
            chatMessages.scrollHeight;

    }, 50);
}


function showLoginScreen() {

    loginScreen.classList.remove(
        "hidden"
    );

    chatScreen.classList.add(
        "hidden"
    );
}


function showChatScreen() {

    loginScreen.classList.add(
        "hidden"
    );

    chatScreen.classList.remove(
        "hidden"
    );
}


function showLoginError(message) {

    loginError.textContent =
        message;

    loginError.classList.remove(
        "hidden"
    );
}


function clearLoginError() {

    loginError.textContent = "";

    loginError.classList.add(
        "hidden"
    );
}


function showChatError(message) {

    chatError.textContent =
        message;

    chatError.classList.remove(
        "hidden"
    );
}


function clearChatError() {

    chatError.textContent = "";

    chatError.classList.add(
        "hidden"
    );
}


function setLoginLoading(isLoading) {

    loginButton.disabled =
        isLoading;

    loginButton.textContent =
        isLoading
            ? "Logging in..."
            : "Login";
}


function setConnectionStatus(
    state,
    text
) {

    connectionStatus.textContent =
        text;

    statusDot.classList.remove(
        "online",
        "offline",
        "connecting"
    );

    statusDot.classList.add(
        state
    );
}


/* =========================================================
   LOGOUT
   ========================================================= */

logoutButton.addEventListener(
    "click",
    () => {

        logout();
    }
);


function logout() {

    closeWebSocket();

    clearAuthentication();

    sessionId = null;

    showLoginScreen();

    clearChatError();

    clearLoginError();

    loginForm.reset();
}


function clearAuthentication() {

    accessToken = null;

    localStorage.removeItem(
        "vehicle_service_token"
    );
}


function handleAuthenticationFailure() {

    hideLoading();

    closeWebSocket();

    clearAuthentication();

    sessionId = null;

    showLoginScreen();

    showLoginError(
        "Your login session has expired. Please login again."
    );
}


/* =========================================================
   WEBSOCKET CLOSE
   ========================================================= */

function closeWebSocket() {

    if (!websocket) {

        return;
    }

    try {

        websocket.close();

    } catch (error) {

        console.error(
            "WebSocket close error:",
            error
        );
    }

    websocket = null;
}


/* =========================================================
   TEXTAREA
   ========================================================= */

questionInput.addEventListener(
    "input",
    autoResizeTextarea
);


function autoResizeTextarea() {

    questionInput.style.height =
        "auto";

    questionInput.style.height =
        Math.min(
            questionInput.scrollHeight,
            130
        ) + "px";
}


questionInput.addEventListener(
    "keydown",
    (event) => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();
        }
    }
);