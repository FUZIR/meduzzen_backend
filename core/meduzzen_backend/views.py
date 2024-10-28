import logging
from django.http import JsonResponse

logger = logging.getLogger("meduzzen_backend")
def health_check(request):
    return JsonResponse(data={
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    })