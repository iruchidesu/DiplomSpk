import os
import hashlib
import random
from flask import render_template, flash, redirect, session, url_for, request, g, Response, send_from_directory, jsonify, json
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from app.forms import LoginForm, UploadForm, EditForm, AddUserForm, AddDiscipForm, AddSpecForm, AddMethodForm, EditDiscipForm, EditUserFormS, EditUserFormP, EditMethodForm, EditSpecForm, AddGroupsForm, EditGroupsForm, EditMessage, EditUserPassForm, AcceptForm
from app.models import User, files, discip, spec, role, method, groups, message, tmtypes, pertain
#from werkzeug import secure_filename
from datetime import datetime, timedelta
from app.momentjs import momentjs

def getMD5sum(filename):
    """
    возвращает md5-хэш от "имя файла + случайное число"

    filename - имя файла
    """
    random.seed()
    m = hashlib.md5()
    name_ = filename + str(random.random())
    m.update(name_.encode('utf8'))
    return m.hexdigest()

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/accessdenied')
def accessdenied():
    return render_template('accessdenied.html')

@app.route('/select', methods = ['GET'])
@login_required
def select():
    """
    возвращает список предметов для выбранной специальности в json-формате
    """
    id_spec_ = request.args.get('spec_info',0,type=int)
    discip_info = discip.query.filter(discip.id_spec==id_spec_).order_by('name')
    result = {}
    for d in discip_info:
        result[str(d.id)] = {"discip_id":str(d.id),"discip_name":d.name}
    return jsonify(result)

@app.route('/selecttype', methods = ['GET'])
@login_required
def selecttype():
    """
    возвращает список типов файлов для выбранной принадлежности в json-формате
    """
    id_pertain_ = request.args.get('pertain_info',0,type=int)
    tmtypes_ = tmtypes.query.filter(tmtypes.id_pertain==id_pertain_).order_by('name')
    result = {}
    for d in tmtypes_:
        result[str(d.id)] = {"tmtypes_id":str(d.id),"tmtypes_name":d.name}
    return jsonify(result)

@app.route('/')
@app.route('/index')
@login_required
def index():
    """
    Первая страница,
    для администратора и методиста содержит статистику загруженных файлов,
    для остальных - сообщение от администрации
    """
    user = g.user.name
    role_ = g.user.id_role
    follow_discip = g.user.followed_discip_stud()
    follow_discip_prep = g.user.followed_discip_prep()
    discip_ = discip.query.filter(discip.id!=2).first()
    spec_ = spec.query.filter(spec.id!=2).first()
    message_ = message.query
   
    res = []
    res_accept = []
    for s in [5,4,3,2,1]:
        stat = g.user.statistic(s)
        stat_accept = g.user.statistic_accept(s)
        for count in stat:    
            res.append(count.cnt)
        for count_accept in stat_accept:    
            res_accept.append(count_accept.cnt)
    
    return render_template('index.html',
        title = 'Главная',
        name = user,
        role = role_,
        follow_discip = follow_discip,
        follow_discip_prep = follow_discip_prep,
        disciplin = discip_,
        spec_ = spec_,
        message = message_,
        stat = res,
        stat_accept = res_accept)

@app.route('/login',methods=['GET','POST'])
def login():
    """
    форма входа
    """
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user)
        return redirect(request.args.get("next") or url_for("index"))
    return render_template('login.html', 
        title = 'Вход',
        form = form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/upload/',methods=['GET','POST'])
@login_required
def upload():
    """
    загрузка файлов
    """
    user = g.user.name
    role_user = g.user.id_role
    if role_user == 1:
        return redirect(url_for('accessdenied'))
    form = UploadForm()

    form.spec_info.choices = [(g.id,g.name) for g in spec.query.order_by('name')]

    if role_user == 2:
        form.role_info.choices = [(1,'Студент'),(2,'Преподаватель')]
    else:
        form.role_info.choices = [(g.id,g.name) for g in role.query]

    form.discip_info.choices = [(g.id,g.name) for g in discip.query.order_by('name')]

    if role_user == 2:
        form.tmtypes_.choices = [(g.id,g.name) for g in tmtypes.query.filter_by(id_pertain=3)]
    if role_user == 4:
        form.tmtypes_.choices = [(g.id,g.name) for g in tmtypes.query.filter(tmtypes.id_pertain!=1)]
    if role_user == 3 or role_user == 5:
        form.tmtypes_.choices = [(g.id,g.name) for g in tmtypes.query]

    if role_user == 2 or role_user == 4:    
        form.pertain_info.choices = [(g.id,g.name) for g in pertain.query.filter(pertain.id!=1).order_by('id')]
    else:
        form.pertain_info.choices = [(g.id,g.name) for g in pertain.query.order_by('id')]

    if role_user == 2:
        form.pertain_info.data = 3
            
##    discip_ = discip.query.filter(discip.id == form.discip_info.data).first()
##    spec_ = spec.query.filter(spec.id == discip_.id_spec).first()
##        
##    if not os.path.exists(app.config['UPLOAD_FOLDER'] + str(spec_.id)):
##        os.mkdir(app.config['UPLOAD_FOLDER'] + str(spec_.id))
##
##    directory_spec = str(spec_.id) + '\\'
##    if not os.path.exists(directory_spec + str(discip_.id)):
##        os.mkdir(app.config['UPLOAD_FOLDER'] + directory_spec + str(discip_.id))
##            
##    directory = directory_spec + str(discip_.id) + '\\'
##    file.save(os.path.join(app.config['UPLOAD_FOLDER'] + directory, filename_hash))
    
    if form.validate_on_submit():
        upload_file = request.files.getlist('file_upload')
        for file in upload_file:
            filename = file.filename
            extension = filename.split('.')[-1]
            filename_hash = getMD5sum(filename) + '.' + extension
            fileinfo = form.file_info.data
            
            if form.pertain_info.data == 1:
                accepted = 1
                discip_info_form = 369
            else:
                accepted = 1
                discip_info_form = form.discip_info.data
                
            if form.role_info.data == 1:
                accepted = 1
            else:
                accepted = 1
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename_hash))
            file_ = files(id_user = g.user.id,
                          id_discip = discip_info_form,
                          id_role = form.role_info.data,
                          id_tmtypes = form.tmtypes_.data,
                          id_pertain = form.pertain_info.data,
                          name = filename,
                          name_hash = filename_hash,
                          timestamp = datetime.utcnow(),
                          info = fileinfo,
                          eduYear = form.eduYear_info.data,
                          public = form.public_check.data,
                          accept = accepted)
            db.session.add(file_)
            db.session.commit()
            flash('Файл %s успешно загружен!'%filename)
        form.file_info.data = ''
    else:
        if role_user == 4 or role_user == 5:
            form.pertain_info.data = 2
            form.tmtypes_.data = 2
        form.role_info.data = 2
        filename = None
    return render_template('upload.html',
                           title = 'Загрузка файлов',
                           name=user,
                           role=role_user,
                           form = form,
                           filename = filename)

