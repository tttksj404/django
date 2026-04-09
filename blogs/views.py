from django.shortcuts import render

# 게시글 정보를 변수에 저장
# - 서버가 켜질 때 자동으로 실행
posts = [
    {
        "post_id": 1,
        "title": "블로그 동아리에 대해서",
        "content": "나의 깊은 내면과 마주하는 공간입니다"
    },
    {
        "post_id": 2,
        "title": "김지윤은 누구인가?",
        "content": "지윤님은 가짜 뉴스 전문가입니다. 은수님을 잘 놀립니다."
    },
]

# Create your views here.
def index(request):
    greeting = "안녕이다"
    view_count = 5 

    context = {
        'greeting' : greeting,
        'view_count' : view_count,
        'posts' : posts,
    }
    return render(request, 'blogs/index.html' , context)


