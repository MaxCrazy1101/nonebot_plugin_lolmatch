from pydantic import BaseModel, field_validator


class Config(BaseModel):
    lolmatch_command_priority: int = 10
    lolmatch_plugin_enabled: bool = True

    @field_validator("lolmatch_command_priority")
    @classmethod
    def check_priority(cls, v: int) -> int:
        if v >= 1:
            return v
        raise ValueError("lolmatch command priority must greater than 1")
