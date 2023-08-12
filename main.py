from src.error_counts import ErrorCounts
from src.install_reports import InstallReports
from src.config import APPS, BUCKET_URI
from pandas import DataFrame
from prometheus_client import Gauge, start_http_server
from threading import Thread
from time import sleep
import prometheus_client

counters: dict[str, Gauge] = {}

def set_counters(app, metric, value):
  fix_metric = metric.replace(" ", "_").lower()
  if fix_metric not in counters:
    counters[fix_metric] = Gauge(f"{fix_metric}", f"{metric}", ["app"])
  counters[fix_metric].labels(app).set(value)

def main():
  # "Clients"
  delay = 3 # Controls how many days back to query because one data can be older than the other
  installReports = InstallReports(BUCKET_URI, delay)
  errorCounts = ErrorCounts(delay)

  for app in APPS:
    print(f"App: {app}")
    reports = installReports.get_statistics(app)
    counts = errorCounts.query(app)
    if len(counts) == 0:
      print("No error counts")
      # Create copy of reports dates with all distinctUsers values set to 0
      counts = DataFrame([(r, 0.0) for r in reports["Date"]], columns=["Date", "distinctUsers"])
    # Merge the two dataframes
    merged = reports.merge(counts, on="Date", how="inner")
    print(merged)

    # Select the latest record
    latest = merged.iloc[-1]
    for metric in latest.index:
      if metric != "Date":
        set_counters(app, metric, latest[metric])

def main_thread():
  while True:
    main()
    print("Sleeping for 1 hour")
    sleep(60 * 60)
    
if __name__ == "__main__":
  prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
  prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
  prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)
  Thread(target=main_thread).start() # Create second counters
  start_http_server(9300)
