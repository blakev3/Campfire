from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.serving import run_simple
from scripts.forum import Forum
import json, os


app = Flask(__name__) 

app.secret_key = '872c7e22346f8cca2530abfcf213bab94908473e7a1ec7e4' # import os; print(os.urandom(24).hex())

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# User class for authentication
class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.load_user_data()
    
    def load_user_data(self):
        user_data = database.users.get(self.id, {})
        self.xp = user_data.get("xp", 0)
        self.level = user_data.get("level", 1)
        self.update_level()

    
    def save_user_data(self):
        database.users[self.id] = {
            "xp": self.xp,
            "level": self.level
        }
        with open('data/users.json', 'w') as f:
            json.dump(database.users, f)

    def update_level(self):
        level_thresholds = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
        for level, threshold in enumerate(level_thresholds):
            if self.xp >= threshold:
                self.level = level + 1




class Database:
    def __init__(self):
        with open('data/users.json') as f:
            self.users = json.load(f)

        self.friendships = {}

database = Database()

# Initialize the forum
my_forum = Forum("Campfire")

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route("/")
def index():
    return render_template("index.html", forum=my_forum, current_user=current_user)


@app.route("/create_thread", methods=["POST"])
@login_required
def create_thread():
    author = current_user.id
    title = request.form.get("title")
    description = request.form.get("description")
    
    if len(title) > 20:
        flash("Thread title must be 20 characters or less.", "danger")
        return redirect(url_for("index"))
    
    if len(description) > 200:
        flash("Thread description must be 200 characters or less.", "danger")
        return redirect(url_for("index"))
    
    with open("mod/src/swearWords.txt", encoding="utf8") as f:
        banned_words = f.read().split("\n")

    title_lower = title.lower()
    description_lower = description.lower()

    banned_words_lower = [word.lower() for word in banned_words]

    if any(word in title_lower or word in description_lower for word in banned_words_lower):
        flash("Your thread was picked up as possibly offensive, please refrain from creating offensive threads.", "danger")
    else:
        my_forum.create_thread(author, title, description)
        current_user.xp += 5
        current_user.save_user_data()

    return redirect(url_for("index"))


@app.route("/thread/<thread_title>", methods=["GET", "POST"])
def thread(thread_title):
    current_thread = my_forum.find_thread(thread_title)
    
    if request.method == "POST":
        author = current_user.id if current_user.is_authenticated else "Anonymous"
        content = request.form.get("content")
        with open("mod/src/swearWords.txt", encoding="utf8") as f:
            banned_words = f.read().split("\n")

        content_lower = content.lower()
        banned_words_lower = [word.lower() for word in banned_words]

        if any(word in content_lower for word in banned_words_lower):
            flash("Your post was picked up as possibly offensive, please refrain from posting offensive content.", "danger")
        else:
            current_thread.add_post(author, content)
            current_user.xp += 1
            current_user.save_user_data()
    
    return render_template("thread.html", thread=current_thread, current_user=current_user)


