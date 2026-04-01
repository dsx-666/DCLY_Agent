import logging

logging.getLogger("langgraph").setLevel(logging.WARNING)
logging.getLogger("langchain_core").setLevel(logging.WARNING)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)