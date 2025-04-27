import os
import io
import fitz
import streamlit as st
from llm_apikeys import groq_api_key
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from PIL import Image
import pytesseract

os.environ['GROQ_API_KEY'] = groq_api_key

llm = ChatGroq(model="llama3-8b-8192", temperature=0.5)

chat_prompt = PromptTemplate(
    input_variables=['query'],
    template="Answer this query: {query}"
)

chat_chain = LLMChain(llm=llm, prompt=chat_prompt)

st.title("Chatbot with File Upload")

user_query = st.text_input("Ask me anything:")

uploaded_file = st.file_uploader("Upload a file (PDF/Image)", type=["pdf", "png", "jpg", "jpeg"])

def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file uploaded via Streamlit."""
    text = ""
    pdf_bytes = io.BytesIO(pdf_file.read()) 
    with fitz.open("pdf", pdf_bytes) as doc:
        for page in doc:
            text += page.get_text("text") + "\n"
    return text

def extract_text_from_image(image_file):
    """Extracts text from an image using OCR."""
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image)
    return text

extracted_text = ""
if uploaded_file:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    if file_extension == "pdf":
        extracted_text = extract_text_from_pdf(uploaded_file)
    elif file_extension in ["png", "jpg", "jpeg"]:
        extracted_text = extract_text_from_image(uploaded_file)
    st.write("📄 Extracted Text from File:")
    st.text_area("File Content", extracted_text, height=200)

if st.button("Get Response"):
    if user_query:
        response = chat_chain.run(query=user_query)
        st.write("Response:", response)
    elif extracted_text:
        response = chat_chain.run(query=extracted_text)
        st.write("Response from File:", response)
    else:
        st.warning("Please enter a query or upload a file.")
# 🧠💬 