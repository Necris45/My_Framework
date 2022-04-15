from hospis_framework.templator import render


class Index:
    def __call__(self, request):
        return '200 OK', render('index.html', data=request.get('data', None))


class About:
    def __call__(self, request):
        return '200 OK', render('about.html')


class NotFound404:
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'


class Registration:
    def __call__(self, request):
        return '200 OK', 'Register here'


class Auth:
    def __call__(self, request):
        return '200 OK', 'Enter on site here'


class Appointment:
    def __call__(self, request):
        return '200 OK', 'doctor\'s appointment'


class Aprove_appointment:
    def __call__(self, request):
        return '200 OK', 'accept chosen time'


class Decline_appointment:
    def __call__(self, request):
        return '200 OK', 'Decline chosen time'
