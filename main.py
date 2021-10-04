import os
import http.cookiejar
import requests
from uecauth.shibboleth import ShibbolethAuthenticator
from uecauth.password import DefaultPasswordProvider
from uecauth.mfa import AutoTOTPMFAuthCodeProvider

url = 'https://campusweb.office.uec.ac.jp/campusweb/ssologin.do'
shibboleth_host = 'shibboleth.cc.uec.ac.jp'

shibboleth = ShibbolethAuthenticator(
    shibboleth_host=shibboleth_host,
    # mfa_code_provider=AutoTOTPMFAuthCodeProvider(os.environ['UEC_MFA_SECRET']),
    password_provider=DefaultPasswordProvider(
        os.environ['UEC_USERNAME'],
        os.environ['UEC_PASSWORD']
    ),
    debug=False,
)

res = shibboleth.login(url)
print(res.url)

# http.LWPCookieJar
cookies: http.cookiejar.LWPCookieJar = shibboleth.get_cookies()
