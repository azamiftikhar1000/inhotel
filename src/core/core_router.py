# framework imports
from fastapi import APIRouter, status, HTTPException, File, UploadFile
import os
import tempfile
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import BSHTMLLoader
from openai import OpenAI
from src.app.utils.schemas_utils import AbstractModel
from fastapi import Form


from src.services.embeddings_manager import setup_embedding_model
from src.services.milvus_manager import setup_milvus 
from src.services.embeddings_processor import EmbeddingsProcessor
import requests
from bs4 import BeautifulSoup

def scrape_html_from_url(url):
    try:
        # Send an HTTP GET request to the URL
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers,verify=False)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract the text content from the HTML
            html_content = soup.get_text()
            # Create a temporary file to save the HTML content
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8') as html_file:
                html_file.write(html_content)

            html_path = html_file.name
            print(f"HTML content saved to {html_path}")
            return html_path

        else:
            print(f"Failed to fetch HTML content. Status code: {response.status_code}")
            return None

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
    
milvus_manager = None
embeddings_model = None
embeddings_processor = None

if "MILVUS_URI" in os.environ:
    milvus_manager = setup_milvus()
    embeddings_model = setup_embedding_model()
    embeddings_processor = EmbeddingsProcessor(embeddings_model, milvus_manager)


# application imports
from src.core import schemas

# API Router
core_router = APIRouter(prefix="/api/v1/core", tags=["Core APIs"])

class HotelData(AbstractModel):
    agentName: str
    agentRole: str
    hotelName: str
    hotel: str

@core_router.post("/add_hotel/", status_code=status.HTTP_201_CREATED)
async def add_hotel( hotelName: str = Form(...),
    hotelURL: str = Form(...),
    agentRole: str = Form(...),
    agentName: str = Form(...),
 upload_document: UploadFile = File(...)):
    try:
        # Verify if the uploaded document is a PDF
        if not upload_document.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Create a temporary directory to store the uploaded PDF
        with tempfile.TemporaryDirectory() as temp_dir:

            pdf_path = os.path.join("/home/azam/projects/inhotel/uploads", upload_document.filename)
            # Save the uploaded PDF to the temporary directory
            with open(pdf_path, 'wb') as pdf_file:
                pdf_file.write(upload_document.file.read())

            # Check if the file was successfully created
            if not os.path.exists(pdf_path):
                raise HTTPException(status_code=500, detail="Failed to create the file")
            
        # Parsing and chunking the document.
        print("Inserting document data into Milvus")  
        doc_data = PyPDFLoader(pdf_path).load_and_split(
            RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        )
        # Embedding and insert chunks into the vector database.
        
        for doc  in doc_data:
                embeddings_processor.process_and_save("".join([doc.page_content ]))
        print("Done Insertion") 

        print("Inserting web data into Milvus")
        if hotelURL:       
            web_data = BSHTMLLoader(scrape_html_from_url(hotelURL)).load_and_split(
                RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            )
            for doc  in web_data:
                embeddings_processor.process_and_save("".join([doc.page_content ]))
        print("Done Insertion") 


        # Setup OpenAI client.
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        # Set default values for optional fields
        hotelName = hotelName or "Hotel"
        agentRole = agentRole or "Front Desk Officer"
        agentName = agentName or "Emily"

        # Create an Assistant.
        my_assistant = client.beta.assistants.create(
            name=f'Chat with {agentName}',
            instructions=f'You are {agentName}, a {agentRole} at a renowned hotel named {hotelName}. You excel at assisting others by answering their queries and providing relevant information. You can search for pertinent information using Hotel Database tool if required and respond to questions based on the information retrieved. When you are unsure of an answer to a question, you admit your lack of knowledge while ensuring you always remain polite.',
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

@core_router.post("/chat_hotel/", status_code=status.HTTP_201_CREATED)

async def add_hotel( hotelName: str = Form(...),
    assistant_ID: str = Form(...),
    thread_id: str = Form(...),
    message_id: str = Form(...),
 upload_document: UploadFile = File(...)):
    try:

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="I need to solve the equation `3x + 11 = 14`. Can you help me?"
    )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")
