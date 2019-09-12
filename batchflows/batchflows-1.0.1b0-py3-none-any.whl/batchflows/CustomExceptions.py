import logging
import traceback


class ParallelFlowsException(Exception):
    def __init__(self, flow_name, exceptions):
        super().__init__(f'an unexpected exception occur in flow: {flow_name}')

        logging.error(f"##### unexpected error in flow: {flow_name} ####")
        for error in exceptions:
            logging.error(f"##### unexpected error in step: {error['name']} ####")
            traceback.print_tb(error['trace'])
