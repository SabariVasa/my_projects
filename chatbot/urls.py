# from django.urls import path
# from .views import send_otp, verify_otp, chat_view

# urlpatterns = [
#     path("api/send-otp/", send_otp, name="send_otp"),
#     path("api/verify-otp/", verify_otp, name="verify_otp"),
#     path("api/chat/", chat_view, name="chat"),
# ]

from django.urls import path
from .views import start_game,chatbot_api, send_otp,verify_otp,llm_chat,roll_dice,register_user,login_user
from .llm import chatbot_response
from .web_scrabing import web_scrape
from django.urls import path
from .analysis import process_prompt, process_visualization,upload_preview
# from rest_framework_simplejwt.auth import TokenRefreshView


urlpatterns = [
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('send-otp/', send_otp, name='otp'),
    path('start/', start_game),
    path('roll/<int:game_id>/', roll_dice),
    path('chat/', llm_chat, name='llm_chat'),
    path('llm_chatbot/', chatbot_response, name='chatbot-response'),
    # path('upload/', analyze_data, name="file-upload"),
    path('upload_preview/', upload_preview, name="file-preview"),
    path('process_prompt/', process_prompt, name="process_prompt"),
    path('process_visualization/', process_visualization),
    path('web_scrab/', web_scrape, name='web_scrabing'),
    path('chatbot/', chatbot_response, name='chatbot_response'),
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('send-otp/', send_otp, name='otp'),
    path('chat/', chatbot_api, name='chatbot_api'),
]