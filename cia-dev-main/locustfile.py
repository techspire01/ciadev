from locust import HttpUser, task, between
import random

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    @task(3)
    def index(self):
        """Test the home page"""
        self.client.get("/")
    
    @task(2)
    def about(self):
        """Test about page if it exists"""
        self.client.get("/about/", catch_response=True)
    
    @task(2)
    def contact(self):
        """Test contact page if it exists"""
        self.client.get("/contact/", catch_response=True)
    
    @task(1)
    def random_page(self):
        """Test random endpoints"""
        pages = ["/", "/admin/", "/accounts/login/"]
        self.client.get(random.choice(pages), catch_response=True)
