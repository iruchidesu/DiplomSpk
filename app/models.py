from passlib.apps import custom_app_context as pwd_context
from datetime import datetime, timedelta
from app import db
from app import app


class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    id_spec = db.Column(db.Integer,db.ForeignKey('spec.id'))
    id_method = db.Column(db.Integer,db.ForeignKey('method.id'))
    id_role = db.Column(db.Integer,db.ForeignKey('role.id'))
    id_group = db.Column(db.Integer,db.ForeignKey('groups.id'))
    name = db.Column(db.String(50))
    login = db.Column(db.String(50),unique=True)
    password_hash = db.Column(db.String(128))
    files_ = db.relationship('files',backref='user_file',lazy='dynamic')
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def hash_password(self,password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self,password):
        return pwd_context.verify(password,self.password_hash)

    def followed_files(self,id_disc):
        return files.query.filter(files.id_discip==id_disc)

    def followed_files_stud(self,discip_id):
        return files.query.join(discip,files.id_discip==discip.id).\
               join(spec,discip.id_spec==spec.id).\
               join(User,spec.id==User.id_spec).filter(files.id_discip==discip_id,
                                                          User.id==self.id,
                                                          User.id_role==files.id_role)

    def followed_files_prep(self,id_user):
        return files.query.join(discip,files.id_discip==discip.id).\
               join(spec,discip.id_spec==spec.id).\
               join(User,files.id_user==User.id).\
               join(method,User.id_method==method.id).\
               join(tmtypes,files.id_tmtypes==tmtypes.id).\
               filter(files.id_user==id_user).\
               add_columns(spec.name.label('specname'),
                           discip.name.label('discipname'),
                           method.id.label('methodid'),
                           spec.id.label('specid'),
                           tmtypes.name.label('tmtypename'))

    def accepted_files(self):
        return files.query.join(discip,files.id_discip==discip.id).\
               join(spec,discip.id_spec==spec.id).\
               join(User,files.id_user==User.id).\
               filter(files.accept==0,files.id_pertain!=1,files.public==1).\
               add_columns(spec.name.label('specname'),
                           discip.name.label('discipname'),
                           spec.id.label('specid')).\
               order_by('files.id_tmtypes')
    
    def followed_discip_stud(self):
        return db.session.query(discip).select_from(files).\
               join(discip,files.id_discip==discip.id).\
               join(spec,discip.id_spec==spec.id).\
               join(User,User.id_spec==spec.id).filter(User.id==self.id,files.id_role==1,files.public==1).\
               group_by('discip_id').add_columns(db.func.count(files.id).label('cnt'))
    
    def followed_discip_prep(self):
        return db.session.query(discip).select_from(files).\
               join(discip,files.id_discip==discip.id).\
               join(User,files.id_user==User.id).\
               join(spec,discip.id_spec==spec.id).\
               join(method,User.id_method==method.id).\
               group_by('discip_id').add_columns(db.func.count(files.id).label('cnt')).\
               add_column(spec.name.label('spec_name')).order_by('spec_name','discip_name')

    def spec_admin(self):
        return spec.query.filter(spec.id!=2)

    def discip_admin(self,spec_id):
        return discip.query.filter(discip.id_spec==spec_id).order_by('name')

    def files_admin(self,disc_id):
        return files.query.filter(files.id_discip==disc_id)

    def files_admin_all(self):
        return files.query.order_by('name')

    def method_admin(self):
        return method.query.filter(method.id!=2)

    def user_method_admin(self,method_id):
        return User.query.filter(User.id_method==method_id)

    def groups_admin(self,spec_id):
        return groups.query.filter(groups.id_spec==spec_id).order_by('name')

    def users_admin(self,groups_id):
        return User.query.filter(User.id_group==groups_id)

    def spec_files(self,spec_id):
        return files.query.join(discip,files.id_discip==discip.id).\
               join(spec, spec.id==discip.id_spec).filter(spec.id==spec_id)

    def statistic(self,s):
        return files.query.filter(files.timestamp>datetime.today()-timedelta(days=s),
                                  files.timestamp<datetime.today()-timedelta(days=s-1)).\
               add_column(db.func.count(files.id).label('cnt'))

    def statistic_accept(self,s):
        return files.query.filter(files.timestamp>datetime.today()-timedelta(days=s),
                                         files.timestamp<datetime.today()-timedelta(days=s-1),
                                         files.accept==1).\
               add_column(db.func.count(files.id).label('cnt'))

    def __repr__(self):
        return '<User %r>' % self.name

class discip(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    id_spec = db.Column(db.Integer,db.ForeignKey('spec.id'))
    name = db.Column(db.String(50))
    eduYear = db.Column(db.Integer)
    files_ = db.relationship('files',backref='disc_files',lazy='dynamic')

    def get_id(self):
        return self.id
    
    def __repr__(self):
        return '<%r>' % self.name

class files(db.Model):
    id = db.Column(db.BigInteger,primary_key=True)
    id_user = db.Column(db.Integer,db.ForeignKey('user.id'))
    id_discip = db.Column(db.Integer,db.ForeignKey('discip.id'))
    id_role = db.Column(db.Integer,db.ForeignKey('role.id'))
    id_tmtypes = db.Column(db.Integer,db.ForeignKey('tmtypes.id'))
    id_pertain = db.Column(db.Integer,db.ForeignKey('pertain.id'))
    name = db.Column(db.String(200))
    name_hash = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime)
    info = db.Column(db.String(500))
    eduYear = db.Column(db.Integer)
    public = db.Column(db.Integer)
    accept = db.Column(db.Integer)

    def get_id(self):
        return self.id
    
    def __repr__(self):
        return '<%r>' % self.name

class spec(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(200))
    users = db.relationship('User',backref='special_stud',lazy='dynamic')
    discips = db.relationship('discip',backref='special_disc',lazy='dynamic')
    groups = db.relationship('groups',backref='special_group',lazy = 'dynamic')
    
    def get_id(self):
        return self.id

class role(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(15))
    files_ = db.relationship('files',backref='role_file',lazy='dynamic')
    users = db.relationship('User',backref='role_user',lazy='dynamic')

    def get_id(self):
        return self.id
    
class method(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50))
    users = db.relationship('User',backref='user_method',lazy='dynamic')

    def get_id(self):
        return self.id

class groups(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    id_spec = db.Column(db.Integer,db.ForeignKey('spec.id'))
    name = db.Column(db.String(10))
    users = db.relationship('User',backref='user_group',lazy='dynamic')

    def get_id(self):
        return self.id

class message(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    message = db.Column(db.String(700))
    timestamp = db.Column(db.DateTime)

    def get_id(self):
        return self.id
    
class tmtypes(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))
    id_pertain = db.Column(db.Integer,db.ForeignKey('pertain.id'))
    files_1 = db.relationship('files',backref='file_tmtypes',lazy='dynamic')
    
    def get_id(self):
        return self.id

class pertain(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))
    files_2 = db.relationship('files',backref='file_pertain',lazy='dynamic')
    tmtypes_1 = db.relationship('tmtypes',backref='tmtypes_pertain',lazy='dynamic')
    
    def get_id(self):
        return self.id
