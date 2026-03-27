
from pathlib import Path
import importlib
default_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def list_scrappers():
  folder = Path(__file__).parent.joinpath("scrappers")
  return [
      f.stem
      for f in folder.glob("*.py")
      if not f.name.startswith("_")
  ]
    
def load_scrapper(name):
  return importlib.import_module(f"scrappers.{name}")

def format_bytes(size: float) -> str:
  if size is None or size < 0: return "0 B"
  for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
      if size < 1024:
          return f"{size:.2f} {unit}"
      size /= 1024
  return f"{size:.2f} EB"
  
  
class UnknownTrackerError(Exception):
  pass

class ScrappingError(Exception):
  pass