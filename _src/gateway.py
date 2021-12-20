import datetime
import logging
import os
import requests


logging.basicConfig(
    level=logging.WARNING,
    format='"%(asctime).19s", "%(levelname)s", "%(message)s"'
)

log = logging.getLogger(__name__)


class HTTPGateway:
    def __init__(self, username=None, password=None, cache_expiry_days=30, cache_directory='.'):
        self.username = username
        self.password = password
        self.cache_expiry_days = cache_expiry_days
        self.cache_directory = cache_directory

    @staticmethod
    def _get_cache_name_from_url(url):
        return url.replace('/', '-').replace(':', '-')

    def _fetch_from_url(self, url):
        log.info('Will fetch from internet: {url}')
        connection = requests.get(url, auth=(self.username, self.password))

        if connection.status_code != 200:
            log.error(f'Cannot fetch from URL: {url}')
            raise ConnectionError
        else:
            log.debug(f'Fetched from {url}')
            return connection.text

    def _fetch_from_cache(self, url):
        cache_name = self._get_cache_name_from_url(url)
        path = os.path.join(self.cache_directory, cache_name)

        with open(path) as file:
            log.info(f'Reading from cache file {path}')
            return file.read()

    def _set_cache(self, url, data):
        cache_name = self._get_cache_name_from_url(url)
        path = os.path.join(self.cache_directory, cache_name)

        with open(path, 'w') as file:
            log.debug(f'Writing to cache file {path}')
            file.write(data)

    def _cache_invalid(self, url):
        def last_modified_less_than_month_ago(path):
            modification_timestamp = os.path.getmtime(path)
            modification_datetime = datetime.datetime.fromtimestamp(modification_timestamp)
            now = datetime.datetime.now()
            return (now - modification_datetime).days < self.cache_expiry_days

        cache_name = self._get_cache_name_from_url(url)
        path = os.path.join(self.cache_directory, cache_name)

        if os.path.isfile(path) and last_modified_less_than_month_ago(path):
            return False
        else:
            return True

    def get(self, url):
        if self._cache_invalid(url):
            log.info(f'Will read from URL {url}')
            data = self._fetch_from_url(url)
            self._set_cache(url, data)
        else:
            log.info(f'Will read from cache')
            data = self._fetch_from_cache(url)

        return data