@app.route("/thread/<thread_title>/edit/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(thread_title, post_id):
    current_thread = my_forum.find_thread(thread_title)

    if current_thread is None:
        flash("Thread not found.", "warning")

    if post_id < 0 or post_id >= len(current_thread.posts):
        flash("Post not found.", "danger")

    post = current_thread.posts[post_id]

    if current_user.id != post.author and current_user.id != "admin":
        flash("You don't have permission to edit this post.", "warning")
        return redirect(url_for("thread", thread_title=thread_title))

    if request.method == "POST":
        new_content = request.form.get("new_content")
        
        edited_by_admin = current_user.id == "admin"

        with open("mod/src/swearWords.txt", encoding="utf8") as f:
            banned_words = f.read().split("\n")

        new_content_lower = new_content.lower()
        banned_words_lower = [word.lower() for word in banned_words]

        if any(word in new_content_lower for word in banned_words_lower):
            flash("Your edit was picked up as possibly offensive, please refrain from posting offensive content.", "danger")
        else:
            post.edit(new_content, edited_by_admin)
        return redirect(url_for("thread", thread_title=thread_title))

    return render_template("edit_post.html", post=post, thread_title=thread_title, post_id=post_id)


@app.route("/thread/<thread_title>/delete/<int:post_id>")
@login_required
def delete_post(thread_title, post_id):
    current_thread = my_forum.find_thread(thread_title)
    
    if current_thread is None:
        flash("Thread not found.", "warning")
    
    if post_id < 0 or post_id >= len(current_thread.posts):
        flash("Post not found.", "danger")
    
    post = current_thread.posts[post_id]
    
    if current_user.id != post.author and current_user.id != "admin":
        flash("You don't have permission to delete this post.", "warning")
        return redirect(url_for("thread", thread_title=thread_title))
    
    del current_thread.posts[post_id]
    return redirect(url_for("thread", thread_title=thread_title))


@app.route("/thread/<thread_title>/edit", methods=["GET", "POST"])
@login_required
def edit_thread(thread_title):
    current_thread = my_forum.find_thread(thread_title)
    
    if current_user.id != current_thread.author:
        flash("You don't have permission to edit this thread.", "warning")
    
    if request.method == "POST":
        new_title = request.form.get("new_title")
        current_thread.edit_title(new_title)
        return redirect(url_for("thread", thread_title=new_title))
    
    return render_template("edit_thread.html", thread=current_thread)


@app.route("/thread/<thread_title>/upvote", methods=["POST"])
@login_required
def upvote_thread(thread_title):
    current_thread = my_forum.find_thread(thread_title)
    
    if current_thread:
        user_id = current_user.id
        
        if user_id == current_thread.author:
            flash("You cannot upvote your own thread.", "warning")
            return redirect(url_for("thread", thread_title=thread_title))
        
        if user_id in current_thread.upvoted_by:
            current_thread.cancel_upvote(user_id)
            current_thread.downvote(user_id)
            current_user.xp += 2
            current_user.save_user_data()
        elif user_id in current_thread.downvoted_by:
            current_thread.cancel_downvote(user_id)
        else:
            current_thread.downvote(user_id)
            author_id = current_thread.author
            author_user = User(author_id)
            author_user.xp += 10
            update_level(author_user)
            author_user.save_user_data()
        
        current_user.save_user_data()
        return redirect(url_for("thread", thread_title=thread_title))
    else:
        flash("Thread not found.", "danger")
        return redirect(url_for("index"))

@app.route("/thread/<thread_title>/downvote", methods=["POST"])
@login_required
def downvote_thread(thread_title):
    current_thread = my_forum.find_thread(thread_title)
    if current_thread:
        user_id = current_user.id
        
        if user_id == current_thread.author:
            flash("You cannot downvote your own thread. (Why would you even want to do that?)", "warning")
            return redirect(url_for("thread", thread_title=thread_title))
        
        if user_id in current_thread.downvoted_by:
            current_thread.cancel_downvote(user_id)
            current_thread.upvote(user_id)
            current_user.xp -= 2
            current_user.update_level()
            current_user.save_user_data()
        elif user_id in current_thread.upvoted_by:
            current_thread.cancel_upvote(user_id)
        else:
            current_thread.downvote(user_id)
            author_id = current_thread.author
            author_user = User(author_id)
            author_user.xp -= 5
            update_level(author_user)
            author_user.save_user_data()
        
        current_user.save_user_data()
        return redirect(url_for("thread", thread_title=thread_title))
    else:
        flash("Thread not found.", "danger")
        return redirect(url_for("index"))



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        username_lower = username.lower()
        
        if username_lower in (name.lower() for name in database.users):
            flash("Username already exists. Please choose a different one.", "warning")
            return render_template("register.html")
        if len(username) > 20:
            flash("Username must be under 20 characters", "danger")
            return redirect(url_for("index"))
        else:
            with open("mod/src/swearWords.txt", encoding="utf8") as f:
                banned_words = f.read().split("\n")

            if any(word in username_lower for word in banned_words):
                flash("Your username was picked up as possibly offensive, please refrain from using offensive usernames.", "danger")
            else:
                hashed_password = generate_password_hash(password)
                database.users[username_lower] = {"password": hashed_password}
                with open('data/users.json', 'w') as f:
                    json.dump(database.users, f)
                flash(f"Registration successful! Welcome to Campfire, {username}!", "success")
                user = User(username)
                login_user(user)
            return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    if request.method == "POST":
        # Perform account deletion logic here
        # Example: Delete the user and their data from the database
        if current_user.id in database.users:
            del database.users[current_user.id]
        else:
            print("User ID not found in the database.")
        with open('data/users.json', 'w') as f:
            json.dump(database.users, f)

        # Log the user out after deleting their account
        logout_user()

        flash("Your account has been deleted.", "danger")
        return redirect(url_for("index"))

    return redirect(url_for("index"))



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # Access the users attribute on the database instance
        if username in database.users and check_password_hash(database.users[username], password):
            user = User(username)
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Login failed. Please check your username and password.", "danger")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/account")
@login_required
def account():
    return render_template("account.html", current_user=current_user)
    
    
@app.route('/send_friend_request/<int:user_id>', methods=['POST'])
@login_required
def send_friend_request(user_id):
    current_user_id = current_user.id
    if current_user_id != user_id:
        # Check if the friend request has already been sent
        if current_user_id not in database.friendships:
            database.friendships[current_user_id] = set()
        if user_id not in database.friendships[current_user_id]:
            database.friendships[current_user_id].add(user_id)
            flash("Friend request sent.", "success")
        else:
            flash("Friend request already sent.", "info")
    return redirect(url_for('index'))


@app.route('/accept_friend_request/<int:request_id>', methods=['POST'])
@login_required
def accept_friend_request(request_id):
    current_user_id = current_user.id
    if current_user_id in database.friendships:
        if request_id in database.friendships[current_user_id]:
            # Add friendship relationship
            if request_id not in database.friendships:
                database.friendships[request_id] = set()
            database.friendships[request_id].add(current_user_id)
            flash("Friend request accepted.", "success")
        else:
            flash("Invalid friend request.", "danger")
    else:
        flash("Invalid friend request.", "danger")
    return redirect(url_for('index'))


@app.route('/reject_friend_request/<int:request_id>', methods=['POST'])
@login_required
def reject_friend_request(request_id):
    current_user_id = current_user.id
    if current_user_id in database.friendships:
        if request_id in database.friendships[current_user_id]:
            database.friendships[current_user_id].remove(request_id)
            flash("Friend request rejected.", "info")
        else:
            flash("Invalid friend request.", "danger")
    else:
        flash("Invalid friend request.", "danger")
    return redirect(url_for('index'))


@app.route('/list_friends/<int:user_id>')
@login_required
def list_friends(user_id):
    if user_id in database.friendships:
        friend_ids = database.friendships[user_id]
        friends = [User(id) for id in friend_ids]
        return render_template('friends.html', friends=friends)
    else:
        flash("You have no friends yet.", "info")
        return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))