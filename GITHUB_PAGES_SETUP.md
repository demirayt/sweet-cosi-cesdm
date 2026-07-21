# Publish the CESDM documentation website

The repository is prepared for GitHub Pages with MkDocs Material.

## One-time setup

1. Create or transfer the repository to the GitHub organisation `cesdm` with the repository name `cesdm-toolbox`.
2. Push this repository to the `main` branch.
3. Open **Settings → Pages** in GitHub.
4. Under **Build and deployment**, select **GitHub Actions** as the source.
5. Open the **Actions** tab and verify that **Publish documentation** completes successfully.

The website will then be available at:

`https://cesdm.github.io/cesdm-toolbox/`

## Use a different organisation or repository name

Update these values before publishing:

- `site_url`, `repo_name`, and `repo_url` in `mkdocs.yml`
- `Homepage`, `Documentation`, and `Repository` in `pyproject.toml`
- documentation and clone links in `README.md`

GitHub Pages project-site URLs follow this pattern:

`https://<organisation>.github.io/<repository>/`

## Local preview

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[docs]"
mkdocs serve
```

Open `http://127.0.0.1:8000/`.
