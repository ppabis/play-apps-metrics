from io import StringIO
from datetime import datetime, timedelta
from google.cloud import storage
import pandas
from config import KEY

class InstallReports:
  def __init__(self, uri, delay_days):    
    self.month = (datetime.now() - timedelta(days=delay_days)).strftime("%Y%m")
    bucket = uri.split("/")[2]
    storageClient = storage.Client.from_service_account_json(KEY)
    self.bucket = storageClient.get_bucket(bucket)

  def get_statistics(self, app):
    item = f"stats/installs/installs_{app}_{self.month}_overview.csv"
    blob = self.bucket.blob(item)
    statistics = blob.download_as_string().decode('utf-16')
    df = pandas.read_csv(StringIO(statistics), sep=",")
    return df[["Date", "Total User Installs", "Update events", "Uninstall events"]]

