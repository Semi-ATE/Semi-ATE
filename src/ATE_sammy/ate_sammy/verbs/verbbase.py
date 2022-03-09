from abc import ABC, abstractmethod


class VerbBase(ABC):
    @abstractmethod
    def run(self, cwd: str, arglist) -> int:
        # Note: arglist is an ad-hoc object created by
        # argparse which has no real type, hence the missing
        # annotation. All we know is, that it will have the
        # members "verb" and "noun".
        pass
