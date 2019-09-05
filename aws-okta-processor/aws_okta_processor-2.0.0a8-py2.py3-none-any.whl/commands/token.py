from .base import Base

from . import token_operations


class Token(Base):
    """
    Usage:
      token <operation> <args> ...
    """

    def execute(self):
        operation_name = self.options.pop('<operation>').capitalize()
        operation_args = self.options.pop('<args>')

        if operation_args is None:
            operation_args = {}

        try:
            operation_class = getattr(token_operations, operation_name)
            operation = operation_class(operation_args)
            operation.execute()
        except AttributeError:
            exit((
                "aws-okta-processor: error: "
                "argument operation: Invalid choice"
            ))
