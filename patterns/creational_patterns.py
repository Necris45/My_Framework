import copy
import quopri
from behavioral_patterns import ConsoleWriter, Subject
from architectural_system_pattern_unit_of_work import DomainObject
# from architectural_system_pattern_mappers import PatientMapper
import sqlite3
import threading


# абстрактный пользователь
class User:
    def __init__(self, name):
        self.name = name


# Специалист
class Specialist(User):
    pass


# Пациент
class Patient(User, DomainObject):

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


class PatientMapper:

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.table_name = 'patient'

    def all(self):
        statement = f'SELECT * from {self.table_name}'
        self.cursor.execute(statement)
        result = []
        for item in self.cursor.fetchall():
            id, name = item
            patient = Patient(name)
            patient.id = id
            result.append(patient)
        return result

    def find_by_id(self, id):
        statement = f"SELECT id, name FROM {self.table_name} WHERE id=?"
        self.cursor.execute(statement, (id,))
        result = self.cursor.fetchone()
        if result:
            return Patient(*result)
        else:
            raise RecordNotFoundException(f'record with id={id} not found')

    def insert(self, obj):
        statement = f"INSERT INTO {self.table_name} (name) VALUES (?)"
        self.cursor.execute(statement, (obj.name,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.table_name} SET name=? WHERE id=?"
        # Где взять obj.id? Добавить в DomainModel? Или добавить когда берем объект из базы
        self.cursor.execute(statement, (obj.name, obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.table_name} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)


# class CategoryMapper(PatientMapper):
#
#     def __init__(self, connection):
#         super().__init__(connection)
#         self.cursor = connection.cursor()
#         self.table_name = 'category'
#
#     def all(self):
#         statement = f'SELECT * from {self.table_name}'
#         self.cursor.execute(statement)
#         result = []
#         for item in self.cursor.fetchall():
#             id, name = item
#             category = Category(name)
#             category.id = id
#             result.append(category)
#         return result
#
#     def find_by_id(self, id):
#         statement = f"SELECT id, name FROM {self.table_name} WHERE id=?"
#         self.cursor.execute(statement, (id,))
#         result = self.cursor.fetchone()
#         if result:
#             return Patient(*result)
#         else:
#             raise RecordNotFoundException(f'record with id={id} not found')


class DbCommitException(Exception):
    def __init__(self, message):
        super().__init__(f'Db commit error: {message}')


class DbUpdateException(Exception):
    def __init__(self, message):
        super().__init__(f'Db update error: {message}')


class DbDeleteException(Exception):
    def __init__(self, message):
        super().__init__(f'Db delete error: {message}')


class RecordNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(f'Record not found: {message}')


connection = sqlite3.connect('patterns.sqlite')


# архитектурный системный паттерн - Data Mapper
class MapperRegistry:
    mappers = {
        'patient': PatientMapper,
        # 'category': CategoryMapper
    }

    @staticmethod
    def get_mapper(obj):
        if isinstance(obj, Patient):
            return PatientMapper(connection)
        # if isinstance(obj, Category):
        #     return CategoryMapper(connection)

    @staticmethod
    def get_current_mapper(name):
        return MapperRegistry.mappers[name](connection)
