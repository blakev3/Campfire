from .thread import Thread

class Forum:
    def __init__(self, name):
        self.name = name
        self.threads = []

    def create_thread(self, author, title, description):
        thread = Thread(author, title, description)
        self.threads.append(thread)

    def edit_title(self, current_user, new_title):
        if current_user.id == "admin":
            self.title = new_title
            self.edited = True

    def find_thread(self, title):
        for thread in self.threads:
            if thread.title == title:
                return thread
        return None

    def __str__(self):
        forum_str = f"Forum: {self.name}\Fn"
        thread_str = "\n\n".join(map(str, reversed(self.threads)))
        return f"{forum_str}{thread_str}"
