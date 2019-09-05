#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from clogger import CustomLogger

if __name__ == '__main__':

    logger = CustomLogger(
        handler_name="MyCustomLogger",
        stream_handler=True,
        file_handler=True,
        filenames="default.log",
        level="INFO",
        capture_syserror=True,
    )

    logger.starting_message()

    logger.debug("Debug test")
    logger.info("Info test")
    logger.warning("Warning test")
    logger.error("Error test")

    try:
        1 + 'a'
    except Exception as e:
        logger.exception("Exception test (exception follows)")


    logger.info("Going to do something else...")

    pppo

    logger.exiting_message()