# UEC Auth

電通大のshibboleth認証ライブラリ

## インストール

```sh
pip install uecauth
```

## 使い方

```py
import os
from uecauth.shibboleth import ShibbolethAuthenticator
from uecauth.password import EnvironmentPasswordProvider
from uecauth.mfa import AutoTOTPMFAuthCodeProvider

campusweb_url = 'https://campusweb.office.uec.ac.jp/campusweb/ssologin.do'
shibboleth_host = 'shibboleth.cc.uec.ac.jp'

sa = ShibbolethAuthenticator(
    original_url=campusweb_url,
    shibboleth_host=shibboleth_host,
    mfa_code_provider=AutoTOTPMFAuthCodeProvider(os.environ['UEC_MFA_SECRET']),
    password_provider=EnvironmentPasswordProvider('UEC_USERNAME', 'UEC_PASSWORD'),
    debug=True,
)

res = sa.login(campusweb_url)
print(res.url)
```

### 環境変数

```sh
# UECアカウント
export UEC_USERNAME=""
export UEC_PASSWORD=""
# TOTPの秘密鍵
export UEC_MFA_SECRET=""
```

### ユーザ名、パスワードの取得方法

|||
|---|---|
|`EnvironmentPasswordProvider`|環境変数から読み取る|
|`PromptingPasswordProvider`|プロンプトから読み取る|

### 二段階認証コードの取得方法

|||
|---|---|
|`PromptingMFAuthCodeProvider`|プロンプトから読み取る|
|`AutoTOTPMFAuthCodeProvider`|秘密鍵を用いて自動生成する|

