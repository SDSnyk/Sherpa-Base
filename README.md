# 🚀 AI Dependency Upgrade Planner

A command-line tool that uses Snyk and Google's Gemini AI to analyze open-source vulnerabilities, create strategic upgrade plans, and suggest package replacements.

This tool automates the tedious process of sifting through a Snyk report. It helps developers prioritize security fixes by grouping them based on risk and provides intelligent alternatives for dependencies that have no direct upgrade path.

***

## ✨ Features

* **Automated Snyk Scanning**: Executes a Snyk scan on any local project directory.
* **AI-Powered Upgrade Plan**: Leverages the Gemini AI to analyze vulnerabilities and generate a prioritized upgrade plan. It intelligently groups patch and minor version bumps first to minimize breaking changes.
* **Replacement Suggestions**: For vulnerabilities that have no direct fix, the tool asks the AI to suggest popular and well-maintained alternative packages.
* **Interactive**: Prompts the user for the project path, making it easy to use.
* **Resilient**: Includes a "wait and retry" mechanism to gracefully handle API rate limiting.

***

## 🔧 Prerequisites

Before you begin, ensure you have the following installed and configured:

1.  **Python 3.8+**
2.  **Node.js and npm**
3.  **Snyk CLI**: The command-line tool for Snyk.
4.  **Google AI API Key**: A valid API key from [Google AI Studio](https://aistudio.google.com/).

***

## ⚙️ Setup & Installation

Follow these steps to get your local environment set up.

1.  **Clone the Repository**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-name>
    ```

2.  **Install and Authenticate Snyk**
    ```bash
    # Install the Snyk CLI globally
    npm install -g snyk

    # Authenticate with your Snyk account
    snyk auth
    ```

3.  **Set Up Python Environment**
    ```bash
    # Create a virtual environment
    python3 -m venv venv

    # Activate it (macOS/Linux)
    source venv/bin/activate
    # On Windows, use: venv\Scripts\activate
    ```

4.  **Install Python Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure API Key**
    * Create a file named `.env` in the project's root directory.
    * Add your Google AI API key to this file in the following format:
        ```
        # .env
        GOOGLE_API_KEY="YOUR_API_KEY_HERE"
        ```

***

## ▶️ How to Use

Running the application is simple.

1.  Make sure your virtual environment is activated.
2.  Run the script from the command line:
    ```bash
    python3 upgrade_planner.py
    ```
3.  The script will then prompt you to enter the full path to the project directory you wish to scan.
    ```bash
    Please enter the full path to the project you want to scan: /path/to/your/project
    ```
4.  The tool will then run the scan and display the AI-generated reports in your terminal.

***

### Example Output
