# download2.py - Download many URLs using multiple threads.
import os
import urllib.request
import workerpool

class DownloadJob(workerpool.Job):
    "Job for downloading a given URL."
    def __init__(self, url):
        self.url = url # The url we'll need to download when the job runs
    def run(self):
        save_to = os.path.basename(self.url.split(':')[-1].split('.')[0] + '.html')
        urllib.request.urlretrieve(self.url, save_to)

# Initialize a pool, 5 threads in this case
pool = workerpool.WorkerPool(size=5)

# Loop over urls.txt and create a job to download the URL on each line
for url in open("urls.txt"):
    job = DownloadJob(url.strip())
    pool.put(job)

# Send shutdown jobs to all threads, and wait until all the jobs have been completed
pool.shutdown()
pool.wait()