# flowforge-ai/main.py
from dotenv import load_dotenv
load_dotenv()

from app.main import app
import uvicorn
from app.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True if settings.environment == "development" else False,
        log_level="info"
    )

# uvicorn app.main:app --reload
# pytest tests\test_main.py -v