import uvicorn
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from dash_app import app as dash_app

# Define the FastAPI server
app = FastAPI()

# Mount the Dash app as a sub-application in the FastAPI server
app.mount("/", WSGIMiddleware(dash_app.server))


# Start the FastAPI server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)