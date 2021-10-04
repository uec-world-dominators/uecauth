import os
import pyotp


class MFAuthCodeProvider():
    def get_code(self) -> str:
        pass


class PromptingMFAuthCodeProvider(MFAuthCodeProvider):
    def get_code(self):
        mfa_code = input('二段階認証コードを入力してください> ').strip()
        return mfa_code


class AutoTOTPMFAuthCodeProvider(MFAuthCodeProvider):
    def __init__(self, priv_key) -> None:
        self.totp = pyotp.TOTP(priv_key)

    def get_code(self) -> str:
        return self.totp.now()


if __name__ == '__main__':
    provider = AutoTOTPMFAuthCodeProvider(os.environ['UEC_MFA_SECRET'])
    code = provider.get_code()
    print(code)
