from abc import ABC, abstractmethod


class ChatProviderBase(ABC):
    def __init__(self,model):self.model=model
    @abstractmethod
    async def chat(self,messages):raise NotImplementedError
