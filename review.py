import os
from github import Github
from google import genai

TOKEN = os.environ.get("GITHUB_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

g = Github(TOKEN)

client = genai.Client(
    api_key=GEMINI_API_KEY
)



for repo_name in ["Raveena0410/pr-review"]:
    repo = g.get_repo(repo_name)

    print(f"Checking repository: {repo.name}")

    for pr in repo.get_pulls(state="open"):

        print(f"Checking PR #{pr.number}")

        already_reviewed = False

        for comment in pr.get_issue_comments():
            if "## Gemini Code Review" in comment.body:
                already_reviewed = True
                break

        if already_reviewed:
            print(f"PR #{pr.number} already reviewed. Skipping.")
            continue

        full_review = ""

        for file in pr.get_files():

            if not file.patch:
                continue

            print(f"Reviewing file: {file.filename}")

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"""
You are a senior software engineer reviewing a GitHub Pull Request.

Repository: {repo.name}
File: {file.filename}

Changed Code:
{file.patch}

Provide:

1. Summary
2. Bugs
3. Security Issues
4. Performance Issues
5. Suggestions

Keep the review concise.
"""
            )

            full_review += f"\n\n### File: {file.filename}\n\n"
            full_review += response.text

        if full_review.strip():

            pr.create_issue_comment(
                f"""
## Gemini Code Review

{full_review}
"""
            )

            print(f"Review posted on PR #{pr.number}")