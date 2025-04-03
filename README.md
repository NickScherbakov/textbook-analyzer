# Textbook Analyzer - Intelligent Learning Materials Assistant

An application for analyzing and explaining educational materials using Yandex Cloud artificial intelligence technologies.

## Features
- Text recognition from textbook images (OCR)
- Intelligent analysis and detailed explanation of educational material
- Answers to questions about textbook content
- Generation of examples and additional learning materials

## Technologies
- Python 3.9+
- Flask
- Yandex Cloud Vision API (OCR)
- YandexGPT API
- Bootstrap 5

## Installation and Launch

### Prerequisites
- Python 3.9 or higher
- Yandex Cloud account with a configured service account
- IAM token and Yandex Cloud folder ID

### Installation Steps

1. Clone the repository
```bash
git clone https://github.com/NickScherbakov/textbook-analyzer.git
cd textbook-analyzer
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set environment variables
```bash
export YANDEX_IAM_TOKEN=your_token
export YANDEX_FOLDER_ID=your_folder_id
```

4. Launch the application
```bash
flask run
```

After launching, the application will be available at http://localhost:5000

# Handling Divergent Branches in Git

When working with Git, you may encounter a situation where your local branch and the remote branch have diverged. This means there are commits in both branches that are not present in the other. To resolve this, Git requires you to specify how to reconcile the differences. Here are the available strategies:

1. **Merge**: 
   - Use `git config pull.rebase false` to configure this behavior.
   - This creates a new "merge commit" that combines changes from both branches, preserving their histories.

2. **Rebase**:
   - Use `git config pull.rebase true` to configure this behavior.
   - This rewrites the local branch's history by applying its commits on top of the remote branch's commits, resulting in a linear history.

3. **Fast-forward only**:
   - Use `git config pull.ff only` to configure this behavior.
   - This allows the pull to proceed only if the local branch can be fast-forwarded to match the remote branch, meaning no divergent commits are allowed.

### Configuring Your Preference

You can set your preferred strategy globally for all repositories or locally for the current repository:

- Globally: `git config --global pull.rebase <true|false>` or `git config --global pull.ff only`
- Locally: `git config pull.rebase <true|false>` or `git config pull.ff only`

Alternatively, you can specify the behavior directly in the `git pull` command:

- For merge: `git pull --no-rebase origin <branch>`
- For rebase: `git pull --rebase origin <branch>`
- For fast-forward only: `git pull --ff-only origin <branch>`

By setting a default or specifying the behavior explicitly, you can avoid errors when pulling changes from a remote repository.
