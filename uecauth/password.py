import os
import sys


class PasswordProvider():
    def get(self):
        pass


class EnvironmentPasswordProvider(PasswordProvider):
    def __init__(self, username_envvar, password_envvar) -> None:
        self.username_envvar = username_envvar
        self.password_envvar = password_envvar

    def get(self):
        username = os.environ.get(self.username_envvar, None)
        password = os.environ.get(self.password_envvar, None)

        if not username:
            print(f'Username not found in environment variable: {self.username_envvar}', file=sys.stderr)
            exit(1)
        if not password:
            print(f'Password not found in environment variable: {self.password_envvar}', file=sys.stderr)
            exit(1)

        return username, password


class PromptingPasswordProvider(PasswordProvider):
    def get(self):
        return input('Username? '), input('Password? ')
