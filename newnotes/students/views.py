from flask import Blueprint, render_template, request, session, redirect, url_for, flash
import bcrypt
from flask_mail import Mail, Message
from newnotes.students.forms import StudentForm, EditForm,internForm
from newnotes.models import User, School, Module1, Module2, Module3, Assignment,History
from bson import ObjectId
import datetime
from newnotes import app


mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'warumwa717@gmail.com',
    "MAIL_PASSWORD": '717@Warumwa'
}

app.config.update(mail_settings)
mail = Mail(app)
students_blueprint = Blueprint('students',
                               __name__,
                               template_folder='templates/students')


@students_blueprint.route('/create', methods=['GET', 'POST'])
def create():
    form = StudentForm(request.form)
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
            # we will also get the school id here.
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
            user.user_type = 'student'
            user.name = form.name.data
            user.surname = form.surname.data
            user.email = form.email.data
            user.regnumber=form.regnumber.data
            user.password = hash_password
            user.approved = False
            user.login_counter = 1
            user.login_array = [datetime.datetime.now()]
            # Since we converted the row.id to string. for school we need to convert is ObjectId
            # Because school is a reference type
            user.school = ObjectId(school_id)
            # Finally save the user
            user.save()
            session['email'] = user.email
            return redirect(url_for('students.profile'))
        else:
            flash('User with this email already exist')
            return redirect(url_for('students.create'))

    return render_template('student-create.html', form=form)

@students_blueprint.route('/intern', methods=['GET', 'POST'])
def intern():
    # get the logged in user by session.get('email')
    if session.get('email'):
        form = internForm(request.form)
        user = User.objects().filter(email=session.get('email')).first()
        if user.user_type == 'student' :
            if request.method == 'POST' and form.validate() :
                # First save the Question
                user.company = form.title.data
                # user.date = form.submission_date.data
                user.background=form.description.data
                user.attached="true"
                user.save()
                flash('Internship Company Added !')
                return redirect(url_for('students.profile'))
        else:
            return redirect(url_for('students.profile'))
        return render_template('comp.html',form=form, user=user)
    else:
        return redirect(url_for('login'))

@students_blueprint.route('/internupdate', methods=['GET', 'POST'])
def internupdate():
    # get the logged in user by session.get('email')
    if session.get('email'):
        form = internForm(request.form)
        user = User.objects().filter(email=session.get('email')).first()
        if user.user_type == 'student' :
            if request.method == 'POST' and form.validate() :
                history=History()
                history.email=user.email
                history.title=user.company
                history.background=user.background
                history.save()
                # First save the Question
                user.attached="true"
                user.company = form.title.data
                # user.date = form.submission_date.data
                user.background=form.description.data
                user.save()
                flash('Internship Company Added !')
                return redirect(url_for('students.profile'))
        else:
            return redirect(url_for('students.profile'))
        return render_template('updatecomp.html',form=form, user=user)
    else:
        return redirect(url_for('login'))

@students_blueprint.route('/profile', methods=['GET', 'POST'])
def profile():
    if session.get('email'):
        user = User.objects().filter(email=session.get('email')).first()
        # find the student assignments
        # for this we need to find the assignment which is open as well as same as the student school
        assignments = Assignment.objects(school=user.school.id)
        return render_template('student-profile.html', user=user, assignments=assignments)
    else:
        return redirect(url_for('login'))


# This method can access by only teacher
# Return the list of students
@students_blueprint.route('/', methods=['GET', 'POST'])
def student_list():
    if session.get('email'):
        user = User.objects().filter(email=session.get('email')).first()
        if user.user_type == 'instructor' or user.user_type == 'admin':
            # get the logged in user by session.get('email')
            students = User.objects().filter(user_type='student',attached='true')
            stud=User.objects().filter(user_type='student',attached=False)
            print(stud)
            total=User.objects().filter(user_type='student').count()
            attached=User.objects().filter(attached='true').count()
            return render_template('students.html', students=students,attach=attached, user=user,total=total,stud=stud)
        else:
            return redirect(url_for('students.profile'))
    else:
        return redirect(url_for('login'))


# This method can access by only teacher
# Approve a new student
@students_blueprint.route('/approve/<student_id>', methods=['GET', 'POST'])
def approve(student_id):
    if session.get('email'):
        user = User.objects().filter(email=session.get('email')).first()
        if user.user_type == 'instructor' or user.user_type == 'admin':
            # get the student by student_id
            # update the approve value to true
            student = User.objects().filter(id=student_id).first()
            msg = Message('Hello', sender = 'warumwa717@gmail.com', recipients = [student['email']])
            msg.body = "Hello student you have been approved for this platform"
            mail.send(msg)
            User.objects(id=student_id).update_one(approved=True) 
           
            return redirect(url_for('students.student_list'))
        else:
            return redirect(url_for('students.profile'))
    else:
        return redirect(url_for('login'))


# This method can access by only teacher
# Approve a new student
@students_blueprint.route('/remove/<student_id>', methods=['GET', 'POST'])
def remove(student_id):
    if session.get('email'):
        user = User.objects().filter(email=session.get('email')).first()
        if user.user_type == 'instructor' or user.user_type == 'admin':
            student = User.objects().filter(id=student_id).first()
            msg = Message('Hello student you have been removed from your class', sender = 'warumwa717@gmail.com', recipients = [student['email']])
            mail.send(msg)
            User.objects(id=student_id).delete()
            return redirect(url_for('students.student_list'))
        else:
            return redirect(url_for('students.profile'))
    else:
        return redirect(url_for('login'))


# Student Progress Report Route
@students_blueprint.route('/progress/<student_id>', methods=['GET', 'POST'])
def progress(student_id):
    if session.get('email'):
        teacher = User.objects().filter(email=session.get('email')).first()
        if teacher.user_type == 'instructor' or teacher.user_type == 'admin':

            student = User.objects(id=student_id).first()
            hist=History.objects().filter(email=student["email"])

            return render_template('student-progress.html', user=teacher,history=hist, student=student)
        else:
            return redirect(url_for('students.profile'))
    else:
        return redirect(url_for('login'))


@students_blueprint.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if session.get('email'):
        form = EditForm()
        user = User.objects().filter(email=session.get('email')).first()
        if request.method == 'POST' and form.validate():
            user.name = form.name.data
            user.surname = form.surname.data
            user.save()
            flash('Profile successfully updated !')
        return render_template('student-edit-profile.html', user=user, form=form)
    else:
        return redirect(url_for('login'))
