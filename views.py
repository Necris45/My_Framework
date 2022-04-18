from datetime import date

from hospis_framework.templator import render
from patterns.creational_patterns import Engine, Logger

site = Engine()
logger = Logger('main')


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


# контроллер - список записей
class AppointmentList:
    def __call__(self, request):
        logger.log('Список записей')
        try:
            category = site.find_category_by_id(int(request['request_params']['id']))
            return '200 OK', render('appointment_list.html', objects_list=category.appointments, name=category.name, id=category.id)
        except KeyError:
            return '200 OK', 'No courses have been added yet'


# контроллер - создать запись
class CreateAppointment:
    category_id = -1

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
                site.appointments.append(appointment)

            return '200 OK', render('appointment_list.html', objects_list=category.appointments,
                                    name=category.name, id=category.id)

        else:
            try:
                self.category_id = int(request['request_params']['id'])
                category = site.find_category_by_id(int(self.category_id))

                return '200 OK', render('create_appointment.html', name=category.name, id=category.id)
            except KeyError:
                return '200 OK', 'No categories have been added yet'


# контроллер - создать категорию
class CreateCategory:
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
class CategoryList:
    def __call__(self, request):
        logger.log('Список категорий')
        return '200 OK', render('category_list.html', objects_list=site.categories)


# контроллер - копировать запись
class CopyAppointment:
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
class CurrentAppointment:
    def __call__(self, request):
        return '200 OK', render('appointment_date_time.html', data=date.today())
