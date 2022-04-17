import copy
import quopri


# абстрактный пользователь
class User:
    pass


# преподаватель
class Specialist(User):
    pass


# студент
class Patient(User):
    pass


# порождающий паттерн Абстрактная фабрика - фабрика пользователей
class UserFactory:
    types = {
        'patient': Patient,
        'specialist': Specialist
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_):
        return cls.types[type_]()


# порождающий паттерн Прототип - прием (у специалиста)
class AppointmentPrototype:
    # прототип курсов обучения

    def clone(self):
        return copy.deepcopy(self)


class Appointment(AppointmentPrototype):
    def __init__(self, specialist_category, specialist_name, date, time, duration):
        self.specialist_category = specialist_category
        self.specialist_name = specialist_name
        self.appointment_date = date
        self.appointment_time = time
        self.appointment_duration = duration
        self.specialist_category.appointment.append(self)


# прием у терапевта
class TerapevtAppointment(Appointment):
    pass


# прием у невролога
class NeurologAppointment(Appointment):
    pass


# прием у хирурга
class ChirurgAppointment(Appointment):
    pass


# Категория специалиста (специализация)
class SpecialistCategory:
    # реестр?
    auto_id = 0

    def __init__(self, specialist_category):
        self.id = SpecialistCategory.auto_id
        SpecialistCategory.auto_id += 1
        self.specialist_category = specialist_category
        self.specialists_lst = []

    def specialist_count(self):
        result = len(self.specialists_lst)
        if self.specialist_category:
            result += self.specialist_category.course_count()
        return result


# порождающий паттерн Абстрактная фабрика - фабрика записи к специалисту
class AppointmentFactory:
    types = {
        'terapevt': TerapevtAppointment,
        'neurolog': NeurologAppointment,
        'chirurg': ChirurgAppointment
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_, specialist_category, specialist_name, date, time, duration):
        return cls.types[type_](specialist_category, specialist_name, date, time, duration)


# Основной интерфейс проекта
class Engine:
    def __init__(self):
        self.specialists = []
        self.patients = []
        self.appointments = []
        self.specialist_categories = []

    @staticmethod
    def create_user(type_):
        return UserFactory.create(type_)

    @staticmethod
    def create_category(specialist_category):
        return SpecialistCategory(specialist_category)

    def find_category_by_id(self, category_id):
        for item in self.specialist_categories:
            print('item', item.id)
            if item.id == category_id:
                return item
        raise Exception(f'Нет категории с id = {id}')

    @staticmethod
    def create_appointment(type_, specialist_category, specialist_name, date, time, duration):
        return AppointmentFactory.create(type_, specialist_category, specialist_name, date, time, duration)

    def get_appointment(self, specialist_category, specialist_name, date, time):
        for item in self.appointments:
            if item.specialist_category == specialist_category and item.specialist_name == specialist_name and \
                    item.date == date and item.time == time:
                return item
        return None

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = quopri.decodestring(val_b)
        return val_decode_str.decode('UTF-8')


# порождающий паттерн Синглтон
class SingletonByName(type):

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instance:
            return cls.__instance[name]
        else:
            cls.__instance[name] = super().__call__(*args, **kwargs)
            return cls.__instance[name]


class Logger(metaclass=SingletonByName):

    def __init__(self, name):
        self.name = name

    @staticmethod
    def log(text):
        print('log--->', text)
