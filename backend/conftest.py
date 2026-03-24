import os

os.environ.setdefault("S3_BUCKET", "test-bucket")
os.environ.setdefault("FAISS_INDEX_KEY", "test/index")
os.environ.setdefault("EPISODES_JSON_KEY", "test/episodes.json")
os.environ.setdefault("BEDROCK_EMBED_MODEL", "amazon.titan-embed-text-v2:0")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("BEDROCK_CHAT_MODEL", "anthropic.claude-haiku-4-5-20251001")
