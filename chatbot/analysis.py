# import pandas as pd
# import io
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.parsers import MultiPartParser, FormParser
# from .models import UploadedFile
# from .serializers import FileSerializer

# # Function to process data based on user prompt
# def process_csv(file_data, prompt):
#     # Read CSV from binary data
#     df = pd.read_csv(file_data)

#     # Example prompt-based operations
#     if "remove nulls" in prompt.lower():
#         df.dropna(inplace=True)
#     if "remove duplicates" in prompt.lower():
#         df.drop_duplicates(inplace=True)
#     if "uppercase" in prompt.lower():
#         df = df.applymap(lambda x: x.upper() if isinstance(x, str) else x)
#     if "sort by first column" in prompt.lower():
#         df = df.sort_values(by=df.columns[0])

#     return df.to_dict(orient="records")

# class FileUploadView(APIView):
#     parser_classes = (MultiPartParser, FormParser)

#     def post(self, request, *args, **kwargs):
#         prompt = request.data.get("prompt", "")  # Get prompt input
#         file_serializer = FileSerializer(data=request.data)

#         if file_serializer.is_valid():
#             file_instance = file_serializer.save()

#             # Read file from MongoDB GridFS
#             file_data = file_instance.file.get().read()

#             # ✅ FIX: Use `io.StringIO`
#             processed_data = process_csv(io.StringIO(file_data.decode("utf-8")), prompt)

#             return Response({"message": "File processed successfully", "data": processed_data}, status=200)

#         return Response(file_serializer.errors, status=400)

# import os
# import io
# import pandas as pd
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.parsers import MultiPartParser, FormParser
# from langchain_groq import ChatGroq
# from langchain.schema import HumanMessage
# from .models import UploadedFile
# from .serializers import FileSerializer
# from .llm_apikeys import groq_api_key

# os.environ['GROQ_API_KEY'] = groq_api_key

# llm = ChatGroq(model="llama3-8b-8192", temperature=0.5)

# def process_csv_with_llm(file_data, prompt):
#     """Uses Groq Llama3 to process the CSV file and return an array list."""
#     df = pd.read_csv(file_data)
#     csv_data = df.to_csv(index=False)

#     messages = [
#         HumanMessage(content=f"Here's a CSV file:\n{csv_data}\n\nTask: {prompt}. Provide an array list output.")
#     ]

#     # Generate response using Groq LLM
#     response = llm.invoke(messages)
    
#     # Return the raw response as an array list
#     return response.content  # No JSON conversion, returns direct array format

# class FileUploadView(APIView):
#     parser_classes = (MultiPartParser, FormParser)

#     def post(self, request, *args, **kwargs):
#         prompt = request.data.get("prompt", "")
#         file_serializer = FileSerializer(data=request.data)

#         if file_serializer.is_valid():
#             file_instance = file_serializer.save()
#             file_data = file_instance.file.read().decode("utf-8")

#             processed_data = process_csv_with_llm(io.StringIO(file_data), prompt)

#             return Response({"message": "File processed successfully", "data": processed_data}, status=200)

#         return Response(file_serializer.errors, status=400)
import os
import uuid
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
from rest_framework.parsers import MultiPartParser, FormParser
import base64
from io import BytesIO
from .serializers import FileSerializer
from rest_framework.views import APIView
from langchain_groq import ChatGroq
from rest_framework.response import Response
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework.decorators import api_view
from .llm_apikeys import groq_api_key
import google.generativeai as genai
from langchain.schema import SystemMessage, HumanMessage
from django.views.decorators.csrf import csrf_exempt
from bs4 import BeautifulSoup
import re
from django.utils.decorators import method_decorator

# from langchain_google_genai import ChatGoogleGenerativeAI
os.environ['GROQ_API_KEY'] = groq_api_key
MEDIA_DIR = settings.MEDIA_ROOT
os.makedirs(MEDIA_DIR, exist_ok=True)
llm = ChatGroq(model="llama3-8b-8192", temperature=0.5)

@api_view(['POST'])
def upload_preview(request):
    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    file_path = default_storage.save(f"temp/{file.name}", file)
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)

    try:
        df = pd.read_csv(full_path)
        preview_data = df.head(10).to_dict(orient="records")
        columns = list(df.columns)
    except Exception:
        return JsonResponse({"error": "Invalid CSV file"}, status=400)

    return JsonResponse({
        "file_path": file_path,
        "preview": preview_data,
        "columns": columns
    })



# @api_view(['POST'])
# def process_prompt(request):
#     file_path = request.data.get("file_path")
#     query = request.data.get("query")
#     response_type = request.data.get("response_type", "both").lower()

