from dataclasses import dataclass, field
from typing import List


@dataclass(kw_only=True)
class AccountTitle:
    name: str
    code: str
    old_code: str = None
    seq: str = None

    parent: 'AccountTitle' = None
    children: List['AccountTitle'] = field(default_factory=list)

    def __post_init__(self):
        for child in self.children:
            child.parent = self

    def get(self, path: str = None) -> 'AccountTitle':
        for node in self.traverse():
            if node.path == path:
                return node

        return None

    def traverse(self):
        yield self
        for child in self.children:
            yield from child.traverse()

    @property
    def path(self) -> str:
        if self.parent and self.parent.code.isnumeric():
            return self.parent.path + '/' + self.name
        else:
            return self.name
