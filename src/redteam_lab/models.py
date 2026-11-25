from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

Category = Literal["confidentiality", "instruction_boundary", "utility"]

class Case(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str = Field(min_length=1)
    category: Category
    prompt: str = Field(min_length=1)
    expected: tuple[str,...] = ()
    forbidden: tuple[str,...] = ()

    @model_validator(mode="after")
    def check_rules(self):
        if not self.expected and not self.forbidden:
            raise ValueError("Missing checks")
        if any(not s.strip() for s in (*self.expected,*self.forbidden)):
            raise ValueError("Empty check")
        return self

class Result(BaseModel):
    case_id: str
    category: Category
    status: Literal["pass","fail","error"]
    latency_ms: float = Field(ge=0)
    missing: list[str] = Field(default_factory=list)
    violations: list[str] = Field(default_factory=list)
    error: str | None = None
