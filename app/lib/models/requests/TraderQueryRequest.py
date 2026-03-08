from flask_restful_swagger import swagger


@swagger.model
class TraderQueryRequest:
    def __init__(self, user_name, secret):
        self.user_name = user_name
        self.secret = secret
