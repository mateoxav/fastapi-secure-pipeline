document.addEventListener("DOMContentLoaded", () => {
    // Use relative paths. This allows the frontend to work
    // from any domain, as it assumes the API is at the same origin
    const API_URL = "";
    let token = localStorage.getItem("accessToken");

    // DOM Element Selection
    const loginView = document.getElementById("login-view");
    const registerView = document.getElementById("register-view");
    const itemsSection = document.getElementById("items-section");
    
    // Auth forms
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
    
    // Auth status messages
    const loginStatus = document.getElementById("login-status");
    const registerStatus = document.getElementById("register-status");

    // Auth view switching links
    const showRegisterLink = document.getElementById("show-register-link");
    const showLoginLink = document.getElementById("show-login-link");

    // Items section
    const itemsList = document.getElementById("items-list");
    const createItemForm = document.getElementById("create-item-form");
    const logoutBtn = document.getElementById("logout-btn");
    
    // View Management
    const showView = () => {
        // Clear all status messages on view change
        loginStatus.textContent = "";
        registerStatus.textContent = "";

        if (token) {
            // User is logged in
            loginView.classList.add("hidden");
            registerView.classList.add("hidden");
            itemsSection.classList.remove("hidden");
            fetchItems();
        } else {
            // User is logged out, show login view by default
            loginView.classList.remove("hidden");
            registerView.classList.add("hidden");
            itemsSection.classList.add("hidden");
        }
    };

    // Event Listeners

    // View switching logic
    showRegisterLink.addEventListener("click", (e) => {
        e.preventDefault();
        loginView.classList.add("hidden");
        registerView.classList.remove("hidden");
        loginStatus.textContent = "";
    });

    showLoginLink.addEventListener("click", (e) => {
        e.preventDefault();
        loginView.classList.remove("hidden");
        registerView.classList.add("hidden");
        registerStatus.textContent = "";
    });


    // Registration logic
    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("register-email").value;
        const password = document.getElementById("register-password").value;
        const confirmPassword = document.getElementById("register-confirm-password").value;

        // Frontend validation
        if (password !== confirmPassword) {
            setAuthStatus(registerStatus, "Passwords do not match.", "error");
            return;
        }
        if (password.length < 12) {
             setAuthStatus(registerStatus, "Password must be at least 12 characters.", "error");
            return;
        }

        try {
            const res = await fetch(`${API_URL}/auth/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });
            
            if (!res.ok) {
                const errorData = await res.json();
                throw new Error(errorData.detail || "Registration failed.");
            }
            
            // Success
            setAuthStatus(registerStatus, "Registration successful! Please log in.", "success");
            registerForm.reset(); // Clear the form
            
            // Automatically switch to login view
            setTimeout(() => {
                loginView.classList.remove("hidden");
                registerView.classList.add("hidden");
                registerStatus.textContent = "";
                document.getElementById("login-email").value = email; // Pre-fill email
                document.getElementById("login-password").focus();
            }, 2000);

        } catch (err) {
            setAuthStatus(registerStatus, err.message, "error");
        }
    });

    // Login logic
    loginForm.addEventListener("submit", async (e) => {
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

            if (!res.ok) {
                 const errorData = await res.json();
                throw new Error(errorData.detail || "Invalid credentials.");
            }

            const data = await res.json();
            token = data.access_token;
            localStorage.setItem("accessToken", token);
            loginForm.reset(); // Clear the form
            showView();

        } catch (err) {
            setAuthStatus(loginStatus, err.message, "error");
        }
    });

    // Logout logic
    logoutBtn.addEventListener("click", () => {
        token = null;
        localStorage.removeItem("accessToken");
        itemsList.innerHTML = ""; // Clear item list
        showView();
    });

    // Create item logic
    createItemForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const nameInput = document.getElementById("item-name");
        const descInput = document.getElementById("item-desc");
        
        const name = nameInput.value;
        const description = descInput.value;

        try {
            await apiFetch("/items/", {
                method: "POST",
                body: JSON.stringify({ name, description }),
            });
            
            // Clear fields on success
            nameInput.value = "";
            descInput.value = "";
            
            fetchItems(); // Refresh the list
        } catch (err) {
            console.error("Failed to create item:", err);
            // TODO: Show an error to the user
            // e.g., setAuthStatus(someItemErrorElement, err.message, "error");
        }
    });

    // API & UI Functions
    const setAuthStatus = (element, message, type) => {
        element.textContent = message;
        element.className = `auth-view__status auth-view__status--${type}`;
    };

    const renderItems = (items) => {
        itemsList.innerHTML = ""; // Clear existing list
        
        if (items.length === 0) {
            itemsList.innerHTML = '<li class="items-list__empty-message">You have no items. Create one above!</li>';
            return;
        }

        items.forEach(item => {
            // --- SECURE RENDERING (XSS FIX) ---
            // 1. Create all elements
            const li = document.createElement("li");
            li.className = "items-list__item";

            const textDiv = document.createElement("div");
            textDiv.className = "items-list__text-content";
            
            const nameSpan = document.createElement("span");
            nameSpan.className = "items-list__item-name";
            nameSpan.textContent = item.name; // Use .textContent to prevent XSS

            const descSpan = document.createElement("span");
            descSpan.className = "items-list__item-desc";
            descSpan.textContent = item.description || 'No description'; // Use .textContent

            const deleteBtn = document.createElement("button");
            deleteBtn.className = "button button--danger";
            deleteBtn.textContent = "Delete";
            
            // 2. Add event listener for the button
            deleteBtn.onclick = async () => {
                try {
                    await apiFetch(`/items/${item.id}`, { method: "DELETE" });
                    fetchItems(); // Refresh list after delete
                } catch (err) {
                     console.error("Failed to delete item:", err);
                }
            };

            // 3. Append children securely
            textDiv.appendChild(nameSpan);
            textDiv.appendChild(descSpan);
            li.appendChild(textDiv);
            li.appendChild(deleteBtn);
            itemsList.appendChild(li);
        });
    };

    /**
     * Fetches items from the API and calls renderItems
     */
    const fetchItems = async () => {
        try {
            const items = await apiFetch("/items/");
            renderItems(items); // Call the secure render function
        } catch (err) {
            console.error("Failed to fetch items:", err);
            // If token expired, showView() will be called by apiFetch
        }
    };

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
            if (res.status === 401) {
                // Token expired or invalid
                token = null;
                localStorage.removeItem("accessToken");
                console.error("Unauthorized. Logging out.");
                showView(); // Redirect to login
            }
            // Try to parse error details from API
            let errorDetail = `API error: ${res.statusText}`;
            try {
                const errorData = await res.json();
                if(errorData.detail) errorDetail = errorData.detail;
            } catch (e) { /* Ignore if body is not JSON */ }
            
            throw new Error(errorDetail);
        }

        if (res.status === 204) return null; // Handle "No Content" for DELETE
        return res.json();
    };

    // --- Initial Load ---
    showView(); // Initial view setup
});