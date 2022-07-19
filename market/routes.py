from flask import redirect, render_template, url_for, flash, request
from market.models import Item, User
from market import app, db
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from flask_login import login_user, logout_user, login_required, current_user


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/market', methods = ['GET','POST'])
@login_required
def market_page():
    purchaseForm = PurchaseItemForm()
    sellForm = SellItemForm()
    

    if request.method == 'POST':
        purchased_item = request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name = purchased_item).first()
        if p_item_object:
            if current_user.valid_purchase(p_item_object):
                p_item_object.buy(current_user)
  
                flash(f"You've successfully purchased for {p_item_object.name} for {p_item_object.price}$", category='success')
            else:
                flash(f"Transaction Failed, You don't have enough money to purchase {p_item_object.name}!", category='danger')

        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        
        if s_item_object:
            s_item_object.owner = None
            current_user.budget += s_item_object.price
            db.session.commit()
            flash(f"You've successfully sold {s_item_object.name} for {s_item_object.price}$", category='danger')


        return redirect(url_for('market_page'))

    if request.method == 'GET':
        items = Item.query.filter_by(owner = None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', items = items, purchaseForm = purchaseForm, owned_items = owned_items, sellForm = sellForm)


@app.route('/signup', methods = ['GET','POST'])
def signup_page():
    form = RegisterForm()
    #if any validators given in the forms are not successful, the below if condition won't be True. 
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account Created Successfully!, You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('market_page'))
    
    if(len(form.errors) != 0): # there are some errors
        for err_msg in form.errors.values():
            flash(f'There was an error {err_msg}', category= 'danger')

    return render_template('register.html', form = form)


@app.route('/login', methods= ['GET','POST'])
def login_page():
    form = LoginForm()

    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username = form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password = form.password.data):
            login_user(attempted_user) 
            flash(f"You're logged In as {attempted_user.username}", category='success')
            return redirect(url_for('market_page'))
        else:
            flash("Incorrect Credentials, Please try again!", category= 'danger')
    return render_template('login.html', form = form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash("You've been Logged out!", category='info')
    return redirect(url_for('home_page'))