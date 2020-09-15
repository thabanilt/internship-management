# This is app.py, this is the main file called.
from newnotes import app
from flask import render_template, request, session, redirect, url_for, flash
from newnotes.forms import LoginForm, AdminForm
from newnotes.models import User, School, Module1, Module2, Module3, Assignment,Jobs
from bson import ObjectId
import bcrypt


@app.route('/')
def home():
    jo= Jobs.objects().filter()
    return render_template('home.html',job=jo)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # first check if the request is get or post
    if request.method == 'POST':
        if form.validate():
            # if request is post then grab the data from the request
            email = form.email.data
            password = form.password.data.encode('utf-8')
            # check if the user exist in the database using the given credentials
            user = User.objects().filter(email=email).first()
            # if user exists then check the password
            if user:
                if bcrypt.checkpw(password, user.password):
                    session['email'] = form.email.data
                    # Check the type of the user.
                    # If user is a student then redirect that user to the student profile
                    # If user is a instructor then redirect that user to the teacher profile
                    if user.user_type == 'instructor' or user.user_type == 'admin':
                        return redirect(url_for('teachers.profile'))
                    return redirect(url_for('students.profile'))
                else:
                    # if password is incorrect than show the below message
                    flash('Email or password is incorrect')
                    return redirect(url_for('login'))
            else:
                # if user not found then show the same login page
                # we can set a flash message that email or password is incorrect
                flash('No user found. please sign up')
                return redirect(url_for('login'))

    # if everything is okay then delete the password from the user object
    # set the user into the session
    # redirect the user in profile page
    return render_template('login.html', form=form)


@app.route('/admin/create', methods=['GET', 'POST'])
def create():
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
            flash('User with this email already exist')
            return redirect(url_for('create'))
    return render_template('register.html', form=form)

@app.route('/edit_profile', methods=['GET', 'POST'])
def profile_edit():
    if session.get('email'):
        user = User.objects().filter(email=session.get('email')).first()
        if user.user_type == 'instructor' or user.user_type == 'admin':
            return redirect(url_for('teachers.edit_profile'))
        else:
            return redirect(url_for('students.edit_profile'))
    else:
        return redirect(url_for('login'))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if session.get('email'):
        session.clear()
    return redirect(url_for('login'))


################################################################

# Error page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, port=8080)
