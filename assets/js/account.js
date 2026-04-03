import {
    createSubscription,
    fetchStatus,
    getConfig,
    renderUserEmail,
    requireAuthPage,
    setMessage,
    signOut
} from "./auth-client.js";

const summary = document.querySelector("[data-account-summary]");
const accountState = document.querySelector("[data-account-state]");
const accountMessage = document.querySelector("[data-account-message]");
const accountActions = document.querySelector("[data-account-actions]");
const emailNode = document.querySelector("[data-user-email]");
const signOutButton = document.querySelector("[data-sign-out]");

function renderActionLink(href, label, variant = "portal-button") {
    return `<a class="${variant}" href="${href}">${label}</a>`;
}

function renderSummary(status) {
    const config = getConfig();
    const currentEnd = status.subscription?.currentPeriodEnd
        ? new Date(status.subscription.currentPeriodEnd).toLocaleDateString()
        : "Not scheduled";

    summary.innerHTML = `
        <div class="kv-card">
            <span>Access State</span>
            <strong>${status.state.replaceAll("_", " ")}</strong>
        </div>
        <div class="kv-card">
            <span>Approval</span>
            <strong>${status.approvalStatus ?? "pending"}</strong>
        </div>
        <div class="kv-card">
            <span>Subscription</span>
            <strong>${status.subscription?.status ?? "inactive"}</strong>
        </div>
        <div class="kv-card">
            <span>Plan</span>
            <strong>INR ${config.billing.amountInr}/${config.billing.interval}</strong>
        </div>
        <div class="kv-card">
            <span>Renews / Ends</span>
            <strong>${currentEnd}</strong>
        </div>
    `;
}

function renderState(status) {
    const stateMap = {
        guest: {
            tone: "warning",
            label: "Guest",
            copy: "Sign in to unlock your account dashboard and continue the onboarding flow."
        },
        registered_unverified: {
            tone: "warning",
            label: "Verify Email",
            copy: "Your account exists, but email verification is still pending."
        },
        verified_pending_approval: {
            tone: "info",
            label: "Approval Queue",
            copy: "Your email is verified. The next step is manual approval from NexAlpha before billing can start."
        },
        approved_unsubscribed: {
            tone: "warning",
            label: "Subscription Required",
            copy: "You are approved. Start the Rs 500/month subscription to unlock both products."
        },
        approved_subscription_pending: {
            tone: "info",
            label: "Payment Pending",
            copy: "Your checkout has started. Access will unlock after Razorpay confirms the authorization payment."
        },
        active: {
            tone: "success",
            label: "Active Access",
            copy: "Your account is fully active and both products are unlocked."
        },
        suspended: {
            tone: "danger",
            label: "Suspended",
            copy: "Access is currently paused. Renew the subscription or contact NexAlpha support."
        }
    };

    const view = stateMap[status.state] ?? stateMap.guest;
    accountState.className = `status-badge ${view.tone}`;
    accountState.textContent = view.label;
    setMessage(accountMessage, view.tone === "danger" ? "error" : view.tone, view.copy);
}

function renderActions(status) {
    const products = Object.entries(getConfig().products ?? {});

    if (status.state === "active") {
        accountActions.innerHTML = products.map(([code, product], index) => {
            const variant = index === 0 ? "portal-button" : "portal-button-secondary";
            return renderActionLink(`access.html?product=${code}`, `Launch ${product.name}`, variant);
        }).join("");
        return;
    }

    if (status.state === "approved_unsubscribed" || status.state === "suspended") {
        accountActions.innerHTML = `
            <button class="portal-button" type="button" data-start-subscription>
                Subscribe Rs 500/Month
            </button>
            ${renderActionLink("index.html#products", "Review Products", "portal-button-secondary")}
        `;

        const subscribeButton = accountActions.querySelector("[data-start-subscription]");
        subscribeButton?.addEventListener("click", async () => {
            subscribeButton.disabled = true;
            try {
                const payload = await createSubscription();
                if (payload.checkoutUrl) {
                    window.location.href = payload.checkoutUrl;
                    return;
                }

                setMessage(
                    accountMessage,
                    "info",
                    "Subscription was created, but no checkout URL was returned. Check your Razorpay plan setup."
                );
            } catch (error) {
                setMessage(accountMessage, "error", error.message);
            } finally {
                subscribeButton.disabled = false;
            }
        });
        return;
    }

    if (status.state === "verified_pending_approval") {
        accountActions.innerHTML = renderActionLink(
            "mailto:hello@nexalpha.in?subject=NexAlpha%20Approval%20Request",
            "Contact NexAlpha",
            "portal-button-secondary"
        );
        return;
    }

    if (status.state === "registered_unverified") {
        accountActions.innerHTML = renderActionLink("login.html", "Sign In Again", "portal-button-secondary");
        return;
    }

    accountActions.innerHTML = renderActionLink("login.html", "Sign In", "portal-button");
}

async function init() {
    const session = await requireAuthPage(accountMessage);
    if (!session) {
        return;
    }

    renderUserEmail(emailNode, session.user.email);

    try {
        const status = await fetchStatus();
        renderSummary(status);
        renderState(status);
        renderActions(status);
    } catch (error) {
        setMessage(accountMessage, "error", error.message);
    }
}

signOutButton?.addEventListener("click", async () => {
    await signOut();
    window.location.href = "login.html";
});

void init().catch((error) => {
    setMessage(accountMessage, "error", error.message);
});