@app.route('/uploads/<file_id>/<filename>')
@login_required
def uploaded_file(file_id,filename):
    """
    возвращает файлы
    
    file_id - id файла
    filename - имя файла
    """
    file_name = files.query.filter(files.id==file_id).first()
    if file_name is None:
        return render_template('404.html')
    if (file_name.id_role==2 or file_name.id_role==3) and g.user.id_role==1:
        return redirect(url_for('accessdenied'))
    return send_from_directory(app.config['UPLOAD_FOLDER'],file_name.name_hash)

@app.route('/discips/<int:id_discip>')
@login_required
def discips(id_discip):
    """
    список предметов и загруженных в них файлов для пользователя

    id_discip - id выбранного предмета
    """
    user = g.user.name
    role_ = g.user.id_role
    file_ = g.user.followed_files(id_discip)
    files_stud = g.user.followed_files_stud(id_discip)
    follow_discip = g.user.followed_discip_stud()
    #follow_discip_prep = g.user.followed_discip_prep()
    
    return render_template('discips.html',
        title = 'Файлы',
        name = user,
        role = role_,
        files = file_,
        files_stud = files_stud,
        follow_discip = follow_discip)#,
        #follow_discip_prep = follow_discip_prep)

@app.route('/filesprep',methods = ['GET', 'PUT'])
@login_required
def filesprep():
    """
    список преподавателей и загруженных ими файлов для преподавателя

    """
    user = g.user.name
    role_ = g.user.id_role
    if role_ == 1:
        return redirect(url_for('accessdenied'))
    user_id = request.args.get('user_info',0,type=int)
    file_ = g.user.followed_files_prep(user_id)
    tmtype = tmtypes.query
    spec_ = spec.query.join(discip,discip.id_spec==spec.id).\
               join(files,files.id_discip==discip.id).\
               join(User,files.id_user==User.id).filter(spec.id!=2,User.id==user_id)
    discips_ = discip.query.join(files,files.id_discip==discip.id).\
               join(User,files.id_user==User.id).filter(files.id_user==user_id,
                                                           files.id_pertain==3).\
               order_by('discip_name')
    userlist = User.query.filter(User.id!=g.user.id,User.id_role!=1).order_by('name')
    
    return render_template('filesprep.html',
        title = 'Список загруженных файлов',
        name = user,
        role = role_,
        files = file_,
        users = userlist,
        user_id = user_id,
        tmtype = tmtype,
        specs = spec_,
        discips = discips_)

@app.route('/filescoll')
@login_required
def filescoll():
    """
    список файлов с принадлежностью "по колледжу"
    
    """
    user = g.user.name
    role_ = g.user.id_role
    if role_ == 1:
        return redirect(url_for('accessdenied'))
    file_ = files.query.filter_by(id_pertain=1)
    tmtype = tmtypes.query
    
    return render_template('filesprepcoll.html',
        title = 'Список загруженных файлов',
        name = user,
        role = role_,
        files = file_,
        tmtype = tmtype)

@app.route('/filespec')
@app.route('/filespec/<int:spec_id>')
@login_required
def filespec(spec_id=7):
    """
    список файлов общих для всей специальности
    
    """
    user = g.user.name
    role_ = g.user.id_role
    if role_ == 1:
        return redirect(url_for('accessdenied'))
    file_ = files.query.join(discip,files.id_discip==discip.id).\
            join(spec,spec.id==discip.id_spec).filter(files.id_pertain==2,spec.id==spec_id)
    spec_ = spec.query.filter(spec.id!=2)
    tmtype = tmtypes.query
    cur_spec = spec.query.filter_by(id=spec_id).first()
    
    return render_template('filesprepspec.html',
        title = 'Список загруженных файлов',
        name = user,
        role = role_,
        files = file_,
        specs = spec_,
        current_spec = cur_spec,
        tmtype = tmtype,
        user_id = g.user.id)

@app.route('/specs')
@app.route('/specs/<int:id_spec>')
@login_required
def specsadmin(id_spec=7):
    """
    список специальностей и предметов в них для админа

    id_spec - id выбранной специальности
    """
    user = g.user.name
    role = g.user.id_role
    if role == 1 or role == 2 or role == 4:
        return redirect(url_for('accessdenied'))
    spec_ = g.user.spec_admin()
    discip_ = g.user.discip_admin(id_spec)
    current_spec = spec.query.filter(spec.id==id_spec).first()
    
    return render_template('specsadmin.html',
        title = 'Просмотр специальностей',
        name = user,
        role = role,
        specadm = spec_,
        cur_spec = current_spec,
        discipadm = discip_)

@app.route('/acceptfiles')
@login_required
def acceptfiles():
    """
    список файлов на утверждение
    """
    user = g.user.name
    cur_user_role = g.user.id_role
    if cur_user_role == 1 or cur_user_role == 2 or cur_user_role == 4:
        return redirect(url_for('accessdenied'))
    tmtype = tmtypes.query
    files_ = g.user.accepted_files()
    return render_template('acceptfiles.html',
                           title = 'Файлы на утверждение',
                           name = user,
                           role = cur_user_role,
                           files = files_,
                           tmtype = tmtype)

@app.route('/accept/<file_id>',methods=['GET','POST'])
@login_required
def accept(file_id):
    """
    форма утверждения файла

    file_id - id утверждаемого файла
    """
    user = g.user.name
    role_user = g.user.id_role
    if role_user == 1 or role_user == 2 or role_user == 4:
        return redirect(url_for('accessdenied'))
    form = AcceptForm()
    file = files.query.filter(files.id==file_id).first()
    title = 'Утверждение файла ' + file.name
    if form.validate_on_submit():
        file_update = db.session.query(files).filter(files.id==file_id).update({"accept":1})
        db.session.commit()
        flash('Файл успешно утвержден')
        return redirect(url_for('acceptfiles'))
    return render_template('accept.html',
                           title = title,
                           name=user,
                           role = role_user,
                           form=form,
                           file = file)

