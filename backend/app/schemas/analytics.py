from pydantic import BaseModel


class AnalyticsSummaryResponse(BaseModel):
    total_orders: int
