from urllib.robotparser import RobotFileParser
from config import HEADERS
import logging

def load_robots_txt(url):
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        logging.info(f"Loaded robots.txt from {robots_url}")
    except Exception as e:
        logging.warning(f"Failed to load robots.txt: {e}")
        rp = None
    return rp

def can_fetch_url(rp, url):
    if rp is None:
        return True  # If robots.txt could not be loaded, assume it's safe to fetch
    return rp.can_fetch(HEADERS['User-Agent'], url)
