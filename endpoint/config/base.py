import os

DEBUG = True

# database
DATABASE_HOST = os.environ["DATABASE_HOST"]
DATABASE_NAME = os.environ["DATABASE_NAME"]
DATABASE_USER = os.environ["DATABASE_USER"]
DATABASE_PASSWORD = os.environ["DATABASE_PASSWORD"]
DATABASE_PORT = int(os.environ["DATABASE_PORT"])
