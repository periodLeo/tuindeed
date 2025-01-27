import os
import pandas as pd
from jobspy import scrape_jobs

def search_jobs(query: list) -> pd.DataFrame :

    jobs = scrape_jobs(
        site_name=["indeed"],
        search_term=query[0],
        location=query[2],
        results_wanted=query[4],
        hours_old=query[3],
        country_indeed=query[1],
    )

    return jobs

def save_to_csv(jobs_list: pd.DataFrame) -> str:
    """
    Save a dataframe of jobs in a csv file located in HOME/.local/share/tuindeed/jobs_list.csv

    Args :
        - jobs_list (DataFrame) : A list of jobs.
    Return :
        - (str) : path where the csv has been saved.
    """

    # path to local data on linux
    dir_name = "tuindeed"
    path = os.path.join(os.environ['HOME'], ".local/share", dir_name)
    desc_path = os.path.join(path, "jobs_descriptions")

    # makedirs works recursively, so if none exist, both directory will be created
    if not os.path.isdir(desc_path):
        os.makedirs(desc_path)

    for _, job in jobs_list.iterrows() :
        # save description as Markdown file using job id as name
        filename = job["id"] + ".md"
        file_path = os.path.join(desc_path, filename)
        with open(file_path, 'w') as f:
            f.write(job["description"])

    jobs_without_desc = jobs_list.drop(columns = ["description"])

    filename = os.path.join(path, "jobs_list.csv")
    jobs_without_desc.to_csv(filename, index=False)

    return filename

def load_csv() -> pd.DataFrame:
    filepath = os.path.join(os.environ["HOME"], ".local/share/tuindeed/jobs_list.csv")
    job_list = pd.DataFrame(columns = ["id","title","location"])
    if(os.path.isfile(filepath)):
        job_list = pd.read_csv(filepath).loc[:,["id","title","location"]]

    return job_list
