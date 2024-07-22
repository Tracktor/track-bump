# Track-bump 


Utility library to bump the version / tags or a project repository
following the following pattern:

![CI](./static/ci.png)

# How to use

1. Update your **pyproject.toml** or `.cz.toml` file with the following:

```toml
[tool.track-bump]
version = "0.1.0"
version_files = [
    "sub-project-1/pyproject.toml",
    "sub-project-2/pyproject.toml"
]
bump_message = "chore: release {current_version} → {new_version} [skip ci]"
```
2. Run the following command from inside your project:

```bash
poetry run track-bump
```

or with **pipx**
    
```bash
pipx run track-bump
```

