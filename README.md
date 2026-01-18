# AeroStream: Real-Time Flight Efficiency Engine

![Vue.js](https://img.shields.io/badge/Frontend-Vue.js_3-4FC08D?style=for-the-badge&logo=vuedotjs&logoColor=white)
![Vite](https://img.shields.io/badge/Build_Tool-Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Databricks](https://img.shields.io/badge/Compute-Databricks-FF3621?style=for-the-badge&logo=databricks&logoColor=white)
![Azure Data Factory](https://img.shields.io/badge/Orchestration-Azure_Data_Factory-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)
![ADLS Gen2](https://img.shields.io/badge/Storage-ADLS_Gen2-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Key Vault](https://img.shields.io/badge/Security-Azure_Key_Vault-000000?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Python](https://img.shields.io/badge/Language-Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## Problem Statement


### The Efficiency Blind Spot in Modern Aviation

Commercial aviation is an industry defined by razor-thin margins, where fuel costs typically represent 20-30% of an airline's total operating expenses. While flight paths are meticulously planned before takeoff, the dynamic reality of the atmosphere, shifting wind vectors, unexpected thermal gradients, and jet streams, often renders these plans obsolete the moment wheels leave the ground. A pilot fighting a 100 km/h headwind burns significantly more fuel to maintain schedule, yet traditional tracking tools often fail to contextualize this struggle.

Most existing flight tracking systems provide only positional awareness, answering the question, *"Where is the plane?"* They lack the integrated intelligence to answer the far more critical operational question, *"How efficiently is the plane flying?"* Analysts and ground controllers are often forced to toggle between radar displays, weather maps, and performance charts to gauge fleet health. This fragmentation creates a data blind spot, making it difficult to instantly identify which aircraft are underperforming due to environmental factors versus mechanical drag, leading to reactive rather than proactive decision-making.

---

## The Solution

**AeroStream** is an operational intelligence engine designed to close this gap by fusing live flight telemetry with hyper-local atmospheric data. Rather than treating weather and flight paths as separate datasets, the system integrates them into a single, cohesive data product. By ingesting real-time aircraft positions from the OpenSky API and matching them spatially with the nearest weather stations via the OpenMeteo API, AeroStream creates a rich, multi-dimensional view of every flight’s operating environment.

At the heart of the platform lies a physics-aware Machine Learning model that serves as an automated auditor for flight performance. By analyzing altitude, temperature, and wind resistance, the model calculates the theoretical "Optimal Velocity" for every aircraft in the sky. The system then compares this benchmark against the actual ground speed to generate a live "Efficiency Score." This allows the system to mathematically distinguish between a pilot skillfully riding a tailwind and one burning excess fuel to fight a headwind.

This intelligence is delivered through a modern, web-based dashboard that transforms raw data into instant situational awareness. Instead of presenting a cluttered map of thousands of neutral dots, AeroStream visualizes the fleet's performance spectrum: highly efficient flights glow green, while those struggling against drag or weather highlight in red. This empowers airline analysts to move beyond simple tracking and start managing the true physics of their fleet in real-time.

---

## Tech Stack

I utilized a modern **Lakehouse Architecture** hosted entirely on Microsoft Azure, designed to handle the velocity of flight telemetry and the volume of historical weather data.

* **Cloud Storage & Lakehouse**: **Azure Data Lake Storage (ADLS) Gen2**
    * Serves as the unified storage layer for the **Medallion Architecture** (Bronze/Silver/Gold).
    * Implements **Delta Lake** protocol to ensure ACID transactions and schema enforcement on raw JSON files.
* **Data Processing Engine**: **Azure Databricks (Apache Spark)**
    * The core compute engine for all ETL and ELT workloads.
    * Utilizes **PySpark** for distributed processing, handling complex spatio-temporal joins between moving aircraft and static weather stations.
* **Orchestration**: **Azure Data Factory (ADF)**
    * Manages the end-to-end pipeline lifecycle, triggering ingestion jobs and Databricks notebooks.
    * Decouples the **Training Pipeline** (Weekly) from the **Inference Pipeline** (Hourly) to optimize compute costs.
* **Machine Learning**: **Spark MLlib**
    * Selected for its ability to train models on distributed datasets without sampling.
    * Handles feature vectorization and trains the Linear Regression model used for generating the `Efficiency_Score`.
* **Backend API**: **FastAPI**
    * A high-performance asynchronous Python framework that bridges the gap between the Data Lake and the Web App.
    * Acts as a secure proxy, managing Databricks authentication tokens so they are never exposed to the client.
* **Frontend**: **Vue.js 3 + Vite**
    * A lightweight, reactive framework chosen for its speed and modular component architecture.
    * Integrates **Leaflet.js** to render interactive, geospatial maps capable of plotting hundreds of live flight vectors.
* **Security**: **Azure Key Vault**
    * Centralizes the management of secrets, ensuring that API keys (OpenSky, OpenMeteo) and storage credentials are never hardcoded in the codebase.
* **Deployment**: **Render (Backend) & Vercel (Frontend)**
    * Provides a scalable, serverless production environment that automatically deploys updates via Git triggers.

## Pipeline Architecture

<img width="5000" height="3000" alt="diagram-export-1-19-2026-1_13_27-AM" src="https://github.com/user-attachments/assets/54429262-3136-4404-adeb-548f2bdbe309" />

---
## Project Structure

```
AeroStream/
├── backend/                  # FastAPI Application (The Bridge)
│   ├── venv/                 # Python Virtual Environment
│   ├── .env                  # Secrets (DB_TOKEN, DB_HOST) - *Not committed to Git*
│   ├── main.py               # API Endpoints & CORS configuration
│   └── requirements.txt      # Python dependencies for Render
├── databricks/               # Spark & ML Notebooks (The Brain)
│   ├── 01_raw_staging.ipynb      # Bronze Layer: Ingestion from ADLS
│   ├── 02_processing.ipynb       # Silver Layer: Cleaning & Parsing
│   ├── 03_gold_presentation.ipynb # Gold Layer: Joins & ML Inference
│   └── 04_model_training.ipynb   # (Optional) Weekly Training logic
├── dataset/                  # ADF Dataset Definitions (JSON)
│   ├── DS_ADLS_Bronze_Flights.json   # Connection to Data Lake
│   ├── DS_OpenMeteo_Weather.json     # Connection to Weather API
│   └── ...
├── factory/                  # ADF Factory Configuration
│   └── AeroStream.json       # Main Data Factory resource definition
├── frontend/                 # Vue.js 3 + Vite App (The Face)
│   ├── public/               # Static assets
│   ├── src/                  # Vue components & Logic
│   ├── package.json          # Node.js dependencies
│   └── vite.config.js        # Build configuration for Vercel
├── linkedService/            # ADF Connection Strings (JSON)
│   ├── LS_ADLS_Gen2.json     # Azure Data Lake Storage Auth
│   ├── LS_AzureDatabricks.json # Databricks Cluster connection
│   ├── LS_KeyVault.json      # Secure credential retrieval
│   └── ...
├── pipeline/                 # ADF Pipeline Logic
│   └── PL_Master_Orchestrator.json # The defined workflow JSON
└── README.md                 # Project Documentation
```


### **Component Breakdown**

* **`backend/`**: A lightweight Python API that secures your Databricks credentials. It accepts requests from the frontend, queries the `presentation` schema, and returns JSON, keeping your infrastructure secure.
* **`databricks/`**: Contains the core logic. These notebooks handle the **Medallion Architecture** transformations, from raw JSON ingestion to the complex spatial joins that link moving aircraft to stationary weather towers.
* **`dataset/` & `linkedService/**`: Infrastructure-as-Code (IaC) definitions for Azure Data Factory. These JSON files define *what* data we talk to (APIs, Storage) and *how* we authenticate (Key Vault).
* **`frontend/`**: The reactive web application. It fetches live data from the backend and renders it onto an interactive geospatial map using **Leaflet.js**, providing the final visual layer for the user.

```
