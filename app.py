import os
import requests
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OWNER = os.getenv("OWNER")
REPO = os.getenv("REPO")
PR_NUMBER = os.getenv("PR_NUMBER")

# Initialize Gemini client
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# GitHub headers
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# Get Pull Request files
files_url = f"https://api.github.com/repos/{OWNER}/{REPO}/pulls/{PR_NUMBER}/files"

response = requests.get(files_url, headers=headers)

if response.status_code != 200:
    print("Failed to fetch Pull Request files.")
    print(response.text)
    exit()

files = response.json()

code_changes = ""

for file in files:
    filename = file["filename"]
    patch = file.get("patch", "")

    code_changes += f"\n\nFile: {filename}\n"
    code_changes += patch

if not code_changes.strip():
    print("No code changes found in this Pull Request.")
    exit()

prompt = f"""
You are an experienced Software Engineer.

Review the following GitHub Pull Request.

Provide:

1. Overall Review
2. Bugs (if any)
3. Performance Improvements
4. Security Suggestions
5. Best Practices
6. Final Rating out of 10

Code Changes:

{code_changes}
"""

# Generate AI Review
response = gemini_client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt
)

review = response.text

print("\n========== AI REVIEW ==========\n")
print(review)

# GitHub Comment API
comment_url = f"https://api.github.com/repos/{OWNER}/{REPO}/issues/{PR_NUMBER}/comments"

comment_data = {
    "body": f"## 🤖 AI Code Review\n\n{review}"
}

comment_response = requests.post(
    comment_url,
    headers=headers,
    json=comment_data
)

if comment_response.status_code == 201:
    print("\nAI Review posted successfully!")
else:
    print("\nFailed to post review.")
    print(comment_response.text)