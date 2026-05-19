import os
import git

SUPPORTED_EXTENSIONS = (
    ".py", ".js", ".ts", ".java", ".cpp", ".html", ".css", ".json", ".md"
)

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}

def get_repo_name(repo_url):
    name = repo_url.rstrip("/").split("/")[-1]
    return name[:-4] if name.endswith(".git") else name

def clone_repo(repo_url):
    repo_name = get_repo_name(repo_url)
    repo_path = os.path.join("repos", repo_name)
    os.makedirs("repos", exist_ok=True)

    if not os.path.exists(repo_path):
        print(f"Cloning repo → {repo_path}")
        git.Repo.clone_from(repo_url, repo_path)
    else:
        print(f"Using existing repo → {repo_path}")

    return repo_path, repo_name

def load_codebase(folder_path):
    repo_name = None

    # Step 1: Handle GitHub URL
    if folder_path.startswith("http"):
        folder_path, repo_name = clone_repo(folder_path)
    else:
        repo_name = os.path.basename(folder_path.rstrip("/"))

    code_files = []

    # Step 2: Walk through files
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for file in files:
            ext = os.path.splitext(file)[1]
            if ext not in SUPPORTED_EXTENSIONS:
                continue

            file_path = os.path.join(root, file)

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip()

                if not content:  # skip empty files
                    continue

                code_files.append({
                    "content": content,
                    "path": file_path,
                    "ext": ext,
                    "filename": file
                })

            except Exception as e:
                print(f"⚠️ Error reading {file_path}: {e}")

    print(f"✅ Total files loaded: {len(code_files)}")
    return code_files, repo_name