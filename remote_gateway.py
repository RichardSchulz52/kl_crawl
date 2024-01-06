import time
from http.client import HTTPResponse

class RemoteGateway:

    CRAWL_SLEEP_TIME = 5
    CACHE_CRAWL_SLEEP_TIME = 1
    RETRY_SLEEP_TIME = (5 * 60) + 5

    def __init__(self, retryable_errors, accepted_errors) -> None:
        self.retryable_errors = retryable_errors
        self.accepted_errors = accepted_errors

    def call(self, remote_call):
        try:
            return remote_call()
        except Exception as e:
            if type(e) in self.retryable_errors:
                print(f"Retryable error {type(e)} sleeping for {RemoteGateway.RETRY_SLEEP_TIME}")
                time.sleep(RemoteGateway.RETRY_SLEEP_TIME)
            elif type(e) in self.accepted_errors:
                print(f"accepted error {type(e)}")
                return
            else:
                print(f"Unexpected error {type(e)} in {remote_call.__name__}")
    
    def crawl_call(self, remote_call):
        return_value = self.call(remote_call)
        if type(return_value) == HTTPResponse:
            sleep_time = RemoteGateway.CACHE_CRAWL_SLEEP_TIME
        else:
            sleep_time = RemoteGateway.CRAWL_SLEEP_TIME
        print(f"sleep for {sleep_time} after crawl call")
        time.sleep(sleep_time)
        return return_value
