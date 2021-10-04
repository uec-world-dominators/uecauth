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
    debug=False,
)

res = sa.login(campusweb_url)
print(res.url)