#     if not file_path or not query:
#         return JsonResponse({"error": "file_path and query are required"}, status=400)

#     full_path = os.path.join(settings.MEDIA_ROOT, file_path)

#     try:
#         df = pd.read_csv(full_path)
#         summary = df.describe().to_string()
#     except Exception:
#         return JsonResponse({"error": "Error reading file"}, status=400)

#     ai_response = ""
#     table_data = None

#     if response_type in ["text", "both"]:
#         messages = [
#             SystemMessage(content="You are a data analyst AI. Answer queries based on the dataset."),
#             HumanMessage(content=f"Dataset Summary:\n{summary}\n\nUser's Question: {query}")
#         ]
#         try:
#             response = llm.invoke(messages)
#             ai_response = response.content
#             print("AI Response:", ai_response)
#             soup = BeautifulSoup(ai_response, "html.parser")
#             cleaned_text = soup.get_text()
#             cleaned_text = re.sub(r"[`#]", "", cleaned_text)
#             cleaned_text = re.sub(r"\bhere( is)?\b[:\-]?", "", cleaned_text, flags=re.IGNORECASE)

#             lines = [line.strip() for line in cleaned_text.splitlines() if line.strip()]

#             table_start = 0
#             for i, line in enumerate(lines):
#                 if re.search(r"\bName\b.*\bPosition\b", line):
#                     table_start = i
#                     break

#             explanation = "\n".join(lines[:table_start]).strip()
#             table_lines = lines[table_start:]

#             header = table_lines[0].split()
#             rows = [line.split(None, len(header) - 1) for line in table_lines[1:]]
#             table_data = [dict(zip(header, row)) for row in rows if len(row) == len(header)]

#             ai_response = explanation
#         except Exception as e:
#             ai_response = f"Error: {str(e)}"

#     base64_chart = None
#     if response_type in ["chart", "both"]:
#         base64_chart = generate_visualization(df)

#     response_data = {
#         "response": ai_response,
#         "data": table_data,
#         "visualization": base64_chart
#     }
#     return JsonResponse(response_data)

@api_view(['POST'])
def process_prompt(request):
    file_path = request.data.get("file_path")
    query = request.data.get("query")
    response_type = request.data.get("response_type", "both")

    if not file_path or not query:
        return JsonResponse({"error": "Missing query or file"}, status=400)

    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    try:
        df = pd.read_csv(full_path)
    except Exception:
        return JsonResponse({"error": "Invalid file"}, status=400)

    summary = df.describe().to_string()
    ai_response = ""
    table_data = None

    if response_type in ["text", "both"]:
        messages = [
            SystemMessage(content="You are a data analyst AI. Answer queries based on the dataset."),
            HumanMessage(content=f"Dataset Summary:\n{summary}\n\nUser Query: {query}")
        ]
        try:
            response = llm.invoke(messages)
            cleaned = BeautifulSoup(response.content, "html.parser").get_text()
            lines = [re.sub(r"[`#]", "", line.strip()) for line in cleaned.splitlines() if line.strip()]
            table_start = next((i for i, l in enumerate(lines) if "Name" in l and "Position" in l), len(lines))
            ai_response = "\n".join(lines[:table_start])
            header = lines[table_start].split()
            table_data = [dict(zip(header, line.split(None, len(header) - 1))) for line in lines[table_start+1:]]
        except Exception as e:
            ai_response = str(e)

    chart = generate_visualization(df) if response_type in ["chart", "both"] else None

    return JsonResponse({
        "response": ai_response,
        "data": table_data,
        "visualization": chart
    })


# @api_view(['POST'])
# def analyze_data(request):
#     file = request.FILES.get('file')
#     if not file:
#         return JsonResponse({"error": "No file uploaded"}, status=400)

#     query = request.data.get('query')
#     if not query:
#         return JsonResponse({"error": "Query is required"}, status=400)

#     response_type = request.data.get('response_type', 'both').lower()

#     file_path = default_storage.save(f"temp/{file.name}", file)

#     try:
#         df = pd.read_csv(os.path.join(settings.MEDIA_ROOT, file_path))
#         summary = df.describe().to_string()
#     except Exception:
#         return JsonResponse({"error": "Invalid CSV file"}, status=400)

#     ai_response = None
#     table_data = None


    

#     if response_type in ["text", "both"]:
#         messages = [
#             SystemMessage(content="You are a data analyst AI. Answer queries based on the dataset. Answer Dateframe respone."),
#             HumanMessage(content=f"Dataset Summary:\n{summary}\n\nUser's Question: {query}")
#         ]
#         try:
#             response = llm.invoke(messages)
#             ai_response = response.content

