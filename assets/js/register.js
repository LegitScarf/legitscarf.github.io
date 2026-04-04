import { bounceIfAuthenticated, clearMessage, redirectTo, registerAccount, requireConfigured, setMessage } from "./auth-client.js";

const form = document.querySelector("[data-register-form]");
const message = document.querySelector("[data-form-message]");
const helper = document.querySelector("[data-register-helper]");

function clearHelper() {
    if (helper) {
        helper.innerHTML = "";
    }
}

async function init() {
    if (!form) {
        return;
    }

    await bounceIfAuthenticated();
    requireConfigured(message);
}

form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage(message);
    clearHelper();

    if (!requireConfigured(message)) {
        return;
    }

    const formData = new FormData(form);
    const fullName = String(formData.get("full_name") ?? "").trim();
    const email = String(formData.get("email") ?? "").trim();
    const password = String(formData.get("password") ?? "");
    const confirmPassword = String(formData.get("confirm_password") ?? "");

    if (!fullName || !email || !password) {
        setMessage(message, "error", "Please complete all required fields.");
        return;
    }

    if (password.length < 8) {
        setMessage(message, "error", "Use a password with at least 8 characters.");
        return;
    }

    if (password !== confirmPassword) {
        setMessage(message, "error", "Passwords do not match.");
        return;
    }

    const button = form.querySelector("button[type='submit']");
    const defaultButtonLabel = button?.textContent ?? "Create Account";
    if (button) {
        button.disabled = true;
        button.textContent = "Creating...";
    }

    try {
        const payload = await registerAccount({
            full_name: fullName,
            email,
            password
        });

        if (payload.emailDelivery === "preview" && payload.verificationUrl && helper) {
            helper.innerHTML = `
                <a class="portal-button" href="${payload.verificationUrl}">Verify Email Now</a>
                <a class="portal-button-secondary" href="login.html">Go To Sign In</a>
            `;
        } else if (helper) {
            helper.innerHTML = `<a class="portal-button-secondary" href="login.html">Go To Sign In</a>`;
        }

        setMessage(
            message,
            "success",
            payload.emailDelivery === "preview"
                ? `Account created for ${email}. This backend is running without SMTP, so use the verification link below before signing in.`
                : `Account created for ${email}. Check your inbox, verify your email, then sign in to continue.`
        );

        if (payload.emailDelivery !== "preview") {
            window.setTimeout(() => {
                redirectTo("login.html");
            }, 2400);
        }
    } catch (error) {
        setMessage(message, "error", error.message);
    } finally {
        if (button) {
            button.disabled = false;
            button.textContent = defaultButtonLabel;
        }
    }
});

void init().catch((error) => {
    setMessage(message, "error", error.message);
});
