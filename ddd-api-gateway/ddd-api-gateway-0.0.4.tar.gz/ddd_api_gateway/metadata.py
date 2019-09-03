# -*- coding: utf-8 -*-
"""Domain Driven Design framework."""
from ddd_base import ValueObject


class Metadata(ValueObject):

    def __init__(self, author, email, repository, description):
        super(Metadata, self).__init__()
        self.author = author
        self.email = email
        self.repository = repository
        self.description = description

    def __eq__(self, other):
        if not isinstance(other, Metadata):
            return NotImplemented

        return self.author == other.author \
            and self.email == other.email \
            and self.repository == other.repository \
            and self.description == other.description
