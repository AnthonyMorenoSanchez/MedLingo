from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
import uvicorn
from app.config import Settings
s=Settings()
uvicorn.run('app.main:app',host=s.host,port=s.port,log_level=s.log_level)
