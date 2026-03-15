import sys
from networksecurity.logging.logger import logging


class NetworkSecurityException(Exception):

    def __init__(self, message, error_details: sys):
        super().__init__(message)

        _, _, exc_tb = error_details.exc_info()

        self.error_message = message
        self.lineno = exc_tb.tb_lineno
        self.filename = exc_tb.tb_frame.f_code.co_filename

    def __str__(self):
        return f"Error occurred in script [{self.filename}] at line number [{self.lineno}] error message [{self.error_message}]"


if __name__ == "__main__":

    try:
        logging.info("Enter try block")

        a = 1 / 0

        print("This will not be printed")

    except Exception as e:
        logging.error("An error occurred")

        raise NetworkSecurityException(e, sys)
