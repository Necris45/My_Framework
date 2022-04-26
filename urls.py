from datetime import date


# front controller
def hidden_front(request):
    request['date'] = date.today()


def key_front(request):
    request['key'] = 'key'


fronts = [hidden_front, key_front]
