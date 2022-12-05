
'''
It contains all the server related files which are responsible for creating the end-points which can be accessed via the frontend. It also contains static web pages which can be viewed by the user.
'''


from src.User import routes


def getRoutes():
    return routes.healthCheck()
