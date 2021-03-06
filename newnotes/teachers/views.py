from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import bcrypt
from bson import ObjectId

from newnotes.teachers.forms import TeacherForm, EditForm, AdminForm,internForm
from newnotes.models import User, School, Module1, Module2, Module3, Assignment,Jobs

teachers_blueprint = Blueprint('teachers',
                               __name__,
                               template_folder='templates/teachers')


@teachers_blueprint.route('/create', methods=['GET', 'POST'])
def create():
    form = TeacherForm(request.form)
    # get all the schools from the schools table

    # Issue row.id is mongodb objectId so we need to convert it into str.
    # otherwise the form validation will failed
    school_list = [(str(row.id), row.name) for row in School.objects()]
    school_list.append(("not-listed", "My school is not listed"))
    form.school.choices = school_list
    if request.method == 'POST' and form.validate():
        # for field, errors in form.errors.items():
        #     for error in errors:
        #         flash(u"Error in the %s field - %s" % (
        #             getattr(form, field).label.text,
        #             error
        #         ))
        # check if a user exist with the given email or not
        existing_user = User.objects().filter(email=form.email.data).first()
        if existing_user is None:
            # before inserting the document into database we have to hash password
            hash_password = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
            # check if the school is listed or not
            school_id = form.school.data
            if form.school.data == 'not-listed':
                # get the name of the school
                school_name = request.form.get('school_name')
                # insert the school into the database
                school = School()
                school.name = school_name

                # here create the module1, module2, module3
                # Assign module1, module2, module3 to the school
                module1 = Module1()
                module1.save()
                school.module1 = module1.id

                module2 = Module2()
                module2.save()
                school.module2 = module2.id

                module3 = Module3()
                module3.save()
                school.module3 = module3.id

                school.save()
                school_id = school.id
            user = User()
            # Set the user data
            user.title = form.title.data
            user.user_type = 'instructor'
            user.name = form.name.data
            user.surname = form.surname.data
            user.email = form.email.data
            user.password = hash_password
            # Since we converted the row.id to string. for school we need to convert is ObjectId
            # Because school is a reference type
            user.school = ObjectId(school_id)
            # Finally save the user
            user.save()
            session['email'] = user.email
            return redirect(url_for('teachers.profile'))
        else:
            flash('User with this email already exist')
            return redirect(url_for('teachers.create'))
    return render_template('teacher-create.html', form=form)


@teachers_blueprint.route('/create_admin', methods=['GET', 'POST'])
def create_admin():
    form = AdminForm(request.form)
    # get all the schools from the schools table

    # Issue row.id is mongodb objectId so we need to convert it into str.
    # otherwise the form validation will failed
    school_list = [(str(row.id), row.name) for row in School.objects()]
    school_list.append(("not-listed", "My school is not listed"))
    form.school.choices = school_list
    if request.method == 'POST' and form.validate():
        # for field, errors in form.errors.items():
        #     for error in errors:
        #         flash(u"Error in the %s field - %s" % (
        #             getattr(form, field).label.text,
        #             error
        #         ))
        # check if a user exist with the given email or not
        existing_user = User.objects().filter(email=form.email.data).first()
        # Here check the SECRET KEY
        if existing_user is None and form.secret.data == 'some_super_secret_text_here':
            # before inserting the document into database we have to hash password
            hash_password = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
            # check if the school is listed or not
            school_id = form.school.data
            if form.school.data == 'not-listed':
                # get the name of the school
                school_name = request.form.get('school_name')
                # insert the school into the database
                school = School()
                school.name = school_name

                # here create the module1, module2, module3
                # Assign module1, module2, module3 to the school
                module1 = Module1()
                module1.save()
                school.module1 = module1.id

                module2 = Module2()
                module2.save()
                school.module2 = module2.id

                module3 = Module3()
                module3.save()
                school.module3 = module3.id

                school.save()
                school_id = school.id
            user = User()
            # Set the user data
            user.title = form.title.data
            user.user_type = 'admin'
            user.name = form.name.data
            user.surname = form.surname.data
            user.email = form.email.data
            user.password = hash_password
            # Since we converted the row.id to string. for school we need to convert is ObjectId
            # Because school is a reference type
            user.school = ObjectId(school_id)
            # Finally save the user
            user.save()
            session['email'] = user.email
            return redirect(url_for('teachers.profile'))
        else:
            if form.secret.data != 'some_super_secret_text_here':
                flash('Wrong secret key !')
            else:
                flash('User with this email already exist')
            return redirect(url_for('teachers.create_admin'))
    return render_template('admin-create.html', form=form)

