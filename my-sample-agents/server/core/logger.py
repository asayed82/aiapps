import logging

logging.basicConfig(
    #filename="debug_messages.log",
    level=logging.INFO, #logging.DEBUG, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)