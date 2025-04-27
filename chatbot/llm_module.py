import os
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GEMINI_API_KEY)

prompt = ChatPromptTemplate.from_template(
    """
    You are an intelligent AI assistant. Answer user questions based on the provided context.
    <Context>
    {context}
    </Context>
    Question: {input}
    """
)

@csrf_exempt
def process_pdf(file_path, question):
    """Extract information from a PDF and answer a question."""
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    final_documents = text_splitter.split_documents(docs)
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)
    vectors = FAISS.from_documents(final_documents, embeddings)

    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = vectors.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    response = retrieval_chain.invoke({'input': question})
    return response['answer']

@csrf_exempt
def chatbot_response(request):
    """API to handle both direct text input and PDF-based queries via FormData."""

    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    question = request.POST.get("question")  # Extract text input from FormData
    print(question, 'question')
    uploaded_file = request.FILES.get("file")  # Extract file from FormData

    if not question:
        return JsonResponse({"error": "Question is required"}, status=400)

    if uploaded_file:
        file_path = default_storage.save(uploaded_file.name, uploaded_file)
        full_file_path = os.path.join(default_storage.location, file_path)

        answer = process_pdf(full_file_path, question)

        os.remove(full_file_path)  # Cleanup after processing
        return JsonResponse({"answer": answer})

    else:
        response = llm.invoke(question)
        return JsonResponse({"answer": response.content})