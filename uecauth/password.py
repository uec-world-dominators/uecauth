class PasswordProvider():
    def get(self):
        pass


class DefaultPasswordProvider(PasswordProvider):
    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password

    def get(self):
        return self.username, self.password


class PromptingPasswordProvider(PasswordProvider):
    def get(self):
        return input('Username? '), input('Password? ')
