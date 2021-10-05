class PasswordProvider():
    '''
    パスワード取得の基底クラス
    '''

    def get(self):
        pass


class DefaultPasswordProvider(PasswordProvider):
    '''
    コンストラクタで設定したユーザ名・パスワードを用いる
    '''

    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password

    def get(self):
        return self.username, self.password


class PromptingPasswordProvider(PasswordProvider):
    '''
    プロンプトを表示してユーザ名・パスワードを尋ねる
    '''

    def get(self):
        return input('Username? '), input('Password? ')
