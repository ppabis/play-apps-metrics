from datetime import datetime, timedelta

class ErrorCountsQuery:
  """
  A helper class to keep the function in ErrorCounts clean.
  """
  def __init__(self, freshness, days):
    """
    :param freshness: The freshnessInfo object from the error counts API
    """
    freshness = freshness["freshnessInfo"]["freshnesses"]
    # This will create a map of freshnesses by aggregation period
    freshness = {f['aggregationPeriod']: f for f in freshness}
    self.endTime = freshness["DAILY"]["latestEndTime"]
    # Construct date for the previous day
    self.lastDay = datetime(self.endTime['year'], self.endTime['month'], self.endTime['day'], self.endTime['hours'])
    self.prevDay = self.lastDay - timedelta(days=days)
    del self.endTime['hours']

  def get_body(self, metrics, dimensions):
    return {
      "metrics": metrics,
      "dimensions": dimensions,
      "timelineSpec": {
        "aggregationPeriod": "DAILY",
        "startTime": {
          "timeZone": self.endTime['timeZone'],
          "year": self.prevDay.year,
          "month": self.prevDay.month,
          "day": self.prevDay.day
        },
        "endTime": self.endTime
      }
    }