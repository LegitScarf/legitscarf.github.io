import { fetchStatus, getProduct, requireConfigured, setMessage } from "./auth-client.js";

const headline = document.querySelector("[data-access-headline]");
const copy = document.querySelector("[data-access-copy]");
const actions = document.querySelector("[data-access-actions]");
const message = document.querySelector("[data-access-message]");

function renderActions(html) {
    actions.innerHTML = html;
}

async function init() {
    if (!requireConfigured(message)) {
        return;
    }

    const url = new URL(window.location.href);
    const productCode = url.searchParams.get("product") ?? "optitrade";
    const product = getProduct(productCode);

    if (!product) {
        setMessage(message, "error", "Unknown product requested.");
        return;
    }

    headline.textContent = `Accessing ${product.name}`;
    copy.textContent = "Checking your account status and subscription entitlement now.";

    try {
        const status = await fetchStatus();

        if (status.state === "active") {
            copy.textContent = `${product.name} is unlocked for your account. Redirecting to the app now.`;
            renderActions(`<a class="portal-button" href="${product.appUrl}">Open ${product.name}</a>`);
            window.setTimeout(() => {
                window.location.href = product.appUrl;
            }, 1200);
            return;
        }

        const nextStepMap = {
            guest: {
                copy: "Please sign in or create your account first.",
                actions: `<a class="portal-button" href="login.html?redirect=access.html%3Fproduct%3D${productCode}">Sign In</a>
                    <a class="portal-button-secondary" href="register.html?redirect=access.html%3Fproduct%3D${productCode}">Register</a>`
            },
            registered_unverified: {
                copy: "Verify your email address first, then return here to continue.",
                actions: "<a class=\"portal-button\" href=\"login.html\">Sign In Again</a>"
            },
            verified_pending_approval: {
                copy: "Your account is verified and waiting for manual approval from NexAlpha.",
                actions: "<a class=\"portal-button-secondary\" href=\"account.html\">View Account</a>"
            },
            approved_unsubscribed: {
                copy: "Your account is approved. Start the Rs 500/month plan to unlock both apps.",
                actions: "<a class=\"portal-button\" href=\"account.html\">Subscribe Now</a>"
            },
            approved_subscription_pending: {
                copy: "Authorization payment is still being confirmed. Access unlocks after the Razorpay webhook updates your subscription.",
                actions: "<a class=\"portal-button-secondary\" href=\"account.html\">Refresh Status</a>"
            },
            suspended: {
                copy: "Your account is currently suspended because billing is inactive or access was paused.",
                actions: "<a class=\"portal-button\" href=\"account.html\">Manage Billing</a>"
            }
        };

        const view = nextStepMap[status.state] ?? nextStepMap.guest;
        copy.textContent = view.copy;
        renderActions(view.actions);
    } catch (error) {
        setMessage(message, "error", error.message);
    }
}

void init().catch((error) => {
    setMessage(message, "error", error.message);
});
