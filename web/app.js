document.addEventListener("DOMContentLoaded", () => {
    // Use relative paths. This allows the frontend to work
    // from any domain, as it assumes the API is at the same origin
    const API_URL = "";
    let token = localStorage.getItem("accessToken");

    const authSection = document.getElementById("auth-section");
    const itemsSection = document.getElementById("items-section");
    const authStatus = document.getElementById("auth-status");
    const itemsList = document.getElementById("items-list");

    const showView = () => {
        if (token) {
            authSection.classList.add("hidden");
            itemsSection.classList.remove("hidden");
            fetchItems();
        } else {
            authSection.classList.remove("hidden");
            itemsSection.classList.add("hidden");
        }
    };

    // Event Listeners
    document.getElementById("register-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("register-email").value;
        const password = document.getElementById("register-password").value;
        try {
            const res = await fetch(`${API_URL}/auth/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });
            if (!res.ok) throw new Error("Registration failed.");
            authStatus.textContent = "Registration successful! Please log in.";
        } catch (err) {
            authStatus.textContent = err.message;
        }
    });

    document.getElementById("login-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("login-email").value;
        const password = document.getElementById("login-password").value;
        // OAuth2 Password Flow requires form-encoded data
        const body = new URLSearchParams({ username: email, password });
        try {
            const res = await fetch(`${API_URL}/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body,
            });
            if (!res.ok) throw new Error("Invalid credentials.");
            const data = await res.json();
            token = data.access_token;
            localStorage.setItem("accessToken", token);
            authStatus.textContent = "";
            showView();
        } catch (err) {
            authStatus.textContent = err.message;
        }
    });

    document.getElementById("logout-btn").addEventListener("click", () => {
        token = null;
        localStorage.removeItem("accessToken");
        itemsList.innerHTML = "";
        showView();
    });

    document.getElementById("create-item-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("item-name").value;
        const description = document.getElementById("item-desc").value;
        try {
            await apiFetch("/items/", {
                method: "POST",
                body: JSON.stringify({ name, description }),
            });
            document.getElementById("item-name").value = "";
            document.getElementById("item-desc").value = "";
            fetchItems();
        } catch (err) {
            console.error("Failed to create item:", err);
        }
    });

    // API & UI Functions
    const apiFetch = async (endpoint, options = {}) => {
        const headers = {
            "Content-Type": "application/json",
            ...options.headers,
        };
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }
        const res = await fetch(`${API_URL}${endpoint}`, { ...options, headers });
        if (!res.ok) {
            if (res.status === 401) { // Token expired or invalid
                token = null;
                localStorage.removeItem("accessToken");
                showView();
            }
            throw new Error(`API error: ${res.statusText}`);
        }
        if (res.status === 204) return null; // No Content
        return res.json();
    };

    const fetchItems = async () => {
        try {
            const items = await apiFetch("/items/");
            itemsList.innerHTML = ""; // Clear existing list
            items.forEach(item => {
                const li = document.createElement("li");
                li.innerHTML = `<span>${item.name} - ${item.description || 'No description'}</span>`;
                const deleteBtn = document.createElement("button");
                deleteBtn.textContent = "Delete";
                deleteBtn.onclick = async () => {
                    await apiFetch(`/items/${item.id}`, { method: "DELETE" });
                    fetchItems();
                };
                li.appendChild(deleteBtn);
                itemsList.appendChild(li);
            });
        } catch (err) {
            console.error("Failed to fetch items:", err);
        }
    };

    showView(); // Initial view setup
});