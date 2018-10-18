from django.http import JsonResponse
from django.db.models import F

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Level, KryptosUser
from api.serializers import LevelSerializer
from .decorators import is_logged_in, set_cookies

from datetime import datetime

@is_logged_in
@api_view(['GET'])
def ask(request):

    user = request.session['user']
    kuser, created = KryptosUser.objects.get_or_create(user_id=user)
    # TODO: Send message to websocket on new user.
    level = Level.objects.filter(level=kuser.level)[0]
    serializer = LevelSerializer(level)
    return Response(serializer.data)


@is_logged_in
@api_view(['POST'])
def answer(request):
    answer = request.POST['answer']

    try:
        user = request.session['user']
        kuser = KryptosUser.objects.get(user_id=user)
        level = Level.objects.get(level=kuser.level)

        if answer == level.answer:
            # Here we use an F expression : Read more about it in Django docs.
            kuser.level = F('level') + 1
            kuser.last_anstime = datetime.now()
            kuser.save()
            response = {'answer': 'Correct'}

        else:
            response = {'answer': 'Wrong'}

        return JsonResponse(response)

    except Exception as e:
        resp = {'Error': 'Internal Server Error'}
        return JsonResponse(resp, status=500)


@is_logged_in
@api_view(['GET'])
def leaderboard(request):
    try:
        data = []
        kusers = KryptosUser.objects.all()
        rank = 1
            
        for kuser in kusers:
            dict={}
            dict['user_id'] = kuser.user_id
            dict['rank'] = rank
            rank += 1
            data.append(dict)
            
            return JsonResponse({'data': data})
        
    except:
        resp = {'Error': 'Internal Server Error'}
        return JsonResponse(resp, status=500)



@is_logged_in
@api_view(['GET'])
def myrank(request):
    try:
        user = request.session.get('user', False)
        if user:
            rank = KryptosUser.objects.get(user_id = user).rank
            return JsonResponse({'rank': rank})
        else:
            return JsonResponse({'Error': 'User not logged in'}, status=403)

    except:
        return JsonResponse({'Error': 'Internal Server Error'}, status=500)

