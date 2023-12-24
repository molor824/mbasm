from typing import Iterable, Generic, TypeVar, Callable

T = TypeVar('T')

class Peekable(Generic[T]):
    def __init__(self, iterable: Iterable[T]):
        self.iterator = iter(iterable)
        self.peeked = None
    def __iter__(self):
        return self
    def __next__(self) -> T:
        if self.peeked is not None:
            result = self.peeked
            self.peeked = None
            return result
        return next(self.iterator)
    def next_if(self, condition: Callable[[T], bool]) -> T:
        peeked = self.peek()
        if condition(peeked):
            next(self)
            return peeked
        raise StopIteration()
    def peek(self) -> T:
        if self.peeked is None:
            self.peeked = next(self.iterator)
        return self.peeked