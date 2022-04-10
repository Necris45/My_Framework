from datetime import date
from views import Index, About, Registration, Auth, Appointment, Aprove_appointment, Decline_appointment


# front controller
def hidden_front(request):
    request['data'] = date.today()


def key_front(request):
    request['key'] = 'key'


fronts = [hidden_front, key_front]

routes = {
    '/': Index(),
    '/about/': About(),
    '/registration/': Registration(),
    '/auth/': Auth(),
    '/appointment/': Appointment(),
    '/apr_appointment/': Aprove_appointment(),
    '/dec_appointment/': Decline_appointment(),
}
