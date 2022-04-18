from datetime import date
from views import Index, About, Registration, Auth, Appointment, Aprove_appointment, Decline_appointment, \
    CopyAppointment, CategoryList, CreateCategory, CreateAppointment, AppointmentList, CurrentAppointment


# front controller
def hidden_front(request):
    request['date'] = date.today()


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
    '/appointment-list/': AppointmentList(),
    '/create-appointment/': CreateAppointment(),
    '/create-category/': CreateCategory(),
    '/category-list/': CategoryList(),
    '/copy-appointment/': CopyAppointment(),
    '/appointment_time/': CurrentAppointment(),
}
