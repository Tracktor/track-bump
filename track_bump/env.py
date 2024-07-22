import os


CI_USER = os.getenv("CI_USER")
CI_USER_EMAIL = os.getenv("CI_USER_EMAIL")

MAIN_BRANCH = os.getenv("MAIN_BRANCH", "main")
