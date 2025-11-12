# DevSecOps Fortress API (fastapi-secure-pipeline)

This is a reference project demonstrating the implementation of modern **DevSecOps** and **Software Supply Chain Security** practices for a FastAPI application.

The goal of this repository is to serve as a robust, "production-ready" template that integrates security into every phase of the Software Development Lifecycle (SDLC), **demonstrating a mastery of current tools and concepts.**

---

## Key Features

* **Application:** A FastAPI API featuring JWT authentication, Argon2id password hashing, and Alembic database migrations.
* **Containerization:** A multi-stage, optimized Dockerfile with a non-root user, a true `healthcheck`, and hash-pinned dependencies.
* **Local Orchestration:** A reliable `docker-compose.yaml` using `depends_on` and service `healthcheck` conditions for a clean startup.

---

## How to Run Locally

You can get the entire application and database running with just a few commands.

**Prerequisites:**
* Git
* Docker and Docker Compose

**Steps:**

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/mateoxav/fastapi-secure-pipeline.git
    cd fastapi-secure-pipeline
    ```

2.  **Create the environment file:**
    The project uses a `.env` file for secrets and configuration. Copy it from the example:
    ```bash
    cp .env.example .env
    ```
    *(**Note:** For local development, the default values are sufficient.)*

3.  **Build and run with Docker Compose:**
    ```bash
    docker compose up --build -d
    ```
    * `--build` forces a rebuild of your local image.
    * `-d` runs the containers in detached mode.

4.  **You're all set!**
    * **API:** The API is now available at `http://localhost:8000`.
    * **Docs (Swagger UI):** `http://localhost:8000/docs`.
    * **Frontend:** The simple web UI is served from `http://localhost:8000/`.

### 🧠 Production Note: The `AUTO_MIGRATE` Flag

You'll notice the `compose.yaml` sets the environment variable `AUTO_MIGRATE=true`. This instructs the container's `entrypoint.sh` to run `python scripts/migrate.py` on startup.

> **This is an intentional convenience for development and demos**, ensuring the database is created and migrated automatically.
>
> In a **real production environment**, this flag would be disabled (`AUTO_MIGRATE=false`). Database migrations **must not** be run by the application server on startup. Instead, they should be run as an **explicit step in the deployment (CI/CD) pipeline** *before* the new application version is rolled out (e.g., as a Kubernetes Job or a separate CI `run` step).
>
> This approach prevents race conditions, ensures migrations complete successfully before new code needs them, and allows for cleaner rollbacks.

---

## 📸 Screenshot

Once running, you can use the simple web UI (served by FastAPI) to test user registration, login, and item creation.

![Image.](.png)


---

## 🛡️ The DevSecOps Approach (The "Why")

This project isn't just an API; it's a demonstration of a secure development *process*.

### 1. Code & Pre-commit (Shift-Left)

Security starts on the developer's local machine.

* **Pre-commit Hooks:** The `.pre-commit-config.yaml` ensures that no substandard or insecure code reaches the repository.
    * **Format & Quality:** `black`, `isort`, `flake8`.
    * **Static Typing:** `mypy` prevents type-related bugs.
    * **Local SAST:** `bandit` scans for common Python vulnerabilities on every commit.
    * **Secret Scanning:** `gitleaks` prevents secrets (API keys, passwords) from ever being committed.

### 2. Continuous Integration (CI Pipeline - `ci.yml`)

The CI pipeline is the core of automated security assurance.

* **SAST (Static Analysis):** `GitHub CodeQL` performs a deep security analysis of the source code.
* **SCA (Dependency Scanning):** `pypa/gh-action-pip-audit` scans dependencies (`requirements.txt`) for known vulnerabilities.
* **Testing & Coverage:** `pytest` runs the test suite, and `pytest-cov` enforces a **minimum 85% test coverage** (`--cov-fail-under=85`), ensuring tests are meaningful.
* **IaC & Config Scanning:** `Trivy (config)` and `Trivy (fs)` run on Pull Requests to detect misconfigurations (e.g., in the Dockerfile) and secrets *before* they are merged.

### 3. Supply Chain & Artifacts (The Build)

Ensuring the integrity of the final artifact (the Docker image) is critical.

* **SBOM (Software Bill of Materials):** A `CycloneDX` formatted `SBOM` is generated on every build, providing a complete inventory of all dependencies.
* **Reproducible Dependencies:**
    * The versioned `.txt` files are generated from the `.in` files using `pip-compile --generate-hashes`.
    * The Dockerfile uses `pip install --require-hashes` to guarantee that *only* the exact, vetted dependencies are installed, preventing dependency confusion or hijacking attacks.
* **Secure Images:**
    * The Python base image is **pinned by digest** (`@sha265:...`) to prevent mutable tag attacks.
    * `Trivy (image)` scans the final Docker image for OS and library vulnerabilities before it's pushed.
* **Image Signing & Attestation (SLSA):**
    * The image pushed to GHCR is **signed with Cosign** (in keyless mode via OIDC).
    * A **SLSA build provenance attestation** is generated by the Docker builder.
    * The pipeline **verifies its own signature and attestation** (`cosign verify` and `cosign verify-attestation`) to complete the trust loop.

### 4. Dynamic Analysis (DAST - `dast-zap.yml`)

* **Authenticated DAST:** A separate `OWASP ZAP` pipeline runs, which:
    1.  Starts the full application stack using Docker Compose.
    2.  Registers a new test user against the API.
    3.  **Logs in to get a JWT token.**
    4.  Uses that token to perform an **authenticated API scan** (`action-api-scan`), testing the protected business logic.

### 5. Runtime & Deployment (`migrate.py` & `Dockerfile`)

* **Safe Migrations:** The `migrate.py` script uses a PostgreSQL **Advisory Lock** (`pg_try_advisory_lock`). This prevents race conditions if multiple application replicas try to run migrations simultaneously during a scaled deployment.
* **Principle of Least Privilege:** The container runs as a **non-root user** (`appuser`).
* **Secure Configuration:** The application loads `ALLOWED_HOSTS` and `CORS_ORIGINS` from environment variables and enables `TrustedHostMiddleware` to prevent Host Header attacks.
* **Secure Hashing:** Passwords are hashed using **Argon2id** with OWASP-recommended parameters, managed via `passlib`.