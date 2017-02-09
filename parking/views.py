from django.http import HttpResponse


def home(request):
    """
    Homepage for parking demo.

    :param request: HttpRequest object
    :return: HttpResonse object
    """
    return HttpResponse(
        "<h1>Welcome to StornCo Parking</h1>Get yourself some space, man!"
    )
