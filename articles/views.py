from django.shortcuts import render
from django.http import JsonResponse
# URL에서 호출하는 함수의 첫 번째 파라미터는 항상 request
# -request: 사용자의 요청 정보가 모두 들어있다. 
def index(request):
    print("index 함수 호출됨!")
    print(f'request = {request}')
    return JsonResponse({"응답": "articles의 index 함수"})