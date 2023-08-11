from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from config import KEY
from error_counts_query import ErrorCountsQuery

class ErrorCounts:

  def __init__(self):
    scope = "https://www.googleapis.com/auth/playdeveloperreporting"
    creds = ServiceAccountCredentials.from_json_keyfile_name(KEY, [scope])
    service = build('playdeveloperreporting', 'v1beta1', credentials=creds)
    self.errors = service.vitals().errors().counts()

  def query(self, app):
    freshness = self.errors.get(name=f"apps/{app}/errorCountMetricSet").execute()
    # Create the query for last 3 days
    query = ErrorCountsQuery(freshness, 3)
    body = query.get_body(["distinctUsers"], ["errorType"])
    counts = self.errors.query(name=f"apps/{app}/errorCountMetricSet", body=body).execute()

    return counts['rows'] if 'rows' in counts else []