@app.route('/profile/<userlogin>')
@login_required
def profile(userlogin):
    """
    страница профиля пользователя

    userlogin - логин пользователя
    """
    cur_user_role = g.user.id_role
    user = User.query.filter_by(login=userlogin).first()
    if cur_user_role == 1 and userlogin != g.user.login:
        return redirect(url_for('accessdenied'))
    if user is None:
        flash('Такого пользователя не существует')
        return redirect(request.args.get("next") or url_for("profile",userlogin=g.user.login))
    role_ = user.id_role
    method_ = method.query.filter_by(id=user.id_method).first()
    return render_template('profile.html',
                           title = 'Профиль',
                           user = user,
                           name = user.name,
                           role = cur_user_role,
                           role_user = role_,
                           method_name = method_.name)

@app.route('/editfiles/<int:file_id>',methods=['GET','POST'])
@login_required
def editfiles(file_id):
    """
    форма редактирования информации о загруженном файле

    file_id - id выбранного для редактирования файла
    """
    user = g.user.name
    role_ = g.user.id_role
    form = EditForm(file_id)
    discip_file = files.query.filter(files.id==file_id).first()
    file_ = files.query.filter(files.id_user==g.user.id,files.id==file_id).first()
    if file_ is None:
        flash('Вы не можете редактировать этот файл.')
        return redirect(request.args.get("next") or url_for('filesprep',user_info=g.user.id))

    form.discip_info.choices = [(g.id,g.name) for g in discip.query.order_by('name')]

    if role_ == 2:
        form.role_info.choices = [(1,'Студент'),(2,'Преподаватель')]
    else:
        form.role_info.choices = [(g.id,g.name) for g in role.query]

    form.spec_info.choices = [(g.id,g.name) for g in spec.query.order_by('name')]

    if role_ == 2:
        form.tmtypes_.choices = [(g.id,g.name) for g in tmtypes.query.filter_by(id_pertain=3)]
        form.pertain_info.data = 3
    if role_ == 4:
        form.tmtypes_.choices = [(g.id,g.name) for g in tmtypes.query.filter(tmtypes.id_pertain!=1)]
    if role_ == 3 or role_ == 5:
        form.tmtypes_.choices = [(g.id,g.name) for g in tmtypes.query]
    
    form.pertain_info.choices = [(g.id,g.name) for g in pertain.query.order_by('id')]
    
    if form.validate_on_submit():
        fileinfo = form.file_info.data
        discip_inf = form.discip_info.data
        role_inf = form.role_info.data
        timestamp_ = datetime.utcnow()
        eduYe = form.eduYear_info.data
        tmtype = form.tmtypes_.data
        public_ch = form.public_check.data
        file_update = db.session.query(files).filter(files.id_user==g.user.id,files.id==file_id).\
                      update({"id_discip":discip_inf,
                              "id_role":role_inf,
                              "id_tmtypes":tmtype,
                              "id_pertain":form.pertain_info.data,
                              "timestamp":timestamp_,
                              "info":fileinfo,
                              "eduYear":eduYe,
                              "public":public_ch})
        db.session.commit()
        return redirect(url_for('filesprep',user_info=g.user.id))
    else:
        title = 'Редактирование сведений о файле'
        spec_file = discip.query.filter_by(id=file_.id_discip).first()
        form.spec_info.data = spec_file.id_spec
        form.file_info.data = file_.info
        form.discip_info.data = file_.id_discip
        form.role_info.data = file_.id_role
        eduY = file_.eduYear
        form.tmtypes_.data = file_.id_tmtypes
        form.public_check.data = file_.public
        form.pertain_info.data = file_.id_pertain
        
    return render_template('editfiles.html',
                           title = title,
                           form = form,
                           name = user,
                           role = role_,
                           filename = file_.name,
                           discip_id = file_.id_discip,
                           tmtypes_id = file_.id_tmtypes,
                           eduY = eduY)

@app.route('/delete/<int:file_id>')
@login_required
def delete(file_id):
    """
    удаление выбранного файла

    file_id - id выбранного для удаления файла
    """
    role_user = g.user.id_role
    if role_user == 1:
        return redirect(url_for('accessdenied'))
    if role_user == 2 or role_user == 4:
        file = files.query.filter(files.id==file_id).first()
        if file is None:
            flash('Файл не найден.')
        if file.id_user != g.user.id:
            flash('Вы не можете удалить этот файл.')
            return redirect(request.args.get("next") or url_for('discips',id_discip=file.id_discip))
        file_id_discip = file.id_discip
    elif role_user == 3 or role_user == 5:
        file = files.query.filter(files.id==file_id).first()
        file_id_discip = file.id_discip
        if file is None:
            flash('Файл не найден.')
    db.session.delete(file)
    db.session.commit()
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'],file.name_hash))
    flash('Файл успешно удален')
    if role_user == 2 or role_user == 4:
        return redirect(url_for('filesprep',user_info=g.user.id))
    if role_user == 3 or role_user == 5:
        return redirect(url_for('filesprep',user_info=file.id_user))

@app.route('/deletep/<int:file_id>')
@login_required
def deletep(file_id):
    """
    удаление выбранного файла из раздела положения

    file_id - id выбранного для удаления файла
    """
    role_user = g.user.id_role
    if role_user == 1:
        return redirect(url_for('accessdenied'))
    if role_user == 2 or role_user == 4:
        file = files.query.filter(files.id==file_id).first()
        if file is None:
            flash('Файл не найден.')
        if file.id_user != g.user.id:
            flash('Вы не можете удалить этот файл.')
            return redirect(request.args.get("next") or url_for('filescoll'))
        file_id_discip = file.id_discip
    elif role_user == 3 or role_user == 5:
        file = files.query.filter(files.id==file_id).first()
        file_id_discip = file.id_discip
        if file is None:
            flash('Файл не найден.')
    db.session.delete(file)
    db.session.commit()
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'],file.name_hash))
    flash('Файл успешно удален')
    if role_user == 2 or role_user == 4:
        return redirect(url_for('filescoll'))
    if role_user == 3 or role_user == 5:
        return redirect(url_for('filescoll'))

@app.route('/deletes/<int:file_id>')
@login_required
def deletes(file_id):
    """
    удаление выбранного файла из раздела специальности

    file_id - id выбранного для удаления файла
    """
    role_user = g.user.id_role
    if role_user == 1:
        return redirect(url_for('accessdenied'))
    file_spec_id = files.query.join(discip,files.id_discip==discip.id).\
                               join(spec,discip.id_spec==spec.id).filter(files.id==file_id).\
                               add_columns(spec.id.label('specid')).first()
    if role_user == 2 or role_user == 4:
        file = files.query.filter(files.id==file_id).first()
        if file is None:
            flash('Файл не найден.')
        if file.id_user != g.user.id:
            flash('Вы не можете удалить этот файл.')
            return redirect(request.args.get("next") or url_for('filespec',spec_id = file_spec_id.specid))
        file_id_discip = file.id_discip
    elif role_user == 3 or role_user == 5:
        file = files.query.filter(files.id==file_id).first()
        file_id_discip = file.id_discip
        if file is None:
            flash('Файл не найден.')
    db.session.delete(file)
    db.session.commit()
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'],file.name_hash))
    flash('Файл успешно удален')
    if role_user == 3 or role_user == 5:
        return redirect(url_for('filespec',spec_id = file_spec_id.specid))

