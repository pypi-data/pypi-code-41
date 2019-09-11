import re
from typing import List

from sidecar.services.deployment_outputs_service import InputValueResolver


class InputValueResolverService:
    pattern = r'\$\{([\w\d_.-]+)\}'

    def __init__(self, resolvers: List[InputValueResolver]):
        self._resolvers = resolvers

    def resolve(self, value: str):
        resolved_tokens = {}
        for match in re.finditer(self.pattern, value):
            match_token = match.group()
            if match_token in resolved_tokens:
                continue
            match_value = match.group(1)
            resolver = self.find_resolver(match_value)
            resolved_tokens[match_token] = resolver.resolve(match_value)
            if resolved_tokens:
                for k, v in resolved_tokens.items():
                    value = value.replace(k, v)

        if value.startswith('$'):
            value = value[1:]
            resolver = self.find_resolver(value)
            return resolver.resolve(value)
        return value

    def find_resolver(self, value):
        resolver = next((r for r in self._resolvers if r.can_resolve(value)), None)
        if not resolver:
            raise Exception(f'no input resolver found for {value}')
        return resolver
