from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from charger import charger_app  # Import charger app
from user import user_app  # Import user app

# Create the main FastAPI app
app = FastAPI()

# Configure CORS middleware to allow cross-origin requests from all domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend URL for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the charger and user FastAPI apps
app.mount("/charger", charger_app)  # Routes starting with /charger go to charger app
app.mount("/user", user_app)  # Routes starting with /user go to user app

# Optional: Main root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to the EV Charging System API",
        # "endpoints": {
        #     "charger": "/charger",
        #     "user": "/user"
        # }
    }

# Ensure the script is run as the main module
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
