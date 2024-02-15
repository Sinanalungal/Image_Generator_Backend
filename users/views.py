from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import permissions,status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserCreateSerializer,UserSerializer,PromptSerializer
from .models import UserAccount
from openai import OpenAI
from image_generator.settings import OPEN_AI_API_KEY



User=get_user_model()

class RegisterView(APIView):
    def post(self,request):
        data=request.data
        print(data)

        serializer=UserCreateSerializer(data=data)

        if not serializer.is_valid():
            print(serializer.errors)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
        user=serializer.create(serializer.validated_data)
        user=UserSerializer(user)

        return Response(user.data,status=status.HTTP_201_CREATED)


class RetrieveUserView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def get(self,request):
        user=request.user
        user=UserSerializer(user)
        return Response(user.data,status=status.HTTP_200_OK)
    

    
class ImageView(APIView):
    def post(self, request):
        prompt_serializer = PromptSerializer(data=request.data)
        
        if prompt_serializer.is_valid():
            prompt_value = prompt_serializer.validated_data.get('prompt', '')
            # print(prompt_value)

            client = OpenAI(api_key=OPEN_AI_API_KEY)

            response = client.images.generate(
                model="dall-e-2",
                prompt=prompt_value,  
                size="512x512",
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url
            # print(image_url)
            return Response({"image":image_url}, status=status.HTTP_200_OK)
        else:
            return Response({"err":prompt_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