#             soup = BeautifulSoup(ai_response, "html.parser")
#             cleaned_text = soup.get_text()

#             cleaned_text = re.sub(r"[`#]", "", cleaned_text)
#             cleaned_text = re.sub(r"\bhere( is)?\b[:\-]?", "", cleaned_text, flags=re.IGNORECASE)

#             lines = [line.strip() for line in cleaned_text.splitlines() if line.strip()]

#             table_start = 0
#             for i, line in enumerate(lines):
#                 if re.search(r"\bName\b.*\bPosition\b", line):  # Look for the header line
#                     table_start = i
#                     break

#             explanation = "\n".join(lines[:table_start]).strip()
#             table_lines = lines[table_start:]

#             header = table_lines[0].split()
#             rows = [line.split(None, len(header) - 1) for line in table_lines[1:]]
#             table_data = [dict(zip(header, row)) for row in rows if len(row) == len(header)]

#             ai_response = explanation

#         except Exception as e:
#             ai_response = f"Error processing query: {str(e)}"


#     base64_chart = None
#     if response_type in ["chart", "both"]:
#         base64_chart = generate_visualization(df)

#     response_data = {
#     "response": ai_response
#         }
#     if table_data:
#             response_data["data"] = table_data
#     if base64_chart:
#             response_data["visualization"] = base64_chart

#     return JsonResponse(response_data)

# @api_view(['POST'])
# def process_visualization(request):
#     import matplotlib
#     matplotlib.use('Agg')  # Use non-GUI backend for server

#     vis_type = request.data.get('type')
#     x_column = request.data.get('x_column')
#     y_column = request.data.get('y_column')
    
#     if not vis_type or not x_column:
#         return JsonResponse({"error": "Visualization type and X column are required"}, status=400)

#     df = pd.read_json(request.session.get('uploaded_df'))

#     plt.figure(figsize=(8, 5))

#     try:
#         if vis_type == "bar":
#             sns.barplot(x=df[x_column], y=df[y_column] if y_column else None)
#         elif vis_type == "scatter":
#             if not y_column:
#                 return JsonResponse({"error": "Y column required for scatter plot"}, status=400)
#             sns.scatterplot(x=df[x_column], y=df[y_column])
#         elif vis_type == "histogram":
#             sns.histplot(df[x_column], kde=True)
#         elif vis_type == "pie":
#             df[x_column].value_counts().plot.pie(autopct='%1.1f%%')
#         else:
#             return JsonResponse({"error": "Invalid visualization type"}, status=400)

#         plt.title(f"{vis_type.capitalize()} Plot")
#         buffer = BytesIO()
#         plt.savefig(buffer, format="png", bbox_inches="tight")
#         plt.close()

#         encoded_image = base64.b64encode(buffer.getvalue()).decode()
#         return JsonResponse({"image": encoded_image})
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

@api_view(['POST'])
def process_visualization(request):
    file_path = request.data.get("file_path")
    chart_type = request.data.get("chart_type")
    columns = request.data.get("columns", [])

    if not file_path or not chart_type or not columns:
        return JsonResponse({"error": "Missing input"}, status=400)

    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    try:
        df = pd.read_csv(full_path)
    except:
        return JsonResponse({"error": "CSV error"}, status=400)

    plt.figure(figsize=(8, 5))
    try:
        if chart_type == "bar":
            sns.barplot(x=df[columns[0]], y=df[columns[1]])
        elif chart_type == "scatter":
            sns.scatterplot(x=df[columns[0]], y=df[columns[1]])
        elif chart_type == "pie":
            df.groupby(columns[0]).size().plot.pie(autopct='%1.1f%%')
        elif chart_type == "histogram":
            sns.histplot(df[columns[0]], kde=True)
        else:
            return JsonResponse({"error": "Invalid chart type"}, status=400)

        plt.title(f"{chart_type.capitalize()} Chart")
        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        plt.close()
        base64_img = base64.b64encode(buffer.getvalue()).decode()
        return JsonResponse({"visualization": base64_img})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def generate_visualization(df):
    """
    Generates a histogram and returns the base64-encoded chart.
    """
    num_cols = df.select_dtypes(include=['number']).columns
    if len(num_cols) == 0:
        return None
   
    plt.figure(figsize=(8, 5))
    sns.histplot(df[num_cols[0]], kde=True)
    plt.title(f"Distribution of {num_cols[0]}")
    plt.xlabel(num_cols[0])
    plt.ylabel("Count")

    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    plt.close()
   
    base64_chart = base64.b64encode(buffer.getvalue()).decode()
    return base64_chart

	

