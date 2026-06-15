import os
from github import Github
from google import genai

TOKEN = os.environ.get("GITHUB_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

g = Github(TOKEN)

client = genai.Client(
    api_key=GEMINI_API_KEY
)

print("Logged in as:", g.get_user().login)

for repo in g.get_user().get_repos():
    for pr in repo.get_pulls(state="open"):

        for file in pr.get_files():

            if not file.patch:
                continue

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"""
Repository: {repo.name}
File: {file.filename}

Changed Code:
{file.patch}

Review the code briefly.
Provide:
1. Summary
2. Bugs
3. Security Issues
4. Performance Issues
5. Suggestions
"""
            )

            review = response.text

            print(review)

            pr.create_issue_comment(
                f"""
## Gemini Code Review

**File:** {file.filename}

{review}
"""
            )