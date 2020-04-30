#coding:utf-8

"""
1ユーザーのログイン情報を保持する
"""
class LogObject(object):
    def __init__(self):
        self._user_id = None
        self._date = None
        self._use_times = None

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, user_id):
        self._user_id = user_id

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, date):
        self._date = date

    @property
    def use_times(self):
        return self._use_times

    @use_times.setter
    def use_times(self, use_times):
        self._use_times = use_times