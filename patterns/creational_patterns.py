import copy
import quopri
from behavioral_patterns import ConsoleWriter, Subject

# абстрактный пользователь
class User:
    def __init__(self, name):
        self.name = name


# Специалист
class Specialist(User):
    pass


# Пациент
class Patient(User):
    def __init__(self, name):
        self.appointments = []
        super().__init__(name)


# порождающий паттерн Абстрактная фабрика - фабрика пользователей
class UserFactory:
    types = {
        'patient': Patient,
        'specialist': Specialist
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_, name):
        return cls.types[type_](name)


# порождающий паттерн Прототип - запись
class AppointmentPrototype:
    # прототип записи к специалистам

    def clone(self):
        return copy.deepcopy(self)


class Appointment(AppointmentPrototype, Subject):

    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.category.appointments.append(self)
        self.patients = []
        super().__init__()

    def __getitem__(self, item):
        return self.patients[item]

    def add_patient(self, patient: Patient):
        self.patients.append(patient)
        patient.appointments.append(self)
        self.notify()


# Первичный прием
class FirstAppointment(Appointment):
    pass


# Повторный прием
class RepitAppointment(Appointment):
    pass


# Категория
class Category:
    # реестр?
    auto_id = 0

    def __init__(self, name, category):
        self.id = Category.auto_id
        Category.auto_id += 1
        self.name = name
        self.category = category
        self.appointments = []

    def appointment_count(self):
        result = len(self.appointments)
        if self.category:
            result += self.category.appointment_count()
        return result


# порождающий паттерн Абстрактная фабрика - фабрика записей
class AppointmentFactory:
    types = {
        'first': FirstAppointment,
        'repit': RepitAppointment
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_, specialist, category):
        return cls.types[type_](specialist, category)


# Основной интерфейс проекта
class Engine:
    def __init__(self):
        self.specialists = []
        self.patients = []
        self.appointments = []
        self.categories = []

    @staticmethod
    def create_user(type_, name):
        return UserFactory.create(type_, name)

    @staticmethod
    def create_category(name, category=None):
        return Category(name, category)

    def find_category_by_id(self, id):
        for item in self.categories:
            print('item', item.id)
            if item.id == id:
                return item
        raise Exception(f'Нет категории с id = {id}')

    @staticmethod
    def create_appointment(type_, name, category):
        return AppointmentFactory.create(type_, name, category)

    def get_appointment(self, name):
        for item in self.appointments:
            if item.name == name:
                return item
        return None

    def get_patient(self, name) -> Patient:
        for item in self.patients:
            if item.name == name:
                return item

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

    def __init__(self, name, writer=ConsoleWriter()):
        self.name = name
        self.writer = writer

    def log(self, text):
        text = f'log---> {text}'
        self.writer.write(text)
