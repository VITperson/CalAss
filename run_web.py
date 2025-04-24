import uvicorn
from gpt_calendar_planner.web import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 