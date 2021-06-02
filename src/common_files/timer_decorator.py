from time import time
from typing import Callable, Any
from functools import wraps
from math import factorial
from random import randint


def timed(iterations: int = 1) -> Callable:
	def timed_inner(func: Callable) -> Callable:
		@wraps(func)
		def wrapper(*args: Any, **kwargs: Any) -> str:
			T1 = time()

			for i in range(iterations):
				func(*args, **kwargs)

			Elapsed = time() - T1

			return f'Over {iterations} iterations, function "{func.__name__}" took an average time of ' \
			       f'{(Elapsed / iterations):.2f} seconds to complete its operations'

		return wrapper
	return timed_inner


@timed(5)
def DecoratorTest() -> None:
	factorial(int(randint(0, 100_000) * randint(0, 100_000) / randint(500, 100_000)))
