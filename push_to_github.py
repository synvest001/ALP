import requests
import os
import sys

TOKEN = "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"
REPO_NAME = "ALP"
USERNAME = "synvest001"

# 1. Create the repository on GitHub
headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
data = {
    "name": REPO_NAME,
    "private": True,
    "description": "ALP Magical Kingdom Project"
}
print(f"Creating repository {REPO_NAME} on GitHub...")
response = requests.post("https://api.github.com/user/repos", headers=headers, json=data)

if response.status_code == 201:
    print("Repository created successfully!")
elif response.status_code == 422:
    print("Repository already exists. Proceeding to push...")
else:
    print(f"Failed to create repository: {response.text}")
    sys.exit(1)

# 2. Push using Dulwich
try:
    from dulwich import porcelain
except ImportError:
    print("Dulwich not installed.")
    sys.exit(1)

repo_path = "."
print("Initializing local git repository...")
# Check if .git exists, if not initialize
if not os.path.exists(".git"):
    porcelain.init(repo_path)
    
# Set up gitignore to ignore node_modules
if not os.path.exists(".gitignore"):
    with open(".gitignore", "w") as f:
        f.write("node_modules/\n.env\n")

print("Adding files...")
porcelain.add(repo_path)

print("Committing files...")
porcelain.commit(repo_path, message=b"Initial commit of ALP Master Plan and App Scaffold", author=b"Antigravity <bot@antigravity.dev>")

print("Pushing to GitHub...")
remote_url = f"https://{USERNAME}:{TOKEN}@github.com/{USERNAME}/{REPO_NAME}.git"

# Dulwich push requires specifying the ref explicitly for empty remotes sometimes, or we can just push current active branch
try:
    porcelain.push(repo_path, remote_url, "refs/heads/main")
    print("Push successful!")
except Exception as e:
    # If branch is master
    try:
        porcelain.push(repo_path, remote_url, "refs/heads/master")
        print("Push successful (master branch)!")
    except Exception as e2:
        print(f"Failed to push: {e2}")
