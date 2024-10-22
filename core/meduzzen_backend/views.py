from django.http import JsonResponse


def health_check(request):
    return JsonResponse(data={
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    })