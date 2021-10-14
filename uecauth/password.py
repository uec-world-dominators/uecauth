import getpass


class PasswordProvider():
    '''
    パスワード取得の基底クラス
    '''

    def get(self):
        raise NotImplementedError()

    def max_attempts(self):
        raise NotImplementedError()


class DefaultPasswordProvider(PasswordProvider):
    '''
    コンストラクタで設定したユーザ名・パスワードを用いる
    '''

    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password

    def get(self):
        return self.username, self.password

    def max_attempts(self):
        return 1


class PromptingPasswordProvider(PasswordProvider):
    '''
    プロンプトを表示してユーザ名・パスワードを尋ねる
    '''

    def get(self):
        return input('Username? '), getpass.getpass('Password? ')

    def max_attempts(self):
        return 3
