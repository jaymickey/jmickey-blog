from flask.ext.admin import AdminIndexView, BaseView, expose

class View1(AdminIndexView):
  @expose('/')
  def index(self):
    return 'Hello World!'