from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, PasswordField, TextAreaField, IntegerField, SelectField, StringField
from wtforms.validators import Required, Length, NumberRange, InputRequired, DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed
from app.models import User, discip, role, groups

class LoginForm(FlaskForm):
    login = StringField('login',validators=[DataRequired(message='Поле \"Логин\" обязательно для заполнения')])
    Password = PasswordField('Password',validators=[DataRequired(message='Поле \"Пароль\" обязательно для заполнения')])
##    checkbox = BooleanField('checkbox', default = False)
    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(login=self.login.data).first()
        if user is None:
            self.login.errors.append('Неверный логин или пароль.')
            return False
        
        if not (user.verify_password(self.Password.data)):
            self.Password.errors.append('Неверный логин или пароль')
            return False
        
        self.user = user
        return True

class UploadForm(FlaskForm):
    file_upload = FileField('Обзор',validators=[FileRequired(message='Выберите файл'),
                            FileAllowed(['jpg','jpeg','png','bmp','gif',
                                         'doc','docx','xls','xlsx','odt','odg','ods','odp','rtf', 
                                         'pdf','txt','ppt','pptx','pps','ppsx',
                                         'zip','rar'],
                                        'Недопустимый тип файла')])
    file_info = TextAreaField('file_info',validators=[Length(min=0,max=500)])
    discip_info = SelectField('discip_info',coerce=int)
    role_info = SelectField('role',coerce=int)
    pertain_info = SelectField('pertain',coerce=int)
    eduYear_info = IntegerField('eduYear',validators=[NumberRange(min=1,max=4),DataRequired(message='Выберите курс')])
    spec_info = SelectField('spec_info',coerce=int,validators=[DataRequired(message='Выберите специальность')])
    tmtypes_ = SelectField('tmtypes',coerce=int)
    public_check = BooleanField('publiccheck',default=False)

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        if self.pertain_info.data==1 and self.tmtypes_.data != 1:
            self.pertain_info.errors.append('Невозможно выбрать принадлежность \"По колледжу\" и тип отличный от \"По колледжу\"')
            return False
        if self.pertain_info.data==2 and self.tmtypes_.data > 21:
            self.pertain_info.errors.append('Невозможно выбрать принадлежность \"По специальности\" и данный тип файла')
            return False
        
        return True

class EditForm(FlaskForm):
    file_info = TextAreaField('file_info',validators=[Length(min=0,max=500)])
    discip_info = SelectField('discip_info',coerce=int)
    role_info = SelectField('role',coerce=int)
    pertain_info = SelectField('pertain',coerce=int)
    eduYear_info = IntegerField('eduYear',validators=[NumberRange(min=1,max=4),DataRequired(message='Выберите курс')])
    spec_info = SelectField('spec_info',coerce=int,validators=[DataRequired(message='Выберите специальность')])
    tmtypes_ = SelectField('tmtypes',coerce=int)
    public_check = BooleanField('publiccheck',default=False)
    
    def __init__(self,fileid,*args,**kwargs):
        Form.__init__(self,*args,**kwargs)
        self.fileid = fileid
    
    def validate(self):
        if not FlaskForm.validate(self):
            return False
        if self.pertain_info.data==1 and self.tmtypes_.data != 1:
            self.pertain_info.errors.append('Невозможно выбрать принадлежность \"По колледжу\" и тип отличный от \"По колледжу\"')
            return False
        
        return True

class AddUserForm(FlaskForm):
    spec_info = SelectField('spec_info',coerce=int)
    method_info = SelectField('method_info',coerce=int)
    role_info = SelectField('role_info',coerce=int)
    group_info = SelectField('group_info',coerce=int)
    name_ = StringField('name',validators=[DataRequired(message='Укажите ФИО'),Length(min=1,max=50)])
    login_ = StringField('login',validators=[DataRequired(message='Укажите логин')])
    password_ = PasswordField('Password',validators=[DataRequired(message='Укажите пароль')])
    
    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        if (self.role_info.data == 1) and (self.spec_info.data == 2) and (self.method_info.data == 2):
            self.spec_info.errors.append('Выберите специальность!')
            return False
        
        if (self.role_info.data == 2) and (self.spec_info.data == 2) and (self.method_info.data == 2):
            self.spec_info.errors.append('Выберите цикловую комиссию!')
            return False
               
        if self.group_info.data == 2 and self.role_info.data == 1:
            self.spec_info.errors.append('Выберите группу!')
            return False
        
        return True

