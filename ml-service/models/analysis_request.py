from pydantic import BaseModel


class AnalysisRequest(
    BaseModel
):

    idea: str