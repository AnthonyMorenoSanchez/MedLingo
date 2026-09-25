from pydantic import BaseModel


class Response(BaseModel):
    model_config = {"extra": "allow"}
