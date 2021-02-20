from datetime import datetime

from flask import abort, flash, redirect, render_template, request, url_for
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_login import LoginManager, UserMixin, current_user ,AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as serial

from report import app, db, login_manager 




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




class User(db.Model , UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone_no = db.Column(db.Integer , unique=True , nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    reports = db.relationship('Report', backref='author', lazy=True)


    def get_reset_token(self , expires_sec=1800):
        s = serial(app.config['SECRET_KEY'] , expires_sec)
        return s.dumps({ 'user_id' : self.id }).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = serial(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']

        except:
            return None
        return User.query.get(user_id)


    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}', '{self.id}')"


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_reported = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status  = db.Column(db.String(100) , nullable=False , default = 'Investigating')
   

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_reported}')"

 




class MyModelView(ModelView):
    def is_accessible(self):
        if current_user.id == 1:
            return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
class UserView(ModelView):
        can_delete = False 
        can_create = False 
        can_view_details = True
        column_exclude_list = ['password']
        column_searchable_list = ['username', 'email']
        column_filters = ['id' , 'username']
        def is_accessible(self):
            if current_user.id == 1:
                return current_user.is_authenticated
        def inaccessible_callback(self, name, **kwargs):
            return redirect(url_for('login'))
class ReportView(ModelView):
        page_size = 10  
        can_delete = False 
        can_create = False 
        can_view_details = True
        column_exclude_list = ['content']
        column_searchable_list = ['title']
        column_filters = ['id' , 'title']
        column_editable_list = ['status']
        def is_accessible(self):
            if current_user.id == 1:
                return current_user.is_authenticated
        def inaccessible_callback(self, name, **kwargs):
            return redirect(url_for('login'))



officers = Admin(app , name = '' , template_mode='bootstrap4')            
officers.add_view(UserView(User, db.session))
officers.add_view(ReportView(Report, db.session)) 
