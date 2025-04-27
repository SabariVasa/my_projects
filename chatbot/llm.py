# import os
# import io
# import re
# import fitz
# import pytesseract
# from PIL import Image
# from rest_framework.decorators import api_view
# from django.views.decorators.csrf import csrf_exempt
# from rest_framework.response import Response
# from django.core.files.storage import default_storage
# from .llm_apikeys import groq_api_key
# from langchain_groq import ChatGroq
# from langchain.chains import LLMChain
# from langchain.prompts import PromptTemplate

# os.environ['GROQ_API_KEY'] = groq_api_key

# llm = ChatGroq(model="llama3-8b-8192", temperature=0.5)

# chat_prompt = PromptTemplate(
#     input_variables=['query'],
#     template="Answer this query: {query}"
# )

# chat_chain = LLMChain(llm=llm, prompt=chat_prompt)

# def extract_text_from_pdf(pdf_file):
#     """Extract text from a PDF file."""
#     text = ""
#     pdf_bytes = io.BytesIO(pdf_file.read())
#     with fitz.open("pdf", pdf_bytes) as doc:
#         for page in doc:
#             text += page.get_text("text") + "\n"
#     return text

# def extract_text_from_image(image_file):
#     """Extract text from an image using OCR."""
#     image = Image.open(image_file)
#     text = pytesseract.image_to_string(image)
#     return text

# def extract_url_content_pairs(text, word_limit=50):
#     """Extract URLs and their associated content descriptions, limiting content to 50 words."""
#     pattern = r'(.+?)\s*(https?://[^\s\[\],`)]+)'
#     matches = re.findall(pattern, text)

#     result = []
#     for content, url in matches:
#         if url:
#             words = content.strip().split()
#             truncated_content = " ".join(words[:word_limit])
#             result.append({"content": truncated_content, "url": url.strip()})
#     return result if len(result) > 0 else text

# @csrf_exempt
# @api_view(['POST'])
# def chatbot_response(request):
#     query = request.data.get("query", "")
#     uploaded_file = request.FILES.get("file")

#     extracted_text = ""
#     if uploaded_file:
#         file_extension = uploaded_file.name.split(".")[-1].lower()
#         if file_extension == "pdf":
#             extracted_text = extract_text_from_pdf(uploaded_file)
#         elif file_extension in ["png", "jpg", "jpeg"]:
#             extracted_text = extract_text_from_image(uploaded_file)

#     final_query = query if query else extracted_text
#     if not final_query:
#         return Response({"error": "Please provide a query or upload a valid file."}, status=400)

#     response = chat_chain.run(query=final_query)
#     return Response({"response": response})
# # import os
# # import io
# # import re
# # import fitz
# # import pytesseract
# # from PIL import Image
# # from rest_framework.decorators import api_view
# # from django.views.decorators.csrf import csrf_exempt
# # from rest_framework.response import Response
# # from django.core.files.storage import default_storage
# # from .llm_apikeys import groq_api_key
# # from langchain_groq import ChatGroq
# # from langchain.chains import LLMChain
# # from langchain.prompts import PromptTemplate

# # os.environ['GROQ_API_KEY'] = groq_api_key

# # llm = ChatGroq(model="llama3-8b-8192", temperature=0.5)

# # chat_prompt = PromptTemplate(
# #     input_variables=['query'],
# #     template="Give the real-time web scraping free website URLs only: {query}"
# # )

# # chat_chain = LLMChain(llm=llm, prompt=chat_prompt)

# # def extract_text_from_pdf(pdf_file):
# #     """Extract text from a PDF file."""
# #     text = ""
# #     pdf_bytes = io.BytesIO(pdf_file.read())
# #     with fitz.open("pdf", pdf_bytes) as doc:
# #         for page in doc:
# #             text += page.get_text("text") + "\n"
# #     return text

# # def extract_text_from_image(image_file):
# #     """Extract text from an image using OCR."""
# #     image = Image.open(image_file)
# #     text = pytesseract.image_to_string(image)
# #     return text

# # def extract_urls(text):
# #     """Extract URLs from text using regex."""
# #     urls = re.findall(r'https?://[^\s\[\]]+', text)
# #     return urls

# # @csrf_exempt
# # @api_view(['POST'])
# # def chatbot_response(request):
# #     query = request.data.get("query", "")
# #     uploaded_file = request.FILES.get("file")

# #     extracted_text = ""
# #     if uploaded_file:
# #         file_extension = uploaded_file.name.split(".")[-1].lower()
# #         if file_extension == "pdf":
# #             extracted_text = extract_text_from_pdf(uploaded_file)
# #         elif file_extension in ["png", "jpg", "jpeg"]:
# #             extracted_text = extract_text_from_image(uploaded_file)

# #     final_query = query if query else extracted_text
# #     if not final_query:
# #         return Response({"error": "Please provide a query or upload a valid file."}, status=400)

# #     response_text = chat_chain.run(query=final_query)
# #     urls = extract_urls(response_text)

# #     if urls:
# #         return Response({"urls": urls})
# #     else:
# #         return Response({"message": "No URLs found in the response."})
import os
import io
import re
import fitz  # PyMuPDF for PDF processing
import pytesseract
from PIL import Image
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from .llm_apikeys import groq_api_key
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Set up Groq API key
os.environ['GROQ_API_KEY'] = groq_api_key

# Initialize LLM
llm = ChatGroq(model="llama3-8b-8192", temperature=0.5)

# General Chat Prompt
general_prompt = PromptTemplate(
    input_variables=['query'],
    template="Answer this query: {query}"
)

# Web Scraping Prompt
scrape_prompt = PromptTemplate(
    input_variables=['query'],
    template="Give the real-time web scraping free website URLs only: {query}"
)

# LLM Chains
chat_chain = LLMChain(llm=llm, prompt=general_prompt)
scrape_chain = LLMChain(llm=llm, prompt=scrape_prompt)

# Extract text from PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_bytes = io.BytesIO(pdf_file.read())
    with fitz.open("pdf", pdf_bytes) as doc:
        for page in doc:
            text += page.get_text("text") + "\n"
    return text

# Extract text from Image (OCR)
def extract_text_from_image(image_file):
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image)
    return text.strip()

# Extract URLs from LLM response
def extract_urls(text):
    urls = re.findall(r'https?://[^\s\[\]]+', text)
    return urls

@csrf_exempt
@api_view(['POST'])
def chatbot_response(request):
    """Process user query or uploaded files and return LLM response."""
    query = request.data.get("query", "")
    uploaded_file = request.FILES.get("file")

    extracted_text = ""
    if uploaded_file:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        if file_extension == "pdf":
            extracted_text = extract_text_from_pdf(uploaded_file)
        elif file_extension in ["png", "jpg", "jpeg"]:
            extracted_text = extract_text_from_image(uploaded_file)

    final_query = query if query else extracted_text
    if not final_query:
        return Response({"error": "Please provide a query or upload a valid file."}, status=400)

    # Determine if the query is related to web scraping
    if "web scraping" in final_query.lower() or "free website" in final_query.lower():
        response_text = scrape_chain.run(query=final_query)
        urls = extract_urls(response_text)
        return Response({"urls": urls} if urls else {"message": "No URLs found in the response."})

    # Default LLM response
    response_text = chat_chain.run(query=final_query)
    return Response({"response": response_text})
