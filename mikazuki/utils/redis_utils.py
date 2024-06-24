import json, os
import redis
from dotenv import load_dotenv

print(os.getcwd())
load_dotenv()
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
TRAINER_SERVER = os.getenv("TRAINER_SERVER", "")


r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)


def publish_data(channel: str, data: dict) -> None:
    message = json.dumps(data)
    r.publish(channel, message)
    print(f"Published message.\nmessage: {message}\nchannel: {channel}\n")
