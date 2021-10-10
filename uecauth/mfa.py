import os
import pyotp


class MFAuthCodeProvider():
    '''
    二段階認証コード取得の基底クラス
    '''

    def get_code(self) -> str:
        raise NotImplementedError()

    def max_attempts(self):
        raise NotImplementedError()


class PromptingMFAuthCodeProvider(MFAuthCodeProvider):
    '''
    二段階認証コードをプロンプトから取得する
    '''

    def get_code(self):
        mfa_code = input('二段階認証コードを入力してください> ').strip()
        return mfa_code

    def max_attempts(self):
        return 3


class AutoTOTPMFAuthCodeProvider(MFAuthCodeProvider):
    '''
    二段階認証コードをコンストラクタに与えた秘密鍵から自動生成する
    '''

    def __init__(self, priv_key) -> None:
        self.totp = pyotp.TOTP(priv_key)

    def get_code(self) -> str:
        return self.totp.now()

    def max_attempts(self):
        return 2


if __name__ == '__main__':
    provider = AutoTOTPMFAuthCodeProvider(os.environ['UEC_MFA_SECRET'])
    code = provider.get_code()
    print(code)
