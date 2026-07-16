# Terminal Profile Setup

## Local preview

Replace `YOUR_GITHUB_USERNAME` and run:

```bash
GITHUB_USERNAME=YOUR_GITHUB_USERNAME python3 scripts/generate_profile.py
```

Open `assets/profile.svg` in a browser.

## Profile repository

Create a public GitHub repository whose name exactly matches your GitHub username. Copy these files into it, commit, and push to `main`.

## Workflow

Open the repository's **Actions** tab and run **Update terminal profile** manually once.

The workflow also runs daily and commits a refreshed `assets/profile.svg` when the generated output changes.
