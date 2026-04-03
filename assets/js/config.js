window.NEXALPHA_CONFIG = Object.freeze({
    // Optional: leave blank when FastAPI serves both the frontend and API on the same origin.
    appBaseUrl: "",
    apiBaseUrl: "",
    billing: {
        amountInr: 500,
        interval: "month"
    },
    products: {
        optitrade: {
            name: "OptiTrade",
            appUrl: "https://optitrade-nexalpha.streamlit.app/"
        },
        bharatalpha: {
            name: "BharatAlpha",
            appUrl: "https://bharatalpha-nexalpha.streamlit.app/"
        }
    }
});
