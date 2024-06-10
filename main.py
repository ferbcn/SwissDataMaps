import uvicorn
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.wsgi import WSGIMiddleware
from dash_app import app as dash_app

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# handler = logging.StreamHandler()
handler = logging.FileHandler("fastapi.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Define the FastAPI server
app = FastAPI()

# Middleware to log IP addresses
@app.middleware("http")
async def log_ip_address(request: Request, call_next):
    logger.info(f"Client IP: {request.client.host}")
    response = await call_next(request)
    return response

# Mount the Dash app as a sub-application in the FastAPI server
app.mount("/", WSGIMiddleware(dash_app.server))

# Start the FastAPI server
if __name__ == "__main__":
    logger.info("Starting FastAPI server")
    uvicorn.run(app, host="0.0.0.0", port=8000)