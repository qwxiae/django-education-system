from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@staff_member_required
def tinymce_upload(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        path = default_storage.save(f"tinymce/{file.name}", file)
        url = default_storage.url(path)
        return JsonResponse({"location": url})
    return JsonResponse({"error": "No file"}, status=400)
