import os.path
import urllib.parse
from http.cookiejar import LWPCookieJar
from pprint import pprint
import requests
import bs4
from .mfa import PromptingMFAuthCodeProvider, MFAuthCodeProvider
from .password import PasswordProvider, PromptingPasswordProvider
from .util import create_form_data, debug_response


class ShibbolethAuthenticator():
    def __init__(self,
                 shibboleth_host: str,
                 lwpcookiejar_path: str = 'cookies.lwp',
                 password_provider: PasswordProvider = None,
                 mfa_code_provider: MFAuthCodeProvider = None,
                 max_attempts: int = 3,
                 debug: bool = False,
                 ) -> None:
        self._password_provider = password_provider or PromptingPasswordProvider()
        self._mfa_code_provider = mfa_code_provider or PromptingMFAuthCodeProvider()
        self._shibboleth_host = shibboleth_host
        self._max_attempts = max_attempts

        # setup session
        self._session = requests.Session()

        # setup cookiejar
        self._lwp = LWPCookieJar(filename=lwpcookiejar_path)
        self._session.cookies = self._lwp
        if os.path.exists(lwpcookiejar_path):
            self._lwp.load(ignore_discard=True, ignore_expires=True)

        self.debug = debug

    def get_cookies(self) -> LWPCookieJar:
        return self._lwp

    def login(self, original_url: str) -> requests.Response:
        # Start
        res = self._session.get(original_url)
        self.debug and debug_response(res)
        if urllib.parse.urlparse(res.url).hostname != self._shibboleth_host:
            # already logged in
            return res

        # Continue
        res = self._do_continue_flow(res)

        # Login
        res = self._do_login_flow(res)

        # MFAuth
        res = self._do_mfauth_flow(res)

        # Continue
        res = self._do_continue_flow(res)

        # save cookies
        self._lwp.save(ignore_discard=True, ignore_expires=True)

        return res

    def _do_login(self, method, url, data):
        assert(method.lower() == 'post')
        username, password = self._password_provider.get()
        data.update({
            'j_username': username,
            'j_password': password,
            '_eventId_proceed': '',
        })
        res = self._session.post(url, data=data)
        return res

    def _do_login_flow(self, res: requests.Response):
        for _ in range(self._max_attempts):
            self.debug and input('login [Enter]')

            # assert
            doc = bs4.BeautifulSoup(res.text, 'html.parser')
            assert(doc.select_one('input[name=j_username]') != None)
            assert(doc.select_one('input[name=j_password]') != None)

            # do login
            method, url, data = create_form_data(res.text)
            url = urllib.parse.urljoin(res.url, url)
            res = self._do_login(method, url, data)
            self.debug and debug_response(res)

            # check error
            doc = bs4.BeautifulSoup(res.text, 'html.parser')
            error = doc.select_one('.form-error')
            if error:
                print(f'Failed to login: {error.text}')
            else:
                break
        return res

    def _do_mfauth(self, method, url, _data):
        assert(method.lower() == 'post')
        mfa_code = self._mfa_code_provider.get_code()
        data = {
            'csrf_token': _data['csrf_token'],
            'authcode': mfa_code,
            'login': 'login',
            'mfa_type': 'totp'
        }
        res = self._session.post(url, data=data)
        return res

    def _do_mfauth_flow(self, res: requests.Response):
        self.debug and input('mfauth [Enter]')
        method, url, _data = create_form_data(res.text)
        url = urllib.parse.urljoin(res.url, url)
        if '/mfa/MFAuth.php' in url:
            for _ in range(self._max_attempts):
                # assert
                doc = bs4.BeautifulSoup(res.text, 'html.parser')
                assert(doc.select_one('form[name=MFALogin]') != None)

                # do mfauth
                res = self._do_mfauth(method, url, _data)
                self.debug and debug_response(res)

                # check error
                doc = bs4.BeautifulSoup(res.text, 'html.parser')
                error = doc.select_one('.input_error_for_user')
                if error:
                    print(f'Failed to login: {error.text}')
                else:
                    break
        return res

    def _do_continue(self, method, url, data):
        assert(method.lower() == 'post')
        res = self._session.post(url, data=data)
        return res

    def _do_continue_flow(self, res: requests.Response):
        self.debug and input('do [Enter] continue')

        # assert
        doc = bs4.BeautifulSoup(res.text, 'html.parser')
        need_continue = doc.select_one('noscript input[type=submit][value=Continue]') != None

        # continue
        if need_continue:
            method, url, data = create_form_data(res.text)
            url = urllib.parse.urljoin(res.url, url)
            res = self._do_continue(method, url, data)
            self.debug and debug_response(res)
        return res
