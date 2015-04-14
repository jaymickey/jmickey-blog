from flask.ext.admin import AdminIndexView, BaseView, expose
from flask.ext.login import current_user
from flask import redirect, url_for


class AdminIndex(AdminIndexView):
  
  @expose('/')
  def index(self):
    if not current_user.is_authenticated():
      return redirect(url_for('login'))
    return super(AdminIndex, self).index()