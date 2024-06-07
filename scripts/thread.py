from .post import Post
from datetime import datetime

class Thread:
    def __init__(self, author, title, description):
        self.author = author
        self.title = title
        self.description = description
        self.posts = []
        self.edited = False
        self.timestamp = datetime.utcnow()
        self.upvotes = 0
        self.downvotes = 0
        self.upvoted_by = set()
        self.downvoted_by = set()

    def upvote(self, user_id):
        self.upvotes += 1
        self.upvoted_by.add(user_id)

    def downvote(self, user_id):
        self.downvotes += 1
        self.downvoted_by.add(user_id)

    def cancel_upvote(self, user_id):
        self.upvotes -= 1
        self.upvoted_by.remove(user_id)

    def cancel_downvote(self, user_id):
        self.downvotes -= 1
        self.downvoted_by.remove(user_id)

    def add_post(self, author, content):
        if any(post.content == content for post in self.posts):
            flash("You have already posted the same content in this thread.", "warning")
            return

        post = Post(author, content)
        self.posts.insert(0, post)

    def edit_post(self, current_user, post_id, new_content):
        if 0 <= post_id < len(self.posts):
            edited_by_admin = current_user.id == "admin"
            self.posts[post_id].edit(new_content, edited_by_admin)
            self.edited = True

    def delete_post(self, post_id):
        if 0 <= post_id < len(self.posts):
            del self.posts[post_id]

    @staticmethod
    def get_timestamp(timestamp):
        time_since_post = datetime.utcnow() - timestamp
        if time_since_post.days > 0:
            return f"{time_since_post.days} {'day' if time_since_post.days == 1 else 'days'} ago"
        elif time_since_post.seconds // 3600 > 0:
            hours = time_since_post.seconds // 3600
            return f"{hours} {'hour' if hours == 1 else 'hours'} ago"
        elif time_since_post.seconds // 60 > 0:
            minutes = time_since_post.seconds // 60
            return f"{minutes} {'minute' if minutes == 1 else 'minutes'} ago"
        else:
            return "just now"


    def __str__(self):
        thread_str = f"Thread: {self.title}\n"
        post_str = "\n".join(map(str, self.posts))
        return f"{thread_str}{post_str}"