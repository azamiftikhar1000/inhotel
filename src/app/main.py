# python imports
from typing import List

# fastapi  imports
from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

# application imports
from src.auth.auth_router import user_router
from src.organization.org_router import org_router
from src.core.core_router import core_router
from src.services.embeddings_manager import setup_embedding_model
from src.services.milvus_manager import setup_milvus 
from src.services.embeddings_processor import EmbeddingsProcessor

import os

milvus_manager = None
embeddings_model = None
embeddings_processor = None

if "MILVUS_URI" in os.environ:
    milvus_manager = setup_milvus()
    embeddings_model = setup_embedding_model()
    embeddings_processor = EmbeddingsProcessor(embeddings_model, milvus_manager)

# fastapi initialization
app = FastAPI()


# CORS Middleware
origins: List = []


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers from the application
app.include_router(user_router)
app.include_router(org_router)
app.include_router(core_router)


# root of the server
@app.get("/", status_code=status.HTTP_200_OK)
def root() -> dict:
    return {"message": "Welcome to Inhotel.io", "docs": "/docs"}
