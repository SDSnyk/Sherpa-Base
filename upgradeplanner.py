# upgrade_planner.py

import subprocess
import json
import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
from google.api_core import exceptions


# --- Core Logic Functions ---

def run_snyk_scan(project_path):
    """Runs a Snyk scan on the specified project path and returns the JSON output."""
    print("🔬 Running Snyk scan... (This may take a moment)")
    try:
        result = subprocess.run(
            ['snyk', 'test', '--json'],
            capture_output=True,
            text=True,
            check=False,
            cwd=project_path
        )
        if result.returncode != 0 and not result.stdout:
            print(f"❌ Snyk command failed with an error:\n{result.stderr}")
            return None
        return json.loads(result.stdout)
    except FileNotFoundError:
        print("❌ Error: 'snyk' command not found. Is the Snyk CLI installed and in your PATH?")
        return None
    except json.JSONDecodeError:
        print(f"❌ Error: Failed to decode Snyk's JSON output. Is the project configured correctly?")
        return None


def process_snyk_results(snyk_data):
    """Separates vulnerabilities into fixable and unfixable lists."""
    fixable_vulns = []
    unfixable_vulns = []

    if not snyk_data:
        return fixable_vulns, unfixable_vulns

    # Handle both single project and monorepo Snyk outputs
    if isinstance(snyk_data, list):
        vulnerabilities = [vuln for item in snyk_data for vuln in item.get('vulnerabilities', [])]
    else:
        vulnerabilities = snyk_data.get('vulnerabilities', [])

    for vuln in vulnerabilities:
        if vuln.get('upgradePath') and len(vuln['upgradePath']) > 1:
            fixable_vulns.append(vuln)
        else:
            unfixable_vulns.append(vuln)

    return fixable_vulns, unfixable_vulns


# --- AI Prompt Generation ---

def create_upgrade_prompt(vulnerabilities):
    """Creates the prompt for generating a step-by-step upgrade plan."""
    prompt_details = [
        (
            f"- Package: {vuln.get('packageName')}\n"
            f"  Current Version: {vuln.get('version')}\n"
            f"  Suggested Upgrade: {vuln.get('upgradePath', ['N/A'])[1]}\n"
            f"  Severity: {vuln.get('severity')}"
        )
        for vuln in vulnerabilities
    ]

    # Join the details into a single string before the f-string to avoid syntax errors.
    details_string = "\n".join(prompt_details)

    return f"""
    You are an expert software engineer. Based on the following list of vulnerabilities, create a prioritized, step-by-step upgrade plan in Markdown format. Group patch and minor updates first to minimize breaking changes.

    Vulnerabilities with a direct fix:
    {details_string}
    """


def create_replacement_prompt(vulnerabilities):
    """Creates the prompt for suggesting alternative packages."""
    prompt_details = [
        (
            f"- Package: '{vuln.get('packageName')}'\n"
            f"  Vulnerability: {vuln.get('title')} ({vuln.get('severity')} severity)"
        )
        for vuln in vulnerabilities
    ]

    # Join the details into a single string before the f-string to avoid syntax errors.
    details_string = "\n".join(prompt_details)

    return f"""
    You are an expert software engineer. The following open-source packages have vulnerabilities with no direct upgrade path available. 
    For each package, please infer its primary purpose from its name and suggest 1-2 popular, well-maintained alternative packages that fulfill the same purpose. 
    Provide a brief justification for each suggestion. Format the output clearly in Markdown.

    Packages needing replacement:
    {details_string}
    """


# --- AI Communication ---

def get_ai_response(prompt):
    """Sends a prompt to the Gemini API and returns the response, with a retry mechanism."""
    if not prompt:
        return "Prompt could not be created."

    print("🧠 Asking Gemini for insights...")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        return response.text
    except exceptions.ResourceExhausted:
        print("🟡 Rate limit hit. Waiting for 30 seconds before retrying...")
        time.sleep(30)
        print(" yeniden deneme...")
        try:
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Error on retry: {e}"
    except Exception as e:
        return f"❌ An unexpected error occurred: {e}"


# --- Main Application Flow ---

def main():
    """Main function to orchestrate the entire process."""
    load_dotenv()
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("🚨 Please set the GOOGLE_API_KEY in a .env file.")
        return

    genai.configure(api_key=api_key)

    project_path_to_scan = input("Please enter the full path to the project you want to scan: ")
    if not project_path_to_scan or not os.path.isdir(project_path_to_scan):
        print("❌ Invalid path entered. Please provide a valid directory. Exiting.")
        return

    snyk_results = run_snyk_scan(project_path_to_scan)
    if not snyk_results:
        return

    fixable, unfixable = process_snyk_results(snyk_results)

    if fixable:
        upgrade_prompt = create_upgrade_prompt(fixable)
        upgrade_plan = get_ai_response(upgrade_prompt)
        print("\n" + "=" * 50)
        print("🚀 Your AI-Generated Dependency Upgrade Plan 🚀")
        print("=" * 50 + "\n")
        print(upgrade_plan)
    else:
        print("\n✅ No vulnerabilities with direct upgrade paths were found.")

    if unfixable:
        replacement_prompt = create_replacement_prompt(unfixable)
        replacement_suggestions = get_ai_response(replacement_prompt)
        print("\n" + "=" * 50)
        print("🤔 AI Suggestions for Package Replacements 🤔")
        print("=" * 50 + "\n")
        print(replacement_suggestions)
    else:
        print("\n✅ All found vulnerabilities seem to have a direct upgrade path.")


if __name__ == "__main__":
    main()