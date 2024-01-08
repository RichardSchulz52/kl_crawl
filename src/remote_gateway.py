import time
from http.client import HTTPResponse

class RemoteGateway:

    CRAWL_SLEEP_TIME = 3
    CACHE_CRAWL_SLEEP_TIME = 1
    RETRY_SLEEP_TIME = 30

    NUMBER_OF_RETRIES = 3

    def __init__(self, retryable_errors, accepted_errors, error_handlers) -> None:
        self.retryable_errors = retryable_errors
        self.accepted_errors = accepted_errors
        self.error_handlers = error_handlers

    def call(self, remote_call):
        retries = RemoteGateway.NUMBER_OF_RETRIES
        retry_possible = True
        while retries > 0 and retry_possible:
            retry_possible = False
            try:
                return remote_call()
            except Exception as e:
                if type(e) in self.retryable_errors:
                    retries -= 1
                    retry_possible = True
                    print(f"Retryable error {type(e)} sleeping for {RemoteGateway.RETRY_SLEEP_TIME}")
                    time.sleep(RemoteGateway.RETRY_SLEEP_TIME)
                elif type(e) in self.accepted_errors:
                    print(f"accepted error {type(e)}")
                    return
                elif type(e) in [error_func_tuple[0] for error_func_tuple in self.error_handlers]:
                    handler_func = [error_func_tuple for error_func_tuple in self.error_handlers if error_func_tuple[0] == type(0)][1]
                    handler_func()
                else:
                    print(f"Unexpected error {type(e)}")
        
    
    def crawl_call(self, remote_call):
        return_value = self.call(remote_call)
        if type(return_value) == HTTPResponse:
            sleep_time = RemoteGateway.CACHE_CRAWL_SLEEP_TIME
        else:
            sleep_time = RemoteGateway.CRAWL_SLEEP_TIME
        print(f"sleep for {sleep_time} after crawl call")
        time.sleep(sleep_time)
        return return_value
