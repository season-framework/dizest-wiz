import datetime

class Controller:
    def __init__(self, wiz):
        pass
        
    def join(self, wiz, data):
        room = data['id']
        wiz.flask_socketio.join_room(room, namespace=wiz.socket.namespace)

    def leave(self, wiz, data):
        room = data['id']
        wiz.flask_socketio.leave_room(room, namespace=wiz.socket.namespace)

    def connect(self, wiz, data):
        pass

    def disconnect(self, wiz, data):            
        pass