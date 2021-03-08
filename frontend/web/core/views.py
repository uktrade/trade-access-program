from django.shortcuts import render


def handler404(request, exception):
    return render(request, 'core/404.html', status=404)


def handler500(request, *args, **argv):
    return render(request, 'core/500.html', status=500)  # noqa