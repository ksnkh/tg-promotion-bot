import gspread
from oauth2client.service_account import ServiceAccountCredentials


class Editor:
    def __init__(self, sheet_name):
        self.sheet_name = sheet_name

        scope = ['https://www.googleapis.com/auth/spreadsheets',
                 'https://www.googleapis.com/auth/drive']
        cred_file = './sheets_key.json'
        credentials = ServiceAccountCredentials.from_json_keyfile_name(cred_file, scope)
        self.client = gspread.authorize(credentials)
        self.sheet = self.client.open(self.sheet_name).sheet1
        # data = [[chat_id, uid, uname, day], ...]
        self.data = []
        self.update_data()

    # DONE
    def login(self):
        try:
            self.client.login()
            self.sheet = self.client.open(self.sheet_name).sheet1
            return
        except Exception as e:
            print(f"Failed to log in: {e}")
            return

    # DONE
    def fetch_data(self):
        try:
            return self.sheet.get_all_values()
        except Exception as e:
            print('Error in _get_data:', e)
        try:
            self.login()
            return self.sheet.get_all_values()
        except Exception as e:
            print('Error in _get_data:', e)

    # DONE
    def edit_data(self, span, content):
        try:
            self.sheet.update(span, content)
            self.update_data()
            return
        except Exception as e:
            print(e)
            self.login()
        try:
            self.sheet.update(span, content)
            self.update_data()
            return
        except Exception as e:
            print('Error by sheet editing', e)

    # DONE
    def update_data(self):
        self.data = list()
        for i in self.fetch_data()[1:]:
            if i[0] != '':
                self.data.append([int(i[0]), int(i[1]), i[2], int(i[5])])
            else:
                self.data.append([0, 0, 'fuck', -1])

    # DONE
    def get_day(self, chat_id):
        for i in self.data:
            if i[0] == chat_id:
                return i[3]

    # DONE
    def end_day(self, chat_id):
        r = 2
        for i in self.data:
            if i[0] == chat_id:
                self.edit_data(f'F{r}:F{r}', [[i[3] + 1]])
                return
            r += 1

    # DONE
    def add_user(self, chat_id, uid, uname, name, number, day=1):
        self.edit_data(f'A{len(self.data) + 2}:F{len(self.data) + 2}', [[chat_id, uid, uname, name, number, day]])
        return

    # DONE
    def is_new_user(self, chat_id):
        # TODO un/comment
        for i in self.data:
            if chat_id == i[0]:
                return False
        return True

    # DONE
    def default(self):
        # self.sheet.batch_clear([f'A2:F{len(self.sheet.get_all_values()) + 1}'])
        # self.update_data()
        # self.add_user(83530498, 83530498, '@lena_logo_ped', '', '', 2)
        # uself.add_user(124865082, 124865082, '@ksnkh', 'KostaN', 21212, 2)
        self.update_data()


if __name__ == "__main__":
    editor = Editor('user data')
    editor.default()
