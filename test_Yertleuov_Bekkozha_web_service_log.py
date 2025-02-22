import unittest
from unittest.mock import patch
from flask import Flask
from task_Yertleuov_Bekkozha_web_service_log import app

class TestWebService(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_search_success(self):
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.text = '<div class="results-info">About 40,373 results</div>'
            response = self.app.get('/api/search?query=test')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"version": 1.0, "article_count": 40373})

    def test_search_no_results(self):
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.text = '<div class="results-info">0 results</div>'
            response = self.app.get('/api/search?query=nonexistentquery')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"version": 1.0, "article_count": 0})

    def test_search_wikipedia_unavailable(self):
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError()
            response = self.app.get('/api/search?query=test')
            self.assertEqual(response.status_code, 503)
            self.assertEqual(response.data.decode(), "Wikipedia Search Engine is unavailable")

    def test_non_existent_route(self):
        response = self.app.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data.decode(), "This route is not found")

if __name__ == '__main__':
    unittest.main()
