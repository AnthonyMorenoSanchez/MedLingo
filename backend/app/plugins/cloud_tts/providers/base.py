from abc import ABC, abstractmethod


class TTSProviderBase(ABC):
    @abstractmethod
    async def synthesize(self,text,lang,voice):raise NotImplementedError
