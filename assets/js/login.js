import { bounceIfAuthenticated, clearMessage, getQueryParam, getRedirectTarget, redirectTo, requireConfigured, setMessage, signIn } from "./auth-client.js";

const form = document.querySelector("[data-login-form]");
const message = document.querySelector("[data-form-message]");

async function init() {
    if (!form) {
        return;
    }

    await bounceIfAuthenticated();
    requireConfigured(message);

    if (getQueryParam("verified") === "1") {
        setMessage(message, "success", "Your email has been verified. Sign in to continue.");
        return;
    }

    const verificationState = getQueryParam("verification");
    if (verificationState === "expired") {
        setMessage(message, "warning", "Your verification link expired. Register again or request a new verification email.");
    } else if (verificationState === "invalid") {
        setMessage(message, "error", "That verification link is invalid.");
    }
}

form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage(message);

    if (!requireConfigured(message)) {
        return;
    }

    const formData = new FormData(form);
    const email = String(formData.get("email") ?? "").trim();
    const password = String(formData.get("password") ?? "");

    if (!email || !password) {
        setMessage(message, "error", "Enter both your email and password.");
        return;
    }

    const button = form.querySelector("button[type='submit']");
    if (button) {
        button.disabled = true;
    }

    try {
        await signIn({
            email,
            password
        });

        redirectTo(getRedirectTarget("account.html"));
    } catch (error) {
        setMessage(message, "error", error.message);
    } finally {
        if (button) {
            button.disabled = false;
        }
    }
});

void init().catch((error) => {
    setMessage(message, "error", error.message);
});
