from app import app, db, mail
from flask import render_template, redirect, url_for, flash
from flask_login import login_user ,logout_user, current_user, login_required
from flask_mail import Message
from app.forms import PhonebookForm, PostForm, UserInfoForm, LoginForm
from app.models import Post, User, Phonebook


@app.route('/') 
def index():
    title = 'Home'
    posts = Post.query.all()
    
    return render_template('index.html', title=title, posts=posts )

@app.route('/register', methods=['GET', 'POST'])
def register():
    title = 'Register'
    register_form = UserInfoForm()
    if register_form.validate_on_submit():
        username = register_form.username.data
        email = register_form.email.data
        password = register_form.password.data

        # Check if username from the form already exists in the User table
        existing_user = User.query.filter_by(username=username).all()
        # If there is a user with that username, message them asking them to try again
        if existing_user:
            # Flash a warning message 
            flash(f'The username {username} is already registered. Please try again.', 'danger')
            # Redirect back to the register page
            return redirect(url_for('register'))        

        # Create a new user instance
        new_user = User(username, email, password)
        # Add that user to the database
        db.session.add(new_user)
        db.session.commit()
        # Flash a success message thanking them for signing up
        flash(f'Thank you {username}, you have successfully registered!', 'success')

        # Create Welcome Email to new user
        welcome_message = Message('Welcome to the Kekambas Blog!', [email])
        welcome_message.body = f'Dear {username}, Thank you for signing up for our blog. We are so excited to have you!'

        # Send Welcome Email
        mail.send(welcome_message)

        # Redirecting to the home page
        return redirect(url_for('index'))

    return render_template('register.html', title=title, form=register_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    title= 'Login'
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Query our User table for a user with username
        user = User.query.filter_by(username=username).first()

        # Check if the user is None or if password is incorrect
        if user is None or not user.check_password(password):
            flash('Your username or password is incorrect', 'danger')
            return redirect(url_for('login'))

        login_user(user)

        flash(f'Welcome {user.username}. You have successfully logged in.', 'success')

        return redirect(url_for('index'))

    return render_template('login.html', title=title, login_form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/my_account') 
@login_required 
def my_account():     
    title = 'My Account'
    return render_template('my_account.html', title=title)

@app.route('/phonebook')
@login_required
def phonebook():
    title = 'Phonebook'
    phonebooks = Phonebook.query.all()
    return render_template('phonebook.html',title=title, phonebooks=phonebooks)


@app.route('/create-phonebook', methods=['GET', 'POST'])
@login_required
def create_phonebook():
    title = 'Create Phonebook'
    register_phone_form = PhonebookForm()
    if register_phone_form.validate_on_submit():
        first_name = register_phone_form.first_name.data
        last_name = register_phone_form.last_name.data
        phone_number = register_phone_form.phone_number.data
        address = register_phone_form.address.data
        print(first_name, last_name, phone_number, address)

        new_phonebook = Phonebook(first_name, last_name, phone_number, address, current_user.id)
        
        db.session.add(new_phonebook)
        db.session.commit()

        flash(f'Thank you {first_name} {last_name}, you have successfully registered your info in the phonebook!', 'success')
        return redirect(url_for('phonebook'))

    return render_template('create_phonebook.html', title=title, phonebook_form=register_phone_form)

@app.route('/my-phonebooks')
@login_required
def my_phonebooks():
    phonebooks = current_user.phonebooks
    return render_template('my_phonebooks.html', phonebooks=phonebooks)

@app.route('/phonebook/<int:phonebook_id>')
def phonebook_detail(phonebook_id):
    phonebook = Phonebook.query.get_or_404(phonebook_id)
    return render_template('phonebook_detail.html', phonebook=phonebook)

@app.route('/createpost', methods=['GET', 'POST'])
@login_required
def createpost():
    title = 'Create Post'
    form = PostForm()
    if form.validate_on_submit():
        print('Hello')
        title = form.title.data
        content = form.content.data

        new_post = Post(title, content, current_user.id)

        db.session.add(new_post)
        db.session.commit()

        flash(f'The post {title} has been created.', 'primary')
        return redirect(url_for('index'))

    return render_template('createpost.html', title=title, form=form)


@app.route('/my_posts')
@login_required
def my_posts():
    posts = current_user.posts
    return render_template('my_posts.html', posts=posts)


@app.route('/posts/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)

@app.route('/phonebooks/<int:phonebook_id>/update', methods=["GET", "POST"])
@login_required
def phonebook_update(phonebook_id):
    phonebook = Phonebook.query.get_or_404(phonebook_id)
    # check if user trying to update phonebook is same as user logged in
    if phonebook.author.id != current_user.id:
        flash('You may only edit phonebooks you have created.', 'danger')
        return redirect(url_for('my_phonebooks'))

    form = PhonebookForm()

    if form.validate_on_submit():
        new_first_name = form.first_name.data
        new_last_name = form.last_name.data
        new_phone_number = form.phone_number.data
        new_address = form.address.data
        print(new_first_name, new_last_name, new_phone_number, new_address)
        phonebook.first_name = new_first_name
        phonebook.last_name = new_last_name
        phonebook.phone_number = new_phone_number
        phonebook.address = new_address
        db.session.commit()

        flash(f'{phonebook.first_name} {phonebook.last_name} has been updated', 'success')
        return redirect(url_for('phonebook_detail', phonebook_id=phonebook.id))

    return render_template('phonebook_update.html', phonebook=phonebook, form=form)

@app.route('/posts/<int:post_id>/update', methods=["GET", "POST"])
@login_required
def post_update(post_id):
    post = Post.query.get_or_404(post_id)
    # check if user trying to update post is same as user logged in
    if post.author.id != current_user.id:
        flash('You may only edit posts you have created.', 'danger')
        return redirect(url_for('my_posts'))

    form = PostForm()

    if form.validate_on_submit():
        new_title = form.title.data
        new_content = form.content.data
        print(new_title, new_content)
        post.title = new_title
        post.content = new_content
        db.session.commit()

        flash(f'{post.title} has been updated', 'success')
        return redirect(url_for('post_detail', post_id=post.id))

    return render_template('post_update.html', post=post, form=form)


@app.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash('You can only delete your own posts', 'danger')
        return redirect(url_for('my_posts'))

    db.session.delete(post)
    db.session.commit()

    flash(f'{post.title} has been deleted', 'success')
    return redirect(url_for('my_posts'))

@app.route('/phonebooks/<int:phonebook_id>/delete', methods=['POST'])
@login_required
def delete_phonebook(phonebook_id):
    phonebook = Phonebook.query.get_or_404(phonebook_id)
    if phonebook.author != current_user:
        flash('You can only delete your own phonebooks', 'danger')
        return redirect(url_for('my_phonebooks'))

    db.session.delete(phonebook)
    db.session.commit()

    flash(f'{phonebook.first_name} {phonebook.last_name} has been deleted', 'success')
    return redirect(url_for('my_phonebooks'))
    