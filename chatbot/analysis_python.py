import os
import uuid
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO
import streamlit as st
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage
from .llm_apikeys import groq_api_key

# Set API key
os.environ['GROQ_API_KEY'] = groq_api_key

# Initialize LLM
llm = ChatGroq(model="llama3-8b-8192", temperature=0.5)

# Streamlit UI
st.title("📊 Data Analysis & AI Insights")

# File uploader
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
query = st.text_area("Enter your query about the dataset")
response_type = st.selectbox("Select response type", ["Both", "Text", "Chart"])

if uploaded_file and query:
    try:
        # Load CSV into Pandas
        df = pd.read_csv(uploaded_file)
        summary = df.describe().to_string()

        # Generate AI response (Text)
        ai_response = None
        if response_type in ["Text", "Both"]:
            messages = [
                SystemMessage(content="You are a data analyst AI. Answer queries based on the dataset."),
                HumanMessage(content=f"Dataset Summary:\n{summary}\n\nUser's Question: {query}")
            ]
            try:
                response = llm.invoke(messages)
                ai_response = response.content
                st.subheader("AI Response")
                st.write(ai_response)
            except Exception as e:
                st.error(f"Error processing query: {str(e)}")

        # Generate Chart (if requested)
        if response_type in ["Chart", "Both"]:
            num_cols = df.select_dtypes(include=['number']).columns
            if len(num_cols) > 0:
                st.subheader("Data Visualization")
                fig, ax = plt.subplots(figsize=(8, 5))
                sns.histplot(df[num_cols[0]], kde=True, ax=ax)
                ax.set_title(f"Distribution of {num_cols[0]}")
                ax.set_xlabel(num_cols[0])
                ax.set_ylabel("Count")
                st.pyplot(fig)
            else:
                st.warning("No numerical columns found for visualization.")
    except Exception as e:
        st.error(f"Invalid CSV file: {str(e)}")