class EditUserFormS(FlaskForm):
    spec_info = SelectField('spec_info',coerce=int)
    name_ = StringField('name',validators=[DataRequired(message='Укажите ФИО'),Length(min=1,max=50)])
    group_info = SelectField('group_info',coerce=int)
    login_ = StringField('login',validators=[DataRequired(message='Укажите логин')])
    
    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        if self.spec_info.data == 2:
            self.spec_info.errors.append('Выберите специальность!')
            return False
        
        if self.group_info.data == 2:
            self.spec_info.errors.append('Выберите группу!')
        
        return True

class EditUserFormP(FlaskForm):
    method_info = SelectField('method_info',coerce=int)
    name_ = StringField('name',validators=[DataRequired(message='Укажите ФИО'),Length(min=1,max=50)])
    login_ = StringField('login',validators=[DataRequired(message='Укажите логин')])
    role_info = SelectField('role_info',coerce=int)
    
    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        if self.method_info.data == 2:
            self.method_info.errors.append('Выберите цикловую комиссию!')
            return False
        
        return True

class EditUserPassForm(FlaskForm):
    password_ = PasswordField('Password',validators=[DataRequired(message='Укажите пароль')])
    
    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        
        return True    

class AddDiscipForm(FlaskForm):
    spec_info = SelectField('spec_info',coerce=int)
    name = StringField('name',validators=[DataRequired(message='Укажите название')])
    eduYear_info = IntegerField('eduYear',validators=[NumberRange(min=1,max=4),DataRequired(message='Выберите курс')])
        
    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        if (self.spec_info.data == 2):
            self.spec_info.errors.append('Выберите специальность!')
            return False
        
        return True

class EditDiscipForm(FlaskForm):
    name = StringField('name',validators=[DataRequired(message='Укажите название')])
    eduYear_info = IntegerField('eduYear',validators=[NumberRange(min=1,max=4),DataRequired(message='Выберите курс')])
    spec_info = SelectField('spec_info',coerce=int)

    def __init__(self,discipid,*args,**kwargs):
        FlaskForm.__init__(self,*args,**kwargs)
        self.discipid = discipid
    
    def validate(self):
        if not FlaskForm.validate(self):
            return False

        if (self.spec_info.data == 2):
            self.spec_info.errors.append('Выберите специальность!')
            return False

        return True

class AddSpecForm(FlaskForm):
    name = StringField('name',validators=[DataRequired(message='Укажите название')])

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        
        return True

class EditSpecForm(FlaskForm):
    name = StringField('name',validators=[DataRequired(message='Укажите название')])

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        
        return True

class AddMethodForm(FlaskForm):
    name = StringField('name',validators=[DataRequired(message='Укажите название')])

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        
        return True

class EditMethodForm(FlaskForm):
    name_ = StringField('name',validators=[DataRequired(message='Укажите название')])

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        
        return True


class AddGroupsForm(FlaskForm):
    spec_info = SelectField('spec_info',coerce=int)
    name = StringField('name',validators=[DataRequired(message='Укажите название')])
        
    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        if (self.spec_info.data == 2):
            self.spec_info.errors.append('Выберите специальность!')
            return False
        
        return True

class EditGroupsForm(FlaskForm):
    name = StringField('name',validators=[DataRequired(message='Укажите название')])
    spec_info = SelectField('spec_info',coerce=int)

    def __init__(self,discipid,*args,**kwargs):
        FlaskForm.__init__(self,*args,**kwargs)
        self.discipid = discipid
    
    def validate(self):
        if not FlaskForm.validate(self):
            return False

        if (self.spec_info.data == 2):
            self.spec_info.errors.append('Выберите специальность!')
            return False

        return True

class EditMessage(FlaskForm):
    message = TextAreaField('message',validators=[Length(min=0,max=700)])

    def validate(self):
        if not FlaskForm.validate(self):
            return False

        return True

class AcceptForm(FlaskForm):
    
    def validate(self):
        if not FlaskForm.validate(self):
            return False

        return True
