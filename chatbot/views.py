# import json
# import os
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt

# # Load chatbot data from JSON file
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# JSON_PATH = os.path.join(BASE_DIR, "chatbot/chat_bot.json")

# with open(JSON_PATH, "r") as file:
#     CHATBOT_DATA = json.load(file)

# def get_response(user_input):
#     """Fetch chatbot response based on user input."""
#     user_input = user_input.lower()
    
#     for category, responses in CHATBOT_DATA.items():
#         if isinstance(responses, dict):
#             for key, value in responses.items():
#                 if isinstance(value, dict):
#                     for sub_key, sub_value in value.items():
#                         if sub_key in user_input:
#                             return sub_value
#                 elif key in user_input:
#                     return value
#     return "I'm sorry, I don't understand that."

# @csrf_exempt
# def chatbot_api(request):
#     """API to handle chatbot requests."""
#     if request.method == "POST":
#         data = json.loads(request.body)
#         user_input = data.get("message", "")
#         response = get_response(user_input)
#         return JsonResponse({"response": response})
#     return JsonResponse({"error": "Invalid request"}, status=400)

import json
import random
import os
import smtplib
import pyttsx3
import speech_recognition as sr
from email.message import EmailMessage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from dotenv import load_dotenv
from rest_framework.response import Response
from rest_framework.decorators import api_view
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Game
from rest_framework import status
# from .serializers import GameSerializer
from rest_framework.views import APIView
import random
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.response import Response
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from .serializers import RegisterSerializer, LoginSerializer
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from mongoengine.queryset.visitor import Q
from .llm_apikeys import api_key
# from .utils import get_tokens_for_mongo_user
# from _utils_ import get_tokens_for_mongo_user

# Inside login_user view:


def generate_token(user):
    payload = {
        'id': str(user.id),
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

engine = pyttsx3.init()

otp_storage = {}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, "chatbot/chat_bot.json")

load_dotenv()
os.environ['OPENAI_API_KEY'] = api_key

llm = ChatOpenAI(api_key=api_key, temperature=0.7)
memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm, memory=memory)

@csrf_exempt
@api_view(["POST"])
def llm_chat(request):
    user_message = request.data.get("message", "")
    if not user_message:
        return JsonResponse({"error": "Message is required"}, status=400)

    response = conversation.predict(input=user_message)
    return JsonResponse({"response": response})

with open(JSON_PATH, "r") as file:
    CHATBOT_DATA = json.load(file)

def get_response(user_input):
    """Fetch chatbot response based on user input."""
    user_input = user_input.lower()
    
    for category, responses in CHATBOT_DATA.items():
        if isinstance(responses, dict):
            for key, value in responses.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        if sub_key in user_input:
                            return sub_value
                elif key in user_input:
                    return value
    return "I'm sorry, I don't understand that."

@csrf_exempt
def send_otp(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            if not email:
                return JsonResponse({"error": "Email is required"}, status=400)

            otp = str(random.randint(100000, 999999))
            otp_storage[email] = otp

            # Send OTP via email
            sender_email = "sabarivasan323@gmail.com"
            app_password = "rjop xqxh rpba erpg"
            msg = EmailMessage()
            msg["Subject"] = "Your OTP for Verification"
            msg["From"] = sender_email
            msg["To"] = email
            msg.set_content(f"Your OTP is: {otp}")

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, app_password)
                server.send_message(msg)

            return JsonResponse({"message": "OTP sent successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Invalid request method"}, status=400)

