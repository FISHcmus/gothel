from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from router import EvidenceProblem, FlashlightProblem, ReadingContent, User
load_dotenv()

# --- API ROUTES ---
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                   "https://gothel.fishcmus.io.vn"
                   ],  # Your Next.js frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(EvidenceProblem.router)
app.include_router(FlashlightProblem.router)
app.include_router(ReadingContent.router)
app.include_router(User.router)
