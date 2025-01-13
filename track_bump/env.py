import os

CI_USER = os.getenv("CI_USER")
CI_USER_EMAIL = os.getenv("CI_USER_EMAIL")

DEFAULT_BRANCH = os.getenv("DEFAULT_BRANCH", "main")
