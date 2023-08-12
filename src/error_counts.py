from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from src.config import KEY
from src.error_counts_query import ErrorCountsQuery
from pandas import DataFrame

class ErrorCounts:

  def __init__(self, delay_days=5):
    scope = "https://www.googleapis.com/auth/playdeveloperreporting"
    creds = ServiceAccountCredentials.from_json_keyfile_name(KEY, [scope])
    service = build('playdeveloperreporting', 'v1beta1', credentials=creds)
    self.errors = service.vitals().errors().counts()
    self.delay_days = delay_days

  def query(self, app, metric="distinctUsers"):
    """
      Return the list of dates and values of distinct users who experienced errors
      or specify some other metric optionally.
    """
    freshness = self.errors.get(name=f"apps/{app}/errorCountMetricSet").execute()
    # Create the query for last 3 days
    query = ErrorCountsQuery(freshness, self.delay_days)
    body = query.get_body([metric], ["reportType"])
    counts = self.errors.query(name=f"apps/{app}/errorCountMetricSet", body=body).execute()

    if 'rows' not in counts:
      return []
    
    # Returns DataFrame of tuples(date, value)
    return DataFrame([
      (
        f"{r['startTime']['year']}-{r['startTime']['month']:02}-{r['startTime']['day']:02}",
        float(r['metrics'][0]['decimalValue']['value'])
      ) for r in counts['rows']
    ], columns=["Date", metric])