@app.route('/useradd',methods=['GET','POST'])
@login_required
def useradd():
    """
    форма добавления пользователя для админа
    """
    user = g.user.name
    role_user = g.user.id_role
    if role_user == 1 or role_user == 2 or role_user == 4 or role_user == 5:
        return redirect(url_for('accessdenied'))
    form = AddUserForm()
    form.spec_info.choices = [(g.id,g.name) for g in spec.query.order_by('name')]
    form.method_info.choices = [(g.id,g.name) for g in method.query.order_by('name')]
    form.role_info.choices = [(g.id,g.name) for g in role.query]
    form.group_info.choices = [(g.id,g.name) for g in groups.query.order_by('name')]
    if form.validate_on_submit():
        spec_inf = form.spec_info.data
        method_inf = form.method_info.data
        role_inf = form.role_info.data
        username = form.name_.data
        group = form.group_info.data
        if User.query.filter_by(login=form.login_.data).first() is not None:
            flash('Такой логин уже существует, выберите другой')
            return redirect(request.args.get("next") or url_for('useradd'))
        else:
            login_user = form.login_.data
        password = form.password_.data
        user_ = User(id_spec = spec_inf,
                     id_method = method_inf,
                     id_role = role_inf,
                     id_group = group,
                     name = username,
                     login = login_user)
        user_.hash_password(password)
        db.session.add(user_)
        db.session.commit()
        flash('Пользователь успешно добавлен')
        form.role_info.data = 1
        form.spec_info.data = 2
        form.method_info.data = 2
        form.name_.data = ''
        form.login_.data = ''
        form.group_info.data = 2
    return render_template('useradd.html',
                           form = form,
                           name = user,
                           title = "Добавление пользователя",
                           role = role_user)

@app.route('/discipadd',methods=['GET','POST'])
@login_required
def discipadd():
    """
    форма добавления предмета для админа
    """
    user = g.user.name
    role_user = g.user.id_role
    if role_user == 1 or role_user == 2 or role_user == 4 or role_user == 5:
        return redirect(url_for('accessdenied'))
    form = AddDiscipForm()
    form.spec_info.choices = [(g.id,g.name) for g in spec.query.order_by('name')]
    if form.validate_on_submit():
        spec_inf = form.spec_info.data
        eduY = form.eduYear_info.data
        if discip.query.filter_by(name=form.name.data,id_spec=spec_inf).first() is not None:
            flash('Такой предмет уже существует')
            return redirect(request.args.get("next") or url_for('discipadd'))
        else:
            discipname = form.name.data
        discip_ = discip(id_spec=spec_inf,name=discipname,eduYear=eduY)
        db.session.add(discip_)
        db.session.commit()
        flash('Предмет успешно добавлен')
        form.name.data = ''
    return render_template('discipadd.html',
                           form = form,
                           name = user,
                           title = "Добавление предмета",
                           role = role_user)

@app.route('/methodadd',methods=['GET','POST'])
@login_required
def methodadd():
    """
    форма добавления цикловой комиссии для админа
    """
    user = g.user.name
    role_user = g.user.id_role
    if role_user == 1 or role_user == 2 or role_user == 4 or role_user == 5:
        return redirect(url_for('accessdenied'))
    form = AddMethodForm()
    if form.validate_on_submit():
        if method.query.filter_by(name=form.name.data).first() is not None:
            flash('Цикловая комиссия с таким названием уже существует')
            return redirect(request.args.get("next") or url_for('methodadd'))
        else:
            methodname = form.name.data
        method_ = method(name=methodname)
        db.session.add(method_)
        db.session.commit()
        flash('Цикловая комиссия успешно добавлена')
        form.name.data = ''
    return render_template('methodadd.html',
                           form = form,
                           name = user,
                           title = "Добавление цикловой комиссии",
                           role = role_user)

@app.route('/specadd',methods=['GET','POST'])
@login_required
def specadd():
    """
    форма добавления специальности для админа
    """
    user = g.user.name
    role_user = g.user.id_role
    if role_user == 1 or role_user == 2 or role_user == 4 or role_user == 5:
        return redirect(url_for('accessdenied'))
    form = AddSpecForm()
    if form.validate_on_submit():
        if spec.query.filter_by(name=form.name.data).first() is not None:
            flash('Специальность с таким названием уже существует')
            return redirect(request.args.get("next") or url_for('specadd'))
        else:
            specname = form.name.data
        spec_ = spec(name=specname)
        db.session.add(spec_)
        db.session.commit()
        flash('Специальность успешно добавлена')
        form.name.data = ''
    return render_template('specadd.html',
                           form = form,
                           name = user,
                           title = "Добавление специальности",
                           role = role_user)

@app.route('/filesadm')
@app.route('/filesadm/<int:id_discip>')
@login_required
def filesadmin(id_discip=8):
    """
    список предметов и загруженных в них файлов для админа

    id_discip - id выбранного предмета
    """
    user = g.user.name
    role = g.user.id_role
    if role == 1 or role == 2 or role == 4 or role == 5:
        return redirect(url_for('accessdenied'))
    file_ = g.user.files_admin(id_discip)
    discip_a = discip.query.filter(discip.id==id_discip).first()
    discip_ = g.user.discip_admin(discip_a.id_spec)
    
    return render_template('filesadmin.html',
        title = 'Просмотр',
        name = user,
        role = role,
        filesadm = file_,
        discipadm = discip_,
        id_spec_ = discip_a.id_spec,
        cur_disc = discip_a.name)


@app.route('/userlist')
@login_required
def userlist():
    """
    общий список пользователей для админа
    """
    user = g.user.name
    role = g.user.id_role
    if role == 1 or role == 2 or role == 4 or role == 5:
        return redirect(url_for('accessdenied'))
    userlist_prep = User.query.filter(User.id_role!=1).order_by('name')
    userlist_stud = User.query.filter(User.id_role==1).order_by('name')
    
    return render_template('userlist.html',
        title = 'Список пользователей',
        name = user,
        role = role,
        userlist_p = userlist_prep,
        userlist_s = userlist_stud)

