from django.shortcuts import render


def error_view(request, exception=None, status=500):
    if status == 404:
        message = "Page not found"
    elif status == 403:
        message = "You do not have permission to access this page"
    elif status == 400:
        message = "Bad request"
    else:
        message = "Something went wrong. Please try again later."

    return render(
        request,
        "error.html",
        {
            "message": message,
            "status": status,
        },
        status=status,
    )