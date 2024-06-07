from datetime import datetime

class Post:
    def __init__(self, author, content):
        self.author = author
        self.content = content
        self.edited = False
        self.edited_by_admin = False
        self.timestamp = datetime.utcnow()

    def edit(self, new_content, edited_by_admin):
        self.content = new_content
        self.edited = True
        self.edited_by_admin = edited_by_admin
        
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
        return f"{self.author}: {self.content}"