@csrf_exempt
def verify_otp(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            entered_otp = data.get("otp")

            if otp_storage.get(email) == entered_otp:
                del otp_storage[email]
                return JsonResponse({"message": "OTP verified successfully"})
            return JsonResponse({"error": "Invalid OTP"}, status=400)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

# Chatbot API
@csrf_exempt
def chatbot_api(request):
    """API to handle chatbot requests."""
    if request.method == "POST":
        data = json.loads(request.body)
        user_input = data.get("message", "")
        response = get_response(user_input)
        return JsonResponse({"response": response})
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
@api_view(['GET'])
# def start_game(request):
#     game = Game.objects.create()
#     return Response(GameSerializer(game).data)
def start_game(request):
    try:
        # Your existing code here
        return JsonResponse({"message": "Game started"})
    except Exception as e:
        print("Error in start_game:", str(e))
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@api_view(['POST'])
def roll_dice(request, game_id):
    game = Game.objects.get(id=game_id)
    dice_value = random.randint(1, 6)
    game.move_player(dice_value)
    return Response({'dice_value': dice_value, 'player_position': game.player_position})

User = get_user_model()

@api_view(['POST'])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully"}, status=HTTP_200_OK)
    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_user(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        # print(CustomUser.objects.get(username), 'username')
        try:
            user = CustomUser.objects.get(Q(username=username) | Q(email=username))
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid username"}, status=HTTP_400_BAD_REQUEST)

        if user.check_password(password):
          refresh = RefreshToken.for_user(user)
          return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "username": user.username,
                "email": user.email,
                "emessage": "Login successful",
                "estatus": bool(True)
            }, status=HTTP_200_OK)
        return Response({"emessage": "Invalid password","estatus":bool(False)}, status=HTTP_200_OK)

    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)



# otp_storage = {}

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# JSON_PATH = os.path.join(BASE_DIR, "chatbot/chat_bot.json")

# load_dotenv()
# api_key = "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"

# llm = ChatOpenAI(api_key=api_key, temperature=0.7)
# memory = ConversationBufferMemory()
# conversation = ConversationChain(llm=llm, memory=memory)

# @csrf_exempt
# @api_view(["POST"])
# def chatbot_api(request):
#     user_message = request.data.get("message", "")
#     if not user_message:
#         return JsonResponse({"error": "Message is required"}, status=400)

#     response = conversation.predict(input=user_message)
#     return JsonResponse({"response": response})

# with open(JSON_PATH, "r") as file:
#     CHATBOT_DATA = json.load(file)

# def get_response(user_input):
#     """Fetch chatbot response based on user input."""
#     user_input = user_input.lower()
    
#     for category, responses in CHATBOT_DATA.items():
#         if isinstance(responses, dict):
#             for key, value in responses.items():
#                 if isinstance(value, dict):
#                     for sub_key, sub_value in value.items():
#                         if sub_key in user_input:
#                             return sub_value
#                 elif key in user_input:
#                     return value
#     return "I'm sorry, I don't understand that."

# @csrf_exempt
# def send_otp(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             email = data.get("email")
#             if not email:
#                 return JsonResponse({"error": "Email is required"}, status=400)

#             otp = str(random.randint(100000, 999999))
#             otp_storage[email] = otp

#             # Send OTP via email
#             sender_email = "sabarivasan323@gmail.com"
#             app_password = "rjop xqxh rpba erpg"
#             msg = EmailMessage()
#             msg["Subject"] = "Your OTP for Verification"
#             msg["From"] = sender_email
#             msg["To"] = email
#             msg.set_content(f"Your OTP is: {otp}")

#             with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
#                 server.login(sender_email, app_password)
#                 server.send_message(msg)

#             return JsonResponse({"message": "OTP sent successfully"})
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)
    
#     return JsonResponse({"error": "Invalid request method"}, status=400)

# # Function to verify OTP
# @csrf_exempt
# def verify_otp(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             email = data.get("email")
#             entered_otp = data.get("otp")

#             if otp_storage.get(email) == entered_otp:
#                 del otp_storage[email]
#                 return JsonResponse({"message": "OTP verified successfully"})
#             return JsonResponse({"error": "Invalid OTP"}, status=400)
        
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)

#     return JsonResponse({"error": "Invalid request method"}, status=400)

# # Chatbot API
# @csrf_exempt
# def medical_chatbot(request):
#     """API to handle chatbot requests."""
#     if request.method == "POST":
#         data = json.loads(request.body)
#         user_input = data.get("message", "")
#         response = get_response(user_input)
#         return JsonResponse({"response": response})
#     return JsonResponse({"error": "Invalid request"}, status=400)