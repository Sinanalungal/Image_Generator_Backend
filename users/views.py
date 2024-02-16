from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import permissions,status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserCreateSerializer,UserSerializer,PromptSerializer,ProfilePicSerializer
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

class ProfilePicView(APIView):
    def patch(self,request):
        try :
            image_data=request.data.get('profile')
        except KeyError:
            return Response({'error':'there is nothing to update'}, status=status.HTTP_400_BAD_REQUEST)
        
        if image_data is None:
            return Response({'error': 'There is nothing to update'}, status=status.HTTP_400_BAD_REQUEST) 
        
        try:
            image_serializer=ProfilePicSerializer(data=request.data)
        except ValueError:
            return Response({'error':'given wrong data'}, status=status.HTTP_400_BAD_REQUEST)

        if not image_serializer.is_valid():
            return Response({"error":image_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        try :
            user_data=User.objects.get(email=request.data.get('email'))
        except User.DoesNotExist:
            return Response({"error":'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_data.profile = image_serializer.validated_data.get('profile')
        user_data.save()

        return Response({'updated_image':user_data.profile.url}, status=status.HTTP_200_OK)
    
        
