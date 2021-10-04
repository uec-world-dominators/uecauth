# UEC Auth

電通大のshibboleth認証ライブラリ

## インストール

```sh
pip install uecauth
```

## 使い方

```py
import os
import http.cookiejar
import requests
from uecauth.shibboleth import ShibbolethAuthenticator
from uecauth.password import DefaultPasswordProvider
from uecauth.mfa import AutoTOTPMFAuthCodeProvider

campusweb_url = 'https://campusweb.office.uec.ac.jp/campusweb/ssologin.do'
shibboleth_host = 'shibboleth.cc.uec.ac.jp'

shibboleth = ShibbolethAuthenticator(
    original_url=campusweb_url,
    shibboleth_host=shibboleth_host,
    mfa_code_provider=AutoTOTPMFAuthCodeProvider(os.environ['UEC_MFA_SECRET']),
    password_provider=DefaultPasswordProvider(
        os.environ['UEC_USERNAME'],
        os.environ['UEC_PASSWORD']
    ),
    debug=False,
)

res = shibboleth.login(campusweb_url)
print(res.url)

# http.LWPCookieJar
cookies: http.cookiejar.LWPCookieJar = shibboleth.get_cookies()
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
|`DefaultPasswordProvider`|環境変数等から設定する|
|`PromptingPasswordProvider`|プロンプトから読み取る|

### 二段階認証コードの取得方法

|||
|---|---|
|`PromptingMFAuthCodeProvider`|プロンプトから読み取る|
|`AutoTOTPMFAuthCodeProvider`|秘密鍵を用いて自動生成する|

#### Socks5プロキシで二段階認証を回避する

```sh
ssh sol -D 1080 -N -f
export http_proxy=socks5://localhost:1080
export https_proxy=socks5://localhost:1080
```
