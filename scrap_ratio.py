import argparse
import asyncio
import logging
from dotenv import load_dotenv
from util import format_bytes

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scrap_ratio")

from scraper import get_stats

async def main():
    parser = argparse.ArgumentParser(description="Get stats from Torr9.net or C411.org via API")
    parser.add_argument("--site", choices=["torr9", "c411", "both"], required=True, help="Site to get stats from")
    parser.add_argument("--no-headless", action="store_false", dest="headless", default=True, help="Run browser in non-headless mode")
    
    args = parser.parse_args()
    
    sites = ["torr9", "c411"] if args.site == "both" else [args.site]
    
    for s in sites:
        print(f"--- {s.upper()} ---")
        stats = await get_stats(s, args.headless)
        if isinstance(stats, dict):
            print(f"Ratio: {stats['raw_upload'] / stats['raw_download'] if stats['raw_download'] > 0 else 999 if stats['raw_upload'] > 0 else 0}")
            print(f"Upload: {format_bytes(stats['raw_upload'])}")
            print(f"Download: {format_bytes(stats['raw_download'])}")
        else:
            print(stats)

if __name__ == "__main__":
    asyncio.run(main())