@teachers_blueprint.route('/jobs', methods=['GET', 'POST'])
def job():
    # get the logged in user by session.get('email')
    if session.get('email'):
        form = internForm(request.form)
        teacher = User.objects().filter(email=session.get('email')).first()
        if teacher.user_type == 'instructor' or teacher.user_type == 'admin' :
            if request.method == 'POST' and form.validate():
                job= Jobs()
                job.title=form.title.data
                job.email=form.email.data
                job.about=form.about.data
                job.save()
                # flash('Internship Company Added !')
                return redirect(url_for('teachers.profile'))
        else:
            return redirect(url_for('teachers.profile'))
       
        return render_template('post.html',form=form, user=teacher)
    else:
        return redirect(url_for('login'))

@teachers_blueprint.route('/managejobs', methods=['GET', 'POST'])
def managejobs():
    # get the logged in user by session.get('email')
    if session.get('email'):
        form = internForm(request.form)
        teacher = User.objects().filter(email=session.get('email')).first()
        if teacher.user_type == 'instructor' or teacher.user_type == 'admin' :
            if request.method == 'POST' and form.validate():
                job= Jobs()
                job.title=form.title.data
                job.email=form.email.data
                job.about=form.about.data
                job.save()
                # flash('Internship Company Added !')
                return redirect(url_for('teachers.profile'))
        else:
            return redirect(url_for('teachers.profile'))
        jo= Jobs.objects().filter()
        return render_template('manageposts.html',form=form, user=teacher,job=jo)
    else:
        return redirect(url_for('login'))

@teachers_blueprint.route('/jobedit/<post_id>', methods=['GET', 'POST'])
def jobedit(post_id):
    # get the logged in user by session.get('email')
    if session.get('email'):
        form = internForm(request.form)
        teacher = User.objects().filter(email=session.get('email')).first()
        jo=Jobs.objects(id=post_id).first()
        if teacher.user_type == 'instructor' or teacher.user_type == 'admin' :
            if request.method == 'POST' and form.validate():
                jo.title=form.title.data
                jo.email=form.email.data
                jo.about=form.about.data
                jo.save()
                # flash('Internship Company Added !')
                return redirect(url_for('teachers.managejobs'))
        else:
            return redirect(url_for('teachers.profile'))
        jo= Jobs.objects().filter()
        return render_template('manageposts.html',form=form, user=teacher,job=jo)
    else:
        return redirect(url_for('login'))



@teachers_blueprint.route('/remove/<post_id>', methods=['GET', 'POST'])
def remove(post_id):
    if session.get('email'):
        user = User.objects().filter(email=session.get('email')).first()
        if user.user_type == 'instructor' or user.user_type == 'admin':
            Jobs.objects(id=post_id).delete()
            return redirect(url_for('teachers.managejobs'))
        else:
            return redirect(url_for('teachers.managejobs'))
    else:
        return redirect(url_for('login'))

@teachers_blueprint.route('/edit/<post_id>', methods=['GET', 'POST'])
def edit(post_id):
    if session.get('email'):
        form = internForm(request.form)
        user = User.objects().filter(email=session.get('email')).first()
        if user.user_type == 'instructor' or user.user_type == 'admin':
            jo=Jobs.objects(id=post_id).first()
            return render_template('editpost.html',form=form, user=user,job=jo) 
        else:
           return redirect(url_for('teachers.managejobs'))
    else:
        return redirect(url_for('login'))




@teachers_blueprint.route('/profile', methods=['GET', 'POST'])
def profile():
    if session.get('email'):
        user = User.objects().filter(email=session.get('email')).first()
        total=User.objects().filter(user_type='student').count()
        attached=User.objects().filter(attached='true').count()
        # find the student assignments
        # for this we need to find the assignment which is open as well as same as the student school
        assignments = Assignment.objects(school=user.school.id)
        return render_template('teacher-profile.html', user=user, assignments=assignments,total=total,attached=attached)
    else:
        return redirect(url_for('login'))


@teachers_blueprint.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if session.get('email'):
        form = EditForm()
        school_list = [(str(row.id), row.name) for row in School.objects()]
        form.school.choices = school_list
        user = User.objects().filter(email=session.get('email')).first()
        form.name.data = user.name
        form.surname.data = user.surname
        if request.method == 'POST' and form.validate():
            user.name = form.name.data
            user.surname = form.surname.data
            if user.user_type == 'admin' and form.school.data is not None:
                user.school = ObjectId(form.school.data)
            user.save()
            flash('Profile successfully updated !')
        return render_template('teacher-edit-profile.html', user=user, form=form)
    else:
        return redirect(url_for('login'))
