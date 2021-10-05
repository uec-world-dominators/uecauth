import sys
import os.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from uecauth.mfa import AutoTOTPMFAuthCodeProvider
from uecauth.password import DefaultPasswordProvider
from uecauth.shibboleth import ShibbolethAuthenticator
from uecauth.logger import get_logger
import unittest
import os
import bs4

logger = get_logger()

class Test(unittest.TestCase):
    def test_uec_library(self):
        url = 'https://www.lib.uec.ac.jp/opac/user/top'

        shibboleth_host = 'shibboleth.cc.uec.ac.jp'

        shibboleth = ShibbolethAuthenticator(
            shibboleth_host=shibboleth_host,
            mfa_code_provider=AutoTOTPMFAuthCodeProvider(os.environ['UEC_MFA_SECRET']),
            password_provider=DefaultPasswordProvider(
                os.environ['UEC_USERNAME'],
                os.environ['UEC_PASSWORD']
            ),
            debug=False,
            logger=logger,
        )

        res = shibboleth.login(url)
        logger.info(res.url)

        return self.assertTrue(res.url == url)

    def test_uec_campusweb(self):
        url = 'https://campusweb.office.uec.ac.jp/campusweb/ssologin.do'
        shibboleth_host = 'shibboleth.cc.uec.ac.jp'

        shibboleth = ShibbolethAuthenticator(
            shibboleth_host=shibboleth_host,
            mfa_code_provider=AutoTOTPMFAuthCodeProvider(os.environ['UEC_MFA_SECRET']),
            password_provider=DefaultPasswordProvider(
                os.environ['UEC_USERNAME'],
                os.environ['UEC_PASSWORD']
            ),
            debug=False,
            logger=logger,
        )

        res = shibboleth.login(url)
        logger.info(res.url)

        campusweb_url = 'https://campusweb.office.uec.ac.jp/campusweb/campussquare.do'
        return self.assertTrue(res.url.startswith(campusweb_url))

if __name__ == '__main__':
    unittest.main()
