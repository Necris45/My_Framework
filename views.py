from datetime import date

from hospis_framework.templator import render
from patterns.creational_patterns import Engine, Logger, MapperRegistry
from patterns.structural_patterns import AppRoute, Debug
from patterns.behavioral_patterns import EmailNotifier, SmsNotifier, TemplateView, ListView, CreateView, BaseSerializer
from architectural_system_pattern_unit_of_work import UnitOfWork

site = Engine()
logger = Logger('main')
email_notifier = EmailNotifier()
sms_notifier = SmsNotifier()
UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_registry(MapperRegistry)

routes = {}


@AppRoute(routes=routes, url='/')
class Index:
    @Debug(name='Index')
    def __call__(self, request):
        return '200 OK', render('index.html', objects_list=site.categories)


@AppRoute(routes=routes, url='/about/')
class About:
    @Debug(name='About')
    def __call__(self, request):
        return '200 OK', render('about.html')


class NotFound404:
    @Debug(name='NotFound404')
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'


@AppRoute(routes=routes, url='/registration/')
class Registration:
    @Debug(name='Registration')
    def __call__(self, request):
        return '200 OK', 'Register here'


@AppRoute(routes=routes, url='/auth/')
class Auth:
    @Debug(name='Auth')
    def __call__(self, request):
        return '200 OK', 'Enter on site here'


@AppRoute(routes=routes, url='/appointment/')
class Appointment:
    @Debug(name='Appointment')
    def __call__(self, request):
        return '200 OK', 'doctor\'s appointment'


@AppRoute(routes=routes, url='/apr_appointment/')
class AproveAppointment:
    @Debug(name='AproveAppointment')
    def __call__(self, request):
        return '200 OK', 'accept chosen time'


@AppRoute(routes=routes, url='/dec_appointment/')
class DeclineAppointment:
    @Debug(name='DeclineAppointment')
    def __call__(self, request):
        return '200 OK', 'Decline chosen time'


# контроллер - список записей
@AppRoute(routes=routes, url='/appointment-list/')
class AppointmentList:
    @Debug(name='AppointmentList')
    def __call__(self, request):
        logger.log('Список записей')
        try:
            category = site.find_category_by_id(int(request['request_params']['id']))
            return '200 OK', render('appointment_list.html', objects_list=category.appointments, name=category.name,
                                    id=category.id)
        except KeyError:
            return '200 OK', 'No courses have been added yet'


# контроллер - создать запись
@AppRoute(routes=routes, url='/create-appointment/')
class CreateAppointment:
    category_id = -1

    @Debug(name='CreateAppointment')
    def __call__(self, request):
        if request['method'] == 'POST':
            # метод пост
            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category = None
            if self.category_id != -1:
                category = site.find_category_by_id(int(self.category_id))

                appointment = site.create_appointment('first', name, category)
                # Добавляем наблюдателей на курс
                appointment.observers.append(email_notifier)
                appointment.observers.append(sms_notifier)
                site.appointments.append(appointment)

            return '200 OK', render('appointment_list.html', objects_list=category.appointments,
                                    name=category.name, id=category.id)

        else:
            self.category_id = int(request['request_params']['id'])
            category = site.find_category_by_id(int(self.category_id))
            return '200 OK', render('create_appointment.html', name=category.name, id=category.id)


# контроллер - создать категорию
@AppRoute(routes=routes, url='/create-category/')
class CreateCategory:
    @Debug(name='CreateCategory')
    def __call__(self, request):
        if request['method'] == 'POST':
            # метод пост
            print(request)
            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category_id = data.get('category_id')

            category = None
            if category_id:
                category = site.find_category_by_id(int(category_id))

            new_category = site.create_category(name, category)

            site.categories.append(new_category)

            return '200 OK', render('index.html', objects_list=site.categories)
        else:
            categories = site.categories
            return '200 OK', render('create_category.html', categories=categories)


# контроллер - список категорий
@AppRoute(routes=routes, url='/category-list/')
class CategoryList:
    @Debug(name='CategoryList')
    def __call__(self, request):
        logger.log('Список категорий')
        return '200 OK', render('category_list.html', objects_list=site.categories)


# контроллер - копировать запись
@AppRoute(routes=routes, url='/copy-appointment/')
class CopyAppointment:
    @Debug(name='CopyAppointment')
    def __call__(self, request):
        request_params = request['request_params']

        try:
            name = request_params['name']
            old_appointment = site.get_appointment(name)
            if old_appointment:
                new_name = f'copy_{name}'
                new_appointment = old_appointment.clone()
                new_appointment.name = new_name
                site.appointments.append(new_appointment)

            return '200 OK', render('appointment_list.html', objects_list=site.appointments)
        except KeyError:
            return '200 OK', 'No courses have been added yet'


# контроллер - Расписания
@AppRoute(routes=routes, url='/appointment_time/')
class CurrentAppointment:
    @Debug(name='CurrentAppointment')
    def __call__(self, request):
        return '200 OK', render('appointment_date_time.html', data=date.today())


@AppRoute(routes=routes, url='/patient-list/')
class PatientListView(ListView):
    template_name = 'patient_list.html'

    def get_queryset(self):
        mapper = MapperRegistry.get_current_mapper('patient')
        return mapper.all()


@AppRoute(routes=routes, url='/create-patient/')
class PatientCreateView(CreateView):
    template_name = 'create_patient.html'

    def create_obj(self, data: dict):
        name = data['name']
        name = site.decode_value(name)
        new_obj = site.create_user('patient', name)
        site.patients.append(new_obj)
        new_obj.mark_new()
        UnitOfWork.get_current().commit()


@AppRoute(routes=routes, url='/add-patient/')
class AddPatientByAppointmentCreateView(CreateView):
    template_name = 'add_patient.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['appointments'] = site.appointments
        context['patients'] = site.patients
        return context

    def create_obj(self, data: dict):
        appointment_name = data['appointment_name']
        appointment_name = site.decode_value(appointment_name)
        appointment = site.get_appointment(appointment_name)
        patient_name = data['patient_name']
        patient_name = site.decode_value(patient_name)
        patient = site.get_patient(patient_name)
        appointment.add_patient(patient)


@AppRoute(routes=routes, url='/api/')
class AppointmentApi:
    @Debug(name='AppointmentApi')
    def __call__(self, request):
        return '200 OK', BaseSerializer(site.appointments).save()
