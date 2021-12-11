from datacraft import logging_handler


def test_logging_handler():
    """ for coverage sake """
    logging_handler._configure_logging('debug')
    logging_handler._configure_logging('off')
