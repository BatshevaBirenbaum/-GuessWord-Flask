class User:
    def __init__(self, username,  id_number,password):
        self.username = username
        self.id_number = id_number
        self.password = password
        self.games_count = 0,
        self.list_words =  [],
        self.win_count = 0

    # הופכת את האובייקט שיהיה מסוג מילון
    def to_dict(self):
        return {
            "name": self.username,
            "id": self.id_number,
            "password": self.password,
            "games_count": 0,
            "list_words": [],
            "win_count": 0
        }