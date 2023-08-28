from SheetEditor import Editor
from script import script, Stage
import datetime


class User:
    def __init__(self, chat_id, uid, uname, stage=1, state=1, ping_time=-1, ping_stage=-1, data=None, interrupt_stage=None):
        self.chat_id = chat_id
        if uname is not None:
            self.uname = uname
        else:
            self.uname = uid
        self.uid = uid
        self.stage = stage
        self.state = state
        # user states:
        #   even number - bot is typing, user can`t write
        #   1 - waiting for an answer
        #   3 - afk
        self.ping_time = ping_time
        self.ping_stage = ping_stage
        self.data = data
        self.interrupt_stage = interrupt_stage


class GameMaster:
    def __init__(self, editor: Editor):
        self.active_users = dict()
        self.editor = editor

    def reply(self, chat_id, msg):
        if chat_id not in self.active_users:
            if self.editor.is_new_user(chat_id) or self.editor.get_day(chat_id) == 1:
                return script[-11]['*'], False
            else:
                return script[-12]['*'], False

        user = self.active_users[chat_id]
        if user.state % 2 == 0:
            if user.interrupt_stage is not None:
                return script[user.interrupt_stage]['*'], False
            else:
                return None, False

        # logging in
        if user.stage < 100:
            self.collect_data(user, msg)
        # end day
        if user.stage % 100 == 99:
            # TODO un/comment
            self.end_day(chat_id)

        if msg in script[user.stage]:
            new_stage = script[user.stage][msg]
        else:
            new_stage = script[user.stage]['*']

        user.stage = new_stage.next_stage
        user.state = 2
        user.interrupt_stage = new_stage.interrupt_stage
        return new_stage, True

    def end_reply(self, chat_id, ping_stage):
        if chat_id in self.active_users:
            user = self.active_users[chat_id]
            user.state -= 1
            # TODO set ping delay
            time = datetime.datetime.now() + datetime.timedelta(seconds=600)
            user.ping_time = int(time.timestamp())
            user.ping_stage = ping_stage
            user.interrupt_stage = None

    def add_user(self, chat_id, uname, uid):
        if (chat_id not in self.active_users) and (self.editor.is_new_user(chat_id) or self.editor.get_day(chat_id) == 1):
            self.active_users[chat_id] = User(chat_id, uid, uname, data=list())
            return True
    def collect_data(self, user, text):
        if 2 <= user.stage <= 3:
            user.data.append(text)
        if user.stage == 3:
            if self.editor.is_new_user(user.uid):
                self.editor.add_user(user.chat_id, user.uid, user.uname, *user.data)

    def end_day(self, chat_id):
        self.editor.end_day(chat_id)
        self.active_users.pop(chat_id)

    def ping_inactive(self):
        time = int(datetime.datetime.now().timestamp())
        pings = []
        for i in self.active_users.items():
            chat_id, user = i
            if user.state == 1 and 0 <= user.ping_time <= time:
                pings.append((chat_id, script[user.ping_stage]['*']))
                user.state = 3
        return pings

    def get_user_data(self, chat_id):
        if chat_id in self.active_users:
            user = self.active_users[chat_id]
            return f'USER:{user.uname}, Stage:{user.stage}, State:{user.state}'
        return 'user is not active'
