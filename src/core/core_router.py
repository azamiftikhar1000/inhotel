# framework imports
from fastapi import APIRouter, status, HTTPException, File, UploadFile
import os
import tempfile
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import BSHTMLLoader
from openai import OpenAI
from src.app.utils.schemas_utils import AbstractModel

# application imports
from src.core import schemas

# API Router
core_router = APIRouter(prefix="/api/v1/core", tags=["Core APIs"])

class HotelData(AbstractModel):
    agentName: str
    agent_role: str
    hotel_name: str
    hotel_url: str

@core_router.post("/add_hotel/", status_code=status.HTTP_201_CREATED)
async def add_hotel(data: HotelData, upload_document: UploadFile = File(...)):
    try:
        # Verify if the uploaded document is a PDF
        if not upload_document.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Create a temporary directory to store the uploaded PDF
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = os.path.join(temp_dir, upload_document.filename)
            
            # Save the uploaded PDF to the temporary directory
            with open(pdf_path, 'wb') as pdf_file:
                pdf_file.write(upload_document.file.read())

        # Parsing and chunking the document.
        print("Inserting document data into Milvus")  
        doc_data = PyPDFLoader(pdf_path).load_and_split(
            RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        )

        # Embedding and insert chunks into the vector database.
        embeddings_processor.process_and_save("".join([doc.page_content for doc in doc_data]))
        print("Done Insertion") 

        print("Inserting web data into Milvus")
        if data.hotel_url:       
            web_data = BSHTMLLoader(data.hotel_url).load_and_split(
                RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            )
            embeddings_processor.process_and_save("".join([doc.page_content for doc in web_data]))
        print("Done Insertion") 

        # Setup OpenAI client.
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        # Set default values for optional fields
        hotel_name = data.hotel_name or "Hotel"
        agent_role = data.agent_role or "Front Desk Officer"
        agent_name = data.agent_name or "Emily"

        # Create an Assistant.
        my_assistant = client.beta.assistants.create(
            name=f'Chat with {agent_name}',
            instructions=f'You are {agent_name}, a {agent_role} at a renowned hotel named {hotel_name}. You excel at assisting others by answering their queries and providing relevant information. You can search for pertinent information using Hotel Database tool if required and respond to questions based on the information retrieved. When you are unsure of an answer to a question, you admit your lack of knowledge while ensuring you always remain polite.',
            tools=[
                {
                    'type': 'function',
                    'function': {
                        'name': 'CustomRetriever',
                        'description': 'Retrieve relevant information of Chedi Penthouse',
                        'parameters': {
                            'type': 'object',
                            'properties': {'query': {'type': 'string', 'description': 'The user query'}},
                            'required': ['query']
                        },
                    }
                }
            ],
            model='gpt-4-1106-preview',
        )

        # Return status and assistant ID
        return {"status": "Data processed successfully", "assistant_id": my_assistant.id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")
