import requests
import logging

# Setup proper logging instead of print statements
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Testing streaming response from chat API...")

response = requests.post(
    "http://localhost:8000/api/chat/stream",
    params={"prompt": "Explain LLM"},
    stream=True
)

for chunk in response.iter_content(chunk_size=1):
    if chunk:
        # For streaming response, we'll keep the direct output but log the start/end
        print(chunk.decode("utf-8"), end="", flush=True)

logger.info("Streaming response test completed")