@app.route('/methodlist')
@login_required
def methodlist():
    """
    список цикловых комиссий для админа
    """
    user = g.user.name
    role = g.user.id_role
    if role == 1:
        return redirect(url_for('accessdenied'))
    methodlist = method.query.filter(method.id!=2).order_by('name')
    
    return render_template('methodlist.html',
        title = 'Список цикловых комиссий',
        name = user,
        role = role,
        methodlist = methodlist)

@app.route('/editdiscip/<int:discip_id>',methods=['GET','POST'])
@login_required
def editdiscip(discip_id):
    """
    форма редактирования предмета для админа

    discip_id - id выбранного предмета
    """
    user = g.user.name
    role_ = g.user.id_role
    if role_ == 1:
        return redirect(url_for('accessdenied'))
    if role_ == 2 or role_ == 4 or role_ == 5:
        return redirect(url_for('accessdenied'))
    elif role_ == 3:
        form = EditDiscipForm(discip_id)
        discip_ = discip.query.filter(discip.id==discip_id).first()
        if discip_ is None:
            flash('Предмет не найден')
            return redirect(url_for('specsadmin'))
        form.spec_info.choices = [(x.id,x.name) for x in spec.query.order_by('name')]
    
    if form.validate_on_submit():
        name_discip = form.name.data
        eduYe = form.eduYear_info.data
        spec_inf = form.spec_info.data
        discip_update = db.session.query(discip).filter(discip.id==discip_id).\
                      update({"id_spec":spec_inf,"name":name_discip,"eduYear":eduYe})
        db.session.commit()
        return redirect(url_for('specsadmin',id_spec=spec_inf))
    else:
        title = 'Редактирование ' + discip_.name
        form.spec_info.data = discip_.id_spec
        form.name.data = discip_.name
        eduY = discip_.eduYear 
    return render_template('editdiscipadm.html',
                           title = title,
                           form = form,
                           name = user,
                           role = role_,
                           discipname = discip_.name,
                           discip_spec = discip_.id_spec,
                           eduY = eduY)

@app.route('/deletediscip/<int:discip_id>')
@login_required
def deletediscip(discip_id):
    """
    функция удаления предмета для админа

    discip_id - id выбранного предмета
    """
    role_user = g.user.id_role
    if role_user == 1:
        return redirect(url_for('accessdenied'))
    if role_user == 2 or role_user == 4 or role_user == 5:
        return redirect(url_for('accessdenied'))
    elif role_user == 3:
        discip_ = discip.query.filter(discip.id==discip_id).first()
        discip_spec = discip_.id_spec
        if discip_ is None:
            flash('Предмет не найден.')
            return redirect(request.args.get("next") or url_for('specsadmin',id_spec=discip_spec))
    listfiles = files.query.filter(files.id_discip==discip_id).first()
    if listfiles is None:
        flash('Предмет успешно удален')
        db.session.delete(discip_)
        db.session.commit()
    else:
        flash('Невозможно удалить предмет')
        db.session.rollback()
    if role_user == 3:
        return redirect(url_for('specsadmin',id_spec=discip_spec))

@app.route('/editusers/<int:user_id>',methods=['GET','POST'])
@login_required
def editusers(user_id):
    """
    форма редактирования пользователя-студента для админа

    user_id - id выбранного пользователя
    """
    user = g.user.name
    role_user = g.user.id_role
    if role_user == 1 or role_user == 2 or role_user == 4 or role_user == 5:
        return redirect(url_for('accessdenied'))
    edituser = User.query.filter(User.id==user_id).first()
    form = EditUserFormS()
    form.spec_info.choices = [(g.id,g.name) for g in spec.query.order_by('name')]
    form.group_info.choices = [(g.id,g.name) for g in groups.query.order_by('name')]
    if form.validate_on_submit():
        spec_inf = form.spec_info.data
        username = form.name_.data
        group = form.group_info.data
        login_check = User.query.filter_by(login=form.login_.data).first()
        if form.login_.data != edituser.login:
            if login_check is not None:
                flash('Такой логин уже существует, выберите другой')
                return redirect(request.args.get("next") or url_for('editusers',user_id=edituser.id))
            else:
                login_user = form.login_.data
        else:
            login_user = form.login_.data
        User_update = db.session.query(User).filter(User.id==user_id).\
                      update({"id_spec":spec_inf,"id_group":group,"name":username,"login":login_user})
        db.session.commit()
        flash('Пользователь успешно изменен!')
        return redirect(url_for('groupsadmin',id_groups=group))
    else:
        title = 'Редактирование ' + edituser.name
        form.spec_info.data = edituser.id_spec
        form.name_.data = edituser.name
        form.group_info.data = edituser.id_group
        form.login_.data = edituser.login
        
    return render_template('editusers.html',
                           form = form,
                           name = user,
                           title = title,
                           role = role_user,
                           user_cur = edituser)

@app.route('/edituserp/<int:user_id>',methods=['GET','POST'])
@login_required
def edituserp(user_id):
    """
    форма редактирования пользователя-преподавателя или администратора для админа

    user_id - id выбранного преподавателя
    """
    user = g.user.name
    role_user = g.user.id_role
    if role_user == 1 or role_user == 2 or role_user == 4 or role_user == 5:
        return redirect(url_for('accessdenied'))
    edituser = User.query.filter(User.id==user_id).first()
    form = EditUserFormP()
    form.method_info.choices = [(g.id,g.name) for g in method.query.order_by('name')]
    form.role_info.choices = [(g.id,g.name) for g in role.query]
    if form.validate_on_submit():
        method_inf = form.method_info.data
        role_inf = form.role_info.data
        username = form.name_.data
        login_check = User.query.filter_by(login=form.login_.data).first()
        if form.login_.data != edituser.login:
            if login_check is not None:
                flash('Такой логин уже существует, выберите другой')
                return redirect(url_for(request.args.get("next") or 'edituserp',user_id=edituser.id))
            else:
                login_user = form.login_.data
        else:
            login_user = form.login_.data
        User_update = db.session.query(User).filter(User.id==user_id).\
                      update({"id_method":method_inf,"name":username,"login":login_user,"id_role":role_inf})
        db.session.commit()
        flash('Пользователь успешно изменен!')
        return redirect(url_for('methodsadmin',method_id=method_inf))
    else:
        title = 'Редактирование ' + edituser.name
        form.method_info.data = edituser.id_method
        form.name_.data = edituser.name
        form.login_.data = edituser.login
        form.role_info.data = edituser.id_role
        
    return render_template('edituserp.html',
                           form = form,
                           name = user,
                           title = title,
                           role = role_user,
                           user_cur = edituser,
                           method_inf = edituser.id_method)

