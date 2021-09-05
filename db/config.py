import os

url = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
    os.environ["DB_USERNAME"],
    os.environ["DB_PASSWORD"],
    os.getenv("DB_HOST", "127.0.0.1"),
    os.getenv("DB_PORT", 5432),
    os.environ["DB_NAME"],
)
