import unittest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestAPI(unittest.TestCase):

    def test_initiate_scraping(self):
        # Test /scrape/ endpoint with valid request containing both 'name' and 'organization'
        request_data = {"name": "ajay sharma", "organization": "google"}
        response = client.post("/scrape/", headers={"api_key": "YuacJzUvzblJuPi7Uk9cVA"}, json=request_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("job_id", response.json())

        # Test /scrape/ endpoint with valid request containing only 'name'
        request_data = {"name": "ajay sharma"}
        response = client.post("/scrape/", headers={"api_key": "YuacJzUvzblJuPi7Uk9cVA"}, json=request_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("job_id", response.json())

        # Test /scrape/ endpoint with valid request containing only 'organization'
        request_data = {"organization": "company"}
        response = client.post("/scrape/", headers={"api_key": "YuacJzUvzblJuPi7Uk9cVA"}, json=request_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("job_id", response.json())

        # Test /scrape/ endpoint with invalid request (missing parameters)
        response = client.post("/scrape/", headers={"api_key": "YuacJzUvzblJuPi7Uk9cVA"})
        self.assertEqual(response.status_code, 422)



    def test_get_scraping_results(self):
        # Test /scrape_results/ endpoint with valid job ID
        response = client.get("/scrape_results/?job_id=5078c903-0cf7-43ee-970b-7fd3cd419556", headers={"api_key": "YuacJzUvzblJuPi7Uk9cVA"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())
        
        # Test /scrape_results/ endpoint with invalid job ID
        response = client.get("/scrape_results/?job_id=5078c903-0cf7-43ee-970b-7fd3cd419557", headers={"api_key": "YuacJzUvzblJuPi7Uk9cVA"})
        self.assertEqual(response.status_code, 404)

        # Test /scrape_results/ endpoint with invalid API key
        response = client.get("/scrape_results/?job_id=mock_job_id", headers={"api_key": "YuacJzUvzblJuPi7Uk9cVr"})
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
