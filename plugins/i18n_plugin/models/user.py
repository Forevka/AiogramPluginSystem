import datetime


class User:
    def __init__(self, user_id: int, lang: str, created_at: datetime.datetime,):
        self.user_id = user_id
        self.lang = lang
        self.created_at = created_at