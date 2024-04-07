# main.py

from fastapi import FastAPI, HTTPException, Depends, Header
from celery import Celery
import requests

app = FastAPI()

# API key for authentication
API_KEY = "YuacJzUvzblJuPi7Uk9cVA"

# Celery configuration
celery = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

# Define Celery task for scraping
@celery.task
def scrape_search_results(api_key: str, url: str, name: str, organization: str, page: int = 1) -> list:
    results = []
    for i in range(page, page + 5): 
        params = {"page": i, "api_key": api_key, "name": name, "organization": organization}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            results.append(response.json())  # Assuming response is JSON
        else:
            raise HTTPException(status_code=response.status_code, detail="Error scraping data")
    return results

def verify_api_key(api_key: str = Header(...)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

# Endpoint to initiate scraping
@app.post("/scrape/")
def initiate_scraping(request_data: dict, api_key: str = Header(...)) -> dict:
    name = request_data.get('name')
    organization = request_data.get('organization')

    if name is None and organization is None:
        raise HTTPException(status_code=400, detail="Name or organization must be provided in the request body")

    if name:
        organization = None  # Reset organization if name is provided
        url = "https://api.apollo.io/v1/mixed_people/search"
    elif organization:
        name = None  # Reset name if organization is provided
        url = "https://api.apollo.io/api/v1/mixed_companies/search"
    else:
        raise HTTPException(status_code=400, detail="Invalid request. Either name or organization must be provided.")

    task = scrape_search_results.delay(api_key, url, name, organization)
    return {"job_id": task.id}




# Endpoint to check status and retrieve results
@app.get("/scrape_results/")
def get_scraping_results(job_id: str, api_key: str = Header(..., convert_underscores=False)) -> dict:
    # Verify API key here if needed using the verify_api_key function

    task_result = scrape_search_results.AsyncResult(job_id)

    if task_result.state == 'SUCCESS':
        scraped_results = task_result.get()  # Retrieve the scraped results
        return {"status": "finished", "results": scraped_results}
    elif task_result.state == 'PENDING':
        return {"status": "pending"}
    elif task_result.state == 'FAILURE':
        return {"status": "failed"}
    else:
        raise HTTPException(status_code=404, detail="Job ID not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
