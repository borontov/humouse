from abc import ABC, abstractmethod


class Instruction(ABC):
    @staticmethod
    @abstractmethod
    def perform(human):
        pass
