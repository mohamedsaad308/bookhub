from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from bookhub import app, db, bcrypt, sql
from bookhub.forms import RegistrationForm, LoginForm, UpdateAccountForm, SearchForm, ReviewForm
from bookhub.models import *
from flask_login import login_user, logout_user, current_user, login_required, user_logged_in
from sqlalchemy import and_, or_, func
import requests



# homepage
@app.route("/")
def home():
    return render_template("home.html")

# route for registeration

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('search'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, 
                    email = form.email.data, 
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))


    return render_template('register.html', title='Register', form=form)


# to handle login and athorization
@login_manager.unauthorized_handler
def handle_needs_login():
    flash("You have to be logged in to access this page.", 'warning')
    return redirect(url_for('login', next=request.endpoint))
#To handle next requests
def redirect_dest(fallback):
    dest = request.args.get('next')
    try:
        dest_url = url_for(dest)
    except:
        return redirect(fallback)
    return redirect(dest_url)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect_dest(url_for('search'))
        else:
            flash("Login unsuccessful please check username and password", 'danger')


    return render_template('login.html', title='Login', form=form)

# To log the user out
@app.route("/logout", methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for("home"))

# Implementing the search page
@app.route("/search",  methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    books =[]
    page = request.args.get('page', 1, type=int)
    if form.validate_on_submit():
        searchword_like = f"%{form.searchword.data}%"
        if form.searchby.data=='title':
            books = Book.query.filter(Book.title.like(searchword_like)).paginate(page=page, per_page=5)
        elif form.searchby.data=='isbn':
            books = Book.query.filter(Book.isbn.like(searchword_like)).paginate(page=page, per_page=5)
        elif form.searchby.data=='author':
            books = Book.query.filter(Book.author.like(searchword_like)).paginate(page=page, per_page=5)
        elif form.searchby.data=='year':
            books = Book.query.filter(Book.year.like(searchword_like)).paginate(page=page, per_page=5)
        if books is None:
            
            flash('No books matched your search, change your search and try again', 'warning')

    # elif request.method=='GET':
    #     books =[]
    #     # test='I came here with get method'
    #     # form.searchword.data = "Enter search word here!"
    
    return render_template('search.html', books=books, form=form)

# account page
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account updated successfully!', 'success')
        return redirect(url_for('account'))
    elif request.method=='GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template('account.html', form=form)
# the book page
# to pull book description and book image from google api 
def google_info(book_id):
    book = Book.query.get(book_id)
    res = requests.get(
    'https://www.googleapis.com/books/v1/volumes',
    params={'q': str(book.isbn)})
    data = res.json()
    try:
        book_cover = data['items'][0]['volumeInfo']['imageLinks']['thumbnail']
        book_description = data['items'][0]['volumeInfo']['description']
    except:
        book_cover = "https://blog.springshare.com/wp-content/uploads/2010/02/nc-md.gif"
        book_description = "No Book description available"
    return(book_cover, book_description)
# Route for the book page 
@app.route("/books/<int:book_id>", methods=['GET', 'POST'])
@login_required
def book(book_id):
    book = Book.query.get(book_id)
    if book is None:
        flash("There's no such book, modify your search and try again!", 'warning')
        return redirect(url_for('search'))
    review_count_goodreads, goodreads_avg_rate = books_api(book_id)[0],  books_api(book_id)[1]
    title = Book.query.get(book_id).title
    form = ReviewForm()
    current_id = current_user.id
    if form.validate_on_submit():
        user = Review.query.filter(and_(Review.user_id==current_id, Review.book_id==book_id)).first()
        if user:
            flash('You are allowed to review a book once', 'warning')
        elif form.book_rate.data == 'XX':
            flash('Please choose a valid rate', 'warning')
        else:
            review = Review(rate=form.book_rate.data, body=form.book_review.data,user=current_user, book_id=book_id)
            db.session.add(review)
            db.session.commit()
        
    book_cover, book_description = google_info(book_id)
    reviews = Review.query.filter(Review.book_id==book_id).all()

    return render_template('book.html', book=book, title=title, form=form, reviews=reviews, id=current_id,
                            goodreads_avg_rate=goodreads_avg_rate, review_count_goodreads=review_count_goodreads,
                            book_cover=book_cover, book_description=book_description)

@app.route("/updatereview/<int:review_id>", methods=['GET', 'POST'])
@login_required
def update_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.user != current_user:
        abort(403)
    form = ReviewForm()
    if form.validate_on_submit():
        review.rate =  form.book_rate.data
        review.body = form.book_review.data
        book_id = review.book_id
        db.session.commit()
        flash('Your review has been  been updated!', 'success')
        return redirect(url_for('book', book_id=book_id))
    elif request.method=='GET':
        form.book_rate.data = review.rate
        form.book_review.data = review.body
    return render_template('update_review.html', form=form, title='Update review')


@app.route("/deletereview/<int:review_id>", methods=['POST'])
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.user != current_user:
        abort(403)
    book_id = review.book_id
    db.session.delete(review)
    db.session.commit()
    flash('Your review has been deleted', 'success')
    return redirect(url_for('book', book_id=book_id))
# Website API
def books_api(book_id):
    
    book = Book.query.get_or_404(book_id)
    isbn = book.isbn
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "At03u6afUSw1DPBO7Rzmg", "isbns": isbn})
    data = res.json()
    average_rating = data['books'][0]['average_rating']
    review_count = data['books'][0]['work_ratings_count']
    bookhub_review_count = sql.execute("SELECT * FROM reviews WHERE book_id = :id", {"id": book_id}).rowcount
    if bookhub_review_count==0:
        bookhub_review_average="No reviews Yet"
    else:
        bookhub_review_average_rowproxy = sql.execute("SELECT AVG(rate) FROM reviews WHERE book_id = :id", {"id": book_id})
        d, a = {}, []
        for rowproxy in bookhub_review_average_rowproxy:
            # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
            for column, value in rowproxy.items():
                # build up the dictionary
                d = {**d, **{column: value}}
            a.append(d)
            bookhub_review_average = round(int(a[0]['avg']), 2)
    return (review_count, average_rating, bookhub_review_count, bookhub_review_average)
@app.route("/api/books/<int:book_id>")
@login_required
def book_api(book_id):
    book = Book.query.get_or_404(book_id)
    review_count, average_rating, bookhub_review_count, bookhub_review_average = books_api(book_id)
   
    try:
        return jsonify({
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "isbn": book.isbn,
            "review_count_goodreads": review_count,
            "average_score_goodreads": average_rating,
            "review_count_bookhub": bookhub_review_count,
            "average_score_bookhub": bookhub_review_average
            })

    except:
        return "<h1>API connection problem, Try again later!</h1>"
    