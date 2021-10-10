import os.path
import urllib.parse
import logging
from http.cookiejar import CookieJar, LWPCookieJar
import requests
import bs4

from uecauth.errors import MaximumAttemptsExceededError, OldRequestError
from .mfa import PromptingMFAuthCodeProvider, MFAuthCodeProvider
from .password import PasswordProvider, PromptingPasswordProvider
from .util import create_form_data, debug_response
from . import info


class ShibbolethAuthenticator():
    def __init__(self,
                 shibboleth_host: str,
                 lwpcookiejar_path: str = 'cookies.lwp',
                 password_provider: PasswordProvider = None,
                 mfa_code_provider: MFAuthCodeProvider = None,
                 max_attempts: int = 3,
                 debug: bool = False,
                 logger: logging.Logger = None,
                 ) -> None:
        self._password_provider = password_provider or PromptingPasswordProvider()
        self._mfa_code_provider = mfa_code_provider or PromptingMFAuthCodeProvider()
        self._shibboleth_host = shibboleth_host
        self._max_attempts = max_attempts
        self._lwpcookiejar_path = lwpcookiejar_path
        self.debug = debug
        self.logger = logger or logging.getLogger(info.name)
        self._session = None

    def _create_session(self, cookiejar: CookieJar = None):
        # setup session
        session = requests.Session()

        # setup cookiejar
        session.cookies = self._load_cookies()
        if cookiejar:
            for cookie in cookiejar:
                session.cookies.set_cookie(cookie)

        return session

    def _load_cookies(self) -> LWPCookieJar:
        cookies = LWPCookieJar(filename=self._lwpcookiejar_path)
        if os.path.exists(self._lwpcookiejar_path):
            cookies.load(ignore_discard=True, ignore_expires=True)
        return cookies

    def get_cookies(self) -> LWPCookieJar:
        '''
        認証情報の取得
        '''

        if self._session:
            return self._session.cookies
        else:
            return self._load_cookies()

    def continue_login(self,
                       res: requests.Response,
                       session: requests.Session = None,
                       session_cookies: CookieJar = None,
                       ) -> requests.Response:
        '''
        既に送ったリクエストのリダイレクト先がshibbolethのとき、続けてログインする

        ```py
        session = requests.Session()
        response = session.get(<target_url>)

        if 'shibboleth' in response.url:
            response = shibboleth.continue_login(response, session)
        ```
        '''

        assert self.is_shibboleth(res.url), f'Response URLのホストは{self._shibboleth_host}である必要があります'
        assert session or session_cookies, 'SessionまたはSession Cookieを指定する必要があります'

        # renew session with cookies
        self._session = session or self._create_session(cookiejar=session_cookies)

        return self._do_login_flow(res)

    def login(self, target_url: str) -> requests.Response:
        '''
        target_urlに新たにログインする

        ```py
        response = shibboleth.login(<target_url>)
        ```
        '''

        # setup session
        self._session = self._create_session()

        # Start
        res = self._session.get(target_url)
        if self.is_shibboleth(res.url):
            return self.continue_login(res, session=self._session)
        else:
            # already logged in
            self.logger.info('既にログイン済みです')
            return res

    def _do_login_flow(self, res: requests.Response):
        self.logger.info('Shibbolethにログインします')

        # Continue
        res = self._do_continue_flow(res)

        # Login
        res = self._do_password_auth_flow(res)

        # MFAuth
        res = self._do_mfauth_flow(res)

        # Continue
        res = self._do_continue_flow(res)

        # save cookies
        self._session.cookies.save(ignore_discard=True, ignore_expires=True)

        return res

    def _do_password_auth(self, method, url, data):
        assert method.lower() == 'post'
        username, password = self._password_provider.get()
        data.update({
            'j_username': username,
            'j_password': password,
            '_eventId_proceed': '',
        })
        res = self._session.post(url, data=data)
        return res

    def _do_password_auth_flow(self, res: requests.Response):
        for _ in range(self._password_provider.max_attempts()):
            self.debug and input('login [Enter]')
            self.logger.info('パスワード認証を行います')

            # assert
            doc = bs4.BeautifulSoup(res.text, 'html.parser')
            assert doc.select_one('input[name=j_username]') != None
            assert doc.select_one('input[name=j_password]') != None

            # do login
            method, url, data = create_form_data(res.text)
            url = urllib.parse.urljoin(res.url, url)
            res = self._do_password_auth(method, url, data)
            self.debug and debug_response(res)

            # check error
            doc = bs4.BeautifulSoup(res.text, 'html.parser')
            error = doc.select_one('.form-error')
            if error:
                self.logger.error(f'ログインに失敗しました: {error.text}')
            else:
                break
        else:
            self.logger.fatal('最大試行回数を超えました')
            raise MaximumAttemptsExceededError()
        return res

    def _do_mfauth(self, method, url, _data):
        assert method.lower() == 'post'
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
            for _ in range(self._mfa_code_provider.max_attempts()):
                self.logger.info('二段階認証を行います')

                # assert
                doc = bs4.BeautifulSoup(res.text, 'html.parser')
                assert doc.select_one('form[name=MFALogin]') != None

                # do mfauth
                res = self._do_mfauth(method, url, _data)
                self.debug and debug_response(res)

                # check error
                doc = bs4.BeautifulSoup(res.text, 'html.parser')
                error = doc.select_one('.input_error_for_user')
                if error:
                    self.logger.error(f'二段階認証に失敗しました: {error.text}')
                else:
                    break
            else:
                self.logger.fatal('最大試行回数を超えました')
                raise MaximumAttemptsExceededError()
        return res

    def _do_continue(self, method, url, data):
        assert method.lower() == 'post'
        res = self._session.post(url, data=data)
        return res

    def _do_continue_flow(self, res: requests.Response):
        self.debug and input('continue [Enter]')

        # assert
        doc = bs4.BeautifulSoup(res.text, 'html.parser')
        need_continue = doc.select_one('noscript input[type=submit][value=Continue]') != None

        # continue
        if need_continue:
            self.logger.info('Continueします')

            method, url, data = create_form_data(res.text)
            url = urllib.parse.urljoin(res.url, url)
            res = self._do_continue(method, url, data)

            # assert
            doc = bs4.BeautifulSoup(res.text, 'html.parser')
            if '過去のリクエスト' in doc.select_one('title').text:
                self.logger.fatal('失敗しました: 過去のリクエスト')
                raise OldRequestError()

            self.debug and debug_response(res)
        return res

    def is_shibboleth(self, url: str) -> bool:
        return urllib.parse.urlparse(url).hostname == self._shibboleth_host

    def __del__(self):
        if self._session:
            self._session.close()

    def is_logged_in(self, url: str) -> bool:
        res = requests.head(url,
                            cookies=self.get_cookies(),
                            allow_redirects=False)
        return not (res.status_code // 100 == 3 and
                    self.is_shibboleth(res.headers['Location']))
