from pydantic import validator
from robusta.api import *

class MattermostSinkParams(SinkBaseParams):
    url: str
    token: str
    token_id: str
    channel: str

    @validator("url")
    def set_http_schema(cls, url):
        parsed_url = urlparse(url)
        # if netloc is empty string, the url was provided without schema
        if not parsed_url.netloc:
            raise AttributeError(f"{url} does not contain the schema!")
        return url