import urllib.request


class HtmlDownloader(object):
    def download(self, url):
        if url is None:
            return None

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) ''Chrome/51.0.2704.63 Safari/537.36'}
        request = urllib.request.Request(url=url, headers=headers)

        response = urllib.request.urlopen(request)

        if response.getcode() != 200:
            return None

        data = response.read()
        data = data.decode('utf-8')

        return data