@app.route('/edituserpass/<int:user_id>',methods=['GET','POST'])
@login_required
def edituserpass(user_id):
    """
    форма редактирования пароля пользователя

    user_id - id выбранного пользователя
    """
    user = g.user.name
    role_user = g.user.id_role
    if role_user == 1 or role_user == 2 or role_user == 4 or role_user == 5:
        return redirect(url_for('accessdenied'))
    edituser = User.query.filter(User.id==user_id).first()
    form = EditUserPassForm()
    if form.validate_on_submit():
        password = form.password_.data
        edituser.hash_password(password)
        db.session.commit()
        flash('Пароль успешно изменен!')
        if edituser.id_role!=1:
            return redirect(url_for('methodsadmin',method_id=edituser.id_method))
        else:
            return redirect(url_for('groupsadmin',id_groups=edituser.id_group))
    else:
        title = 'Редактирование ' + edituser.name
                
    return render_template('edituserpass.html',
                           form = form,
                           name = user,
                           title = title,
                           role = role_user,
                           user_cur = edituser)

@app.route('/deleteuser/<int:user_id>')
@login_required
def deleteuser(user_id):
    """
    удаление выбранного пользователя для админа

    user_id - id выбранного пользователя
    """
    role_user = g.user.id_role
    if role_user == 1 or role_user == 2 or role_user == 4 or role_user == 5:
        return redirect(url_for('accessdenied'))
    elif role_user == 3:
        user_ = User.query.filter(User.id==user_id).first()
        if user_ is None:
            flash('Пользователь не найден.')
            return redirect(request.args.get("next") or url_for('userlist'))
        role = user_.id_role
        method_inf = user_.id_method
        group = user_.id_group
    listfiles = files.query.filter(files.id_user==user_id).first()
    if listfiles is None:
        flash('Пользователь успешно удален')
        db.session.delete(user_)
        db.session.commit()
    else:
        flash('Невозможно удалить пользователя')
        db.session.rollback()
    if role_user == 3:
        if role == 1:
            return redirect(url_for('groupsadmin',id_groups=group))
        if role == 2 or role == 3:
            return redirect(url_for('methodsadmin',method_id=method_inf))

@app.route('/editmethod/<int:method_id>',methods=['GET','POST'])
@login_required
def editmethod(method_id):
    """
    форма редактирования цикловой комиссии для админа

    method_id - id выбранной цикловой комиссии
    """
    user = g.user.name
    role_user = g.user.id_role
    if role_user == 1 or role_user == 2 or role_user == 4 or role_user == 5:
        return redirect(url_for('accessdenied'))
    editmethod_ = method.query.filter(method.id==method_id).first()
    form = EditMethodForm()
    if form.validate_on_submit():
        methodname = form.name_.data
        method_update = db.session.query(method).filter(method.id==method_id).\
                      update({"name":methodname})
        db.session.commit()
        flash('Цикловая комиссия успешно изменена!')
        return redirect(url_for('methodlist'))
    else:
        title = 'Редактирование ' + editmethod_.name
        form.name_.data = editmethod_.name
        
    return render_template('editmethod.html',
                           form = form,
                           name = user,
                           title = title,
                           role = role_user,
                           methodname = editmethod_.name)

@app.route('/deletemethod/<int:method_id>')
@login_required
def deletemethod(method_id):
    """
    функция удаления цикловой комиссии для админа

    method_id - id выбранной цикловой комиссии
    """
    role_user = g.user.id_role
    if role_user == 1 or role_user == 2 or role_user == 4 or role_user == 5:
        return redirect(url_for('accessdenied'))
    elif role_user == 3:
        method_ = method.query.filter(method.id==method_id).first()
        if method_ is None:
            flash('Цикловая комиссия не найдена')
            return redirect(request.args.get("next") or url_for('methodlist'))
    listusers = User.query.filter(User.id_method==method_id).first()
    if listusers is None:
        flash('Цикловая комиссия успешно удалена')
        db.session.delete(method_)
        db.session.commit()
    else:
        flash('Невозможно удалить цикловую комиссию')
        db.session.rollback()
    if role_user == 3:
        return redirect(url_for('methodlist'))

@app.route('/editspec/<int:spec_id>',methods=['GET','POST'])
@login_required
def editspec(spec_id):
    """
    форма редактирования специальности для админа

    spec_id - id выбранной специальности
    """
    user = g.user.name
    role_user = g.user.id_role
    if role_user == 1 or role_user == 2 or role_user == 4 or role_user == 5:
        return redirect(url_for('accessdenied'))
    editspec = spec.query.filter(spec.id==spec_id).first()
    form = EditSpecForm()
    if form.validate_on_submit():
        specname = form.name.data
        spec_update = db.session.query(spec).filter(spec.id==spec_id).\
                      update({"name":specname})
        db.session.commit()
        flash('Название специальности успешно изменено!')
        return redirect(url_for('specsadmin'))
    else:
        title = 'Редактирование ' + editspec.name
        form.name.data = editspec.name
        
    return render_template('editspec.html',
                           form = form,
                           name = user,
                           title = title,
                           role = role_user,
                           specname = editspec.name)

@app.route('/deletespec/<int:spec_id>')
@login_required
def deletespec(spec_id):
    """
    функция удаления специальности для админа

    spec_id - id выбранной специальности
    """
    role_user = g.user.id_role
    if role_user == 1 or role_user == 2 or role_user == 4 or role_user == 5:
        return redirect(url_for('accessdenied'))
    elif role_user == 3:
        spec_ = spec.query.filter(spec.id==spec_id).first()
        if spec_ is None:
            flash('Специальность не найдена')
            return redirect(request.args.get("next") or url_for('specsasmin'))
    listusers = User.query.filter(User.id_spec==spec_id).first()
    listdiscip = discip.query.filter(discip.id_spec==spec_id).first()
    if listusers is None and listdiscip is None:
        flash('Специальность успешно удалена')
        db.session.delete(spec_)
        db.session.commit()
    else:
        flash('Невозможно удалить специальность')
        db.session.rollback()
    if role_user == 3:
        return redirect(url_for('specsadmin'))

@app.route('/methodadm')
@app.route('/methodadm/<int:method_id>')
@login_required
def methodsadmin(method_id=1):
    """
    список цикловых комиссий и преподавателей в них для админа

    method_id - id выбранной цикловых комиссий
    """
    user = g.user.name
    role = g.user.id_role
    if role == 1:
        return redirect(url_for('accessdenied'))
    method_ = g.user.method_admin()
    userp_ = g.user.user_method_admin(method_id)
    current_method = method.query.filter(method.id==method_id).first()
    
    return render_template('methodsadmin.html',
        title = 'Просмотр цикловых комиссий',
        name = user,
        role = role,
        methodadm = method_,
        cur_method = current_method,
        userp = userp_)

