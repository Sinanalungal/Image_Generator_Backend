from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from openai import OpenAI
from image_generator.settings import OPEN_AI_API_KEY
from .serializers import (
    UserCreateSerializer,
    UserSerializer,
    PromptSerializer,
    ProfilePicSerializer,
    UserDataSerializer,
    UpdateUserEdit,
    UpdateUserPassword
)
from django.db.models import Q

User = get_user_model()

class RegisterView(APIView):
    """
    API endpoint for user registration.
    """

    def post(self, request):
        """
        Handle POST request for user registration.
        """
        data = request.data
        serializer = UserCreateSerializer(data=data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.create(serializer.validated_data)
        user = UserSerializer(user)

        return Response(user.data, status=status.HTTP_201_CREATED)

class RetrieveUserView(APIView):
    """
    API endpoint for retrieving user details.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Handle GET request for retrieving user details.
        """
        user = request.user
        user = UserSerializer(user)
        return Response(user.data, status=status.HTTP_200_OK)

class ImageView(APIView):
    """
    API endpoint for generating images based on prompts.
    """

    def post(self, request):
        """
        Handle POST request for generating images.
        """
        prompt_serializer = PromptSerializer(data=request.data)

        if prompt_serializer.is_valid():
            prompt_value = prompt_serializer.validated_data.get('prompt', '')
            client = OpenAI(api_key=OPEN_AI_API_KEY)

            response = client.images.generate(
                model="dall-e-2",
                prompt=prompt_value,
                size="512x512",
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url
            return Response({"image": image_url}, status=status.HTTP_200_OK)
        else:
            return Response({"err": prompt_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        

class ProfilePicView(APIView):
    def patch(self, request):
        print(request.data)
        try:
            image_data = request.data.get('profile')
        except KeyError:
            return Response({'error': 'There is nothing to update'}, status=status.HTTP_400_BAD_REQUEST)

        if image_data is None:
            return Response({'error': 'There is nothing to update'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            image_serializer = ProfilePicSerializer(data=request.data)
            if image_serializer.is_valid():
                user_data = User.objects.get(email=request.data.get('email'))
                user_data.profile = image_serializer.validated_data.get('profile')
                user_data.save()
                return Response({'updated_image': user_data.profile.url}, status=status.HTTP_200_OK)
            else:
                return Response({"error": image_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({"error": 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

    # def put(self, request,id):
    #     try:
    #         user_obj = User.objects.get(id=id)
    #     except User.DoesNotExist:
    #         return Response("User profile not found", status=status.HTTP_404_NOT_FOUND)

    #     serializer = ProfilePicSerializer(user_obj, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RetrieveUserData(APIView):
    def post(self,request):
        email = request.data.get('email')
        try:
            data=User.objects.get(email = email)
        except User.DoesNotExist:
            return Response({"error": 'There is no user'}, status=status.HTTP_400_BAD_REQUEST)
        user = UserDataSerializer(data)
        return Response(user.data, status=status.HTTP_200_OK)
    

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username
        token['phone_number'] = user.phone_number
        token['email'] = user.email
        token['isSuperuser'] = user.is_superuser
        token['profile'] = user.profile.url if user.profile else None


        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    
class UserDataUpdateView(APIView):
    def post(self,request):
        try:
            user_obj=User.objects.get(email=request.data.get('email'))
        except User.DoesNotExist:
            return Response({"error": "User does not exist"},status=status.HTTP_400_BAD_REQUEST)
        
        if request.data.get('password'):
            serializer = UpdateUserEdit(user_obj,data=request.data)
        else:
            serializer = UpdateUserEdit(user_obj,data=request.data)

        if serializer.is_valid():
            if request.data.get('password'):
                serializerpassword=UpdateUserPassword(user_obj,data=request.data)
                if serializerpassword.is_valid()  and (request.data['password']).strip()!='':
                    user_obj.set_password(request.data.get('password'))
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class AdminDataFetch(APIView):
    def post(self,request):
        try:
            admin=User.objects.get(email=request.data.get('email'))
            if admin.is_superuser:
                allData=User.objects.all().exclude(is_superuser=True).order_by('id')
                serializer=UserDataSerializer(allData,many=True)
                return Response(serializer.data,status=status.HTTP_200_OK)
            else:
                return Response({"error": "You are not an admin"},status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"},status=status.HTTP_400_BAD_REQUEST)
        
class EditUserData(APIView):
    def put(self,request,id):

        print(request.data)

        print(id)
        try:
            user_obj=User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({"error":'User does not exist'},status=status.HTTP_400_BAD_REQUEST)
        try:
            if "username" in request.data and (request.data["username"]).strip()!='':
                user_obj.username=request.data["username"]
            if "email" in request.data and (request.data["email"]).strip()!='':
                user_obj.email=request.data["email"]
            if "phone_number" in request.data and (request.data["phone_number"]).strip()!='':
                user_obj.phone_number=request.data["phone_number"]
            if 'is_listed' in request.data:
                user_obj.is_listed=request.data["is_listed"]
            if "password" in request.data and (request.data["password"]).strip()!='':
                user_obj.set_password(request.data["password"])
            user_obj.save()
            datas=User.objects.all().exclude(is_superuser=True).order_by('id')
            serializer=UserDataSerializer(datas,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except ValueError:
            return Response({"error":'Something wentwrong'},status=status.HTTP_400_BAD_REQUEST)

class DeleteUser(APIView):
    def delete(self,request,id):
        try:
            user_obj=User.objects.get(id=id)
            user_obj.delete()
            usersData=User.objects.all().exclude(is_superuser=True).order_by('id')
            serialize=UserDataSerializer(usersData,many=True)
            return Response(serialize.data,status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error":"User Does not exist"},status=status.HTTP_400_BAD_REQUEST)
        
class SearchQuery(APIView):
    def post(self,request):
        search=(request.data.get('search')).strip()
        # print(search)
        try:
            if search!='':
                usersData=User.objects.filter(Q(username__icontains=search) | Q(email__icontains=search) | Q(phone_number__icontains=search)).exclude(is_superuser=True).all().order_by('id')
            else:
                usersData=User.objects.all().exclude(is_superuser=True).order_by('id')
            serialize=UserDataSerializer(usersData,many=True)
            return Response(serialize.data,status=status.HTTP_200_OK)
        except:
            return Response({"error":"Something went wrong"},status=status.HTTP_400_BAD_REQUEST)