@app.route('/specgroups')
@app.route('/specsgroups/<int:id_spec>')
@login_required
def specgroupsadmin(id_spec=1):
    """
    список специальностей и групп в них для админа

    id_spec - id выбранной специальности
    """
    user = g.user.name
    role = g.user.id_role
    if role == 1 or role == 2 or role == 4 or role == 5:
        return redirect(url_for('accessdenied'))
    spec_ = g.user.spec_admin()
    groups_ = g.user.groups_admin(id_spec)
    current_spec = spec.query.filter(spec.id==id_spec).first()
    
    return render_template('specgroupsadmin.html',
        title = 'Просмотр специальностей',
        name = user,
        role = role,
        specadm = spec_,
        cur_spec = current_spec,
        groupsadm = groups_)

@app.route('/groupsadm')
@app.route('/groupsadm/<int:id_groups>')
@login_required
def groupsadmin(id_groups=1):
    """
    список групп и пользователей в них для админа

    id_groups - id выбранной группы
    """
    user = g.user.name
    role = g.user.id_role
    if role == 1 or role == 2 or role == 4 or role == 5:
        return redirect(url_for('accessdenied'))
    user_ = g.user.users_admin(id_groups)
    groups_a = groups.query.filter(groups.id==id_groups).first()
    groups_ = g.user.groups_admin(groups_a.id_spec)
    
    return render_template('groupsadmin.html',
        title = 'Просмотр ' + groups_a.name,
        name = user,
        role = role,
        usersadm = user_,
        groupsadm = groups_,
        id_spec_ = groups_a.id_spec,
        cur_groups = groups_a.name)

@app.route('/groupsadd',methods=['GET','POST'])
@login_required
def groupsadd():
    """
    форма добавления групп для админа
    """
    user = g.user.name
    role_user = g.user.id_role
    if role_user == 1 or role_user == 2 or role_user == 4 or role_user == 5:
        return redirect(url_for('accessdenied'))
    form = AddGroupsForm()
    form.spec_info.choices = [(g.id,g.name) for g in spec.query.order_by('name')]
    if form.validate_on_submit():
        spec_inf = form.spec_info.data
        if groups.query.filter_by(name=form.name.data).first() is not None:
            flash('Такая группа уже существует')
            return redirect(request.args.get("next") or url_for('groupsadd'))
        else:
            groupsname = form.name.data
        groups_ = groups(id_spec=spec_inf,name=groupsname)
        db.session.add(groups_)
        db.session.commit()
        flash('Группа успешно добавлена')
        form.name.data = ''
    return render_template('groupsadd.html',
                           form = form,
                           name = user,
                           title = "Добавление группы",
                           role = role_user)

@app.route('/editgroups/<int:groups_id>',methods=['GET','POST'])
@login_required
def editgroups(groups_id):
    """
    форма редактирования групп для админа

    groups_id - id выбранной группы
    """
    user = g.user.name
    role_ = g.user.id_role
    if role_ == 1:
        return redirect(url_for('accessdenied'))
    if role_ == 2 or role_ == 4 or role_ == 5:
        return redirect(url_for('accessdenied'))
    elif role_ == 3:
        form = EditGroupsForm(groups_id)
        groups_ = groups.query.filter(groups.id==groups_id).first()
        if groups_ is None:
            flash('Группа не найдена')
            return redirect(url_for('specgroupsadmin'))
        form.spec_info.choices = [(g.id,g.name) for g in spec.query.order_by('name')]
    
    if form.validate_on_submit():
        name_groups = form.name.data
        spec_inf = form.spec_info.data
        groups_update = db.session.query(groups).filter(groups.id==groups_id).\
                      update({"id_spec":spec_inf,"name":name_groups})
        db.session.commit()
        return redirect(url_for('specgroupsadmin',id_spec=spec_inf))
    else:
        title = 'Редактирование ' + groups_.name
        form.spec_info.data = groups_.id_spec
        form.name.data = groups_.name
    return render_template('editgroupsadm.html',
                           title = title,
                           form = form,
                           name = user,
                           role = role_,
                           groupsname = groups_.name,
                           groups_spec = groups_.id_spec)

@app.route('/deletegroups/<int:groups_id>')
@login_required
def deletegroups(groups_id):
    """
    фукнция удаления группы для админа

    groups_id - id выбранной группы
    """
    role_user = g.user.id_role
    if role_user == 1:
        return redirect(url_for('accessdenied'))
    if role_user == 2 or role_user == 4 or role_user == 5:
        return redirect(url_for('accessdenied'))
    elif role_user == 3:
        groups_ = groups.query.filter(groups.id==groups_id).first()
        groups_spec = groups_.id_spec
        if groups_ is None:
            flash('Группа не найдена.')
            return redirect(request.args.get("next") or url_for('specgroupsadmin',id_spec=groups_spec))
    listusers = User.query.filter(User.id_group==groups_id).first()
    if listusers is None:
        flash('Группа успешно удалена')
        db.session.delete(groups_)
        db.session.commit()
    else:
        flash('Невозможно удалить группу')
        db.session.rollback()
    if role_user == 3:
        return redirect(url_for('specgroupsadmin',id_spec=groups_spec))


@app.route('/messageedit',methods=['GET','POST'])
@login_required
def messageedit():
    """
    форма редактирования оповещения
    """
    user = g.user.name
    role_ = g.user.id_role
    if role_ == 1:
        return redirect(url_for('accessdenied'))
    if role_ == 2 or role_ == 4 or role_ == 5:
        return redirect(url_for('accessdenied'))
    elif role_ == 3:
        form = EditMessage()

    message_ = message.query.first()
    
    if form.validate_on_submit():
        messagedata = form.message.data
        timestamp = datetime.utcnow()
        message_update = db.session.query(message).\
                      update({"message":messagedata,"timestamp":timestamp})
        db.session.commit()
        flash('Изменения успешно внесены')
        return redirect(url_for('messageedit'))
    else:
        title = 'Редактирование оповещения'
        form.message.data = message_.message
    return render_template('messageedit.html',
                           title = title,
                           form = form,
                           name = user,
                           role = role_,
                           messagetimestamp = message_.timestamp)

@app.route('/filesnew', methods = ['GET'])
@login_required
def files_json():
    """
    возвращает список файлов для выбранного пользователя в json-формате
    """
    role_ = g.user.id_role
    if role_ == 1:
        return abort(403)
    user_id = request.args.get('user_info',0,type=int)
    # file_id = request.args.get('files_info',0,type=int)
    # disc_id = request.args.get('disc_info',0,type=int)
    # tmtype = tmtypes.query
    # files_ = files.query.join(discip,files.id_discip==discip.id).\
    #            join(spec,discip.id_spec==spec.id).\
    #            join(User,files.id_user==User.id).\
    #            join(method,User.id_method==method.id).\
    #            join(tmtypes,files.id_tmtypes==tmtypes.id).\
    #            filter(files.id_user==user_id,files.id_tmtypes==file_id,files.id_discip==disc_id).\
    #            add_columns(spec.name.label('specname'),
    #                        discip.name.label('discipname'),
    #                        method.id.label('methodid'),
    #                        spec.id.label('specid'),
    #                        tmtypes.name.label('tmtypename'))
    #
    # result = {}
    #
    # for file_ in files_:
    #     result[str(file_.files.id)] = {"file_name":file_.files.name,
    #                                    "fileid":str(file_.files.id),
    #                                    "specid":file_.specid,
    #                                    "tmtype_name":file_.tmtypename,
    #                                    "spec_name":file_.specname,
    #                                    "discip_name":file_.discipname,
    #                                    "files_info":file_.files.info,
    #                                    "edu_Year":str(file_.files.eduYear),
    #                                    "timestamp":str(file_.files.timestamp),
    #                                    "role_file_id":str(file_.files.role_file.id),
    #                                    "role_file":file_.files.role_file.name,
    #                                    "file_id_user":file_.files.id_user,
    #                                    "file_public":str(file_.files.public),
    #                                    "file_accept":str(file_.files.accept)}
    files_ = files.query.join(discip,files.id_discip==discip.id).\
               join(spec,discip.id_spec==spec.id).\
               join(User,files.id_user==User.id).\
               join(method,User.id_method==method.id).\
               join(tmtypes,files.id_tmtypes==tmtypes.id).\
               filter(files.id_user==user_id,files.id_pertain==3).\
               add_columns(spec.name.label('specname'),
                           discip.name.label('discipname'),
                           method.id.label('methodid'),
                           spec.id.label('specid'),
                           tmtypes.name.label('tmtypename'),
                           tmtypes.id.label('tmtypeid'),
                           discip.id.label('discipid'))
    result = {}

    for fil in files_:
        result[str(fil.files.id)] = {"file_id":str(fil.files.id),
                                     "file":{"file_name":fil.files.name,
                                             "specid":fil.specid,
                                             "tmtype_name":fil.tmtypename,
                                             "spec_name":fil.specname,
                                             "discip_name":fil.discipname,
                                             "files_info":fil.files.info,
                                             "edu_Year":str(fil.files.eduYear),
                                             "timestamp":str(fil.files.timestamp),
                                             "role_file_id":str(fil.files.role_file.id),
                                             "role_file":fil.files.role_file.name,
                                             "file_id_user":fil.files.id_user,
                                             "file_public":str(fil.files.public),
                                             "file_accept":str(fil.files.accept),
                                             "discip_id":fil.discipid,
                                             "tmtype_id":fil.tmtypeid}}
    return jsonify(result)

@app.route('/specnew', methods = ['GET'])
@login_required
def spec_json():
    """
    возвращает список файлов для выбранного пользователя в json-формате
    """
    role_ = g.user.id_role
    if role_ == 1:
        return abort(403)
    user_id = request.args.get('user_info',0,type=int)
    spec_ = spec.query.join(discip,discip.id_spec==spec.id).\
               join(files,files.id_discip==discip.id).\
               join(User,files.id_user==User.id).filter(spec.id!=2,User.id==user_id)
    
    result = {}

    for sp in spec_:
        result[str(sp.id)] = {"specid":str(sp.id),"spec_name":sp.name}
        
    return jsonify(result)

@app.route('/discipnew', methods = ['GET'])
@login_required
def discip_json():
    """
    возвращает список файлов для выбранного пользователя в json-формате
    """
    role_ = g.user.id_role
    if role_ == 1:
        return abort(403)
    user_id = request.args.get('user_info',0,type=int)
    discips_ = discip.query.join(files,files.id_discip==discip.id).\
               join(User,files.id_user==User.id).filter(files.id_user==user_id,
                                                           files.id_pertain==3).\
               order_by('discip_name')
    
    result = {}

    for disc in discips_:
        result[str(disc.id)] = {"disc_id":str(disc.id),"discip_name":disc.name,"specid":disc.id_spec}
        
    return jsonify(result)

@app.route('/tmtypenew', methods = ['GET'])
@login_required
def tmtype_json():
    """
    возвращает список типов файлов для выбранного пользователя в json-формате
    """
    role_ = g.user.id_role
    if role_ == 1:
        return abort(403)
    user_id = request.args.get('user_info',0,type=int)
    tmtype = tmtypes.query.filter(tmtypes.id_pertain==3)
    # spec_ = spec.query.join(discip,discip.id_spec==spec.id).\
    #            join(files,files.id_discip==discip.id).\
    #            join(User,files.id_user==User.id).filter(spec.id!=2,User.id==user_id)
    
    result = {}
    for tm in tmtype:
        result[str(tm.id)] = {"tmtypeid":str(tm.id),"type":tm.name}
    return jsonify(result)

@app.route('/test',methods = ['GET', 'POST'])
@login_required
def test_files():
    """
    список преподавателей и загруженных ими файлов для преподавателя

    """
    user = g.user.name
    role_ = g.user.id_role
    if role_ == 1:
        return redirect(url_for('accessdenied'))
    user_id = 4#request.args.get('user_info',0,type=int)
    files_ = g.user.followed_files_prep(user_id)
    tmtype = tmtypes.query.filter(tmtypes.id_pertain==3)
    spec_ = spec.query.join(discip,discip.id_spec==spec.id).\
               join(files,files.id_discip==discip.id).\
               join(User,files.id_user==User.id).filter(spec.id!=2,User.id==user_id)
    discips_ = discip.query.join(files,files.id_discip==discip.id).\
               join(User,files.id_user==User.id).filter(files.id_user==user_id,
                                                           files.id_pertain==3).\
               order_by('discip_name')
    userlist = User.query.filter(User.id!=g.user.id,User.id_role!=1).order_by('name')

    return render_template('test.html',
        title = 'Список загруженных файлов',
        name = user,
        role = role_,
        files = files_,
        users = userlist,
        user_id = user_id,
        tmtype = tmtype,
        specs = spec_,
        discips = discips_)
