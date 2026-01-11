"""
Load testing with Locust.

Run with:
    locust -f tests/performance/locustfile.py --headless -u 10 -r 2 -t 30s --host=http://localhost:8000
"""

from locust import HttpUser, task, between
import random


class PolicyBotUser(HttpUser):
    """Simulated user for load testing."""
    
    wait_time = between(1, 3)
    
    # Sample queries for testing
    general_queries = [
        "What is the capital of France?",
        "Who invented the telephone?",
        "What is 25 times 4?",
        "Tell me a joke",
    ]
    
    policy_queries = [
        "What is the leave policy?",
        "How many vacation days do I get?",
        "What is the remote work policy?",
        "What are the health benefits?",
        "What is the code of conduct?",
        "How do I request time off?",
        "What is the parental leave policy?",
        "How does the 401k match work?",
    ]
    
    def on_start(self):
        """Called when a simulated user starts."""
        self.session_id = None
    
    @task(5)
    def ask_policy_question(self):
        """Ask a policy-related question (most common)."""
        payload = {"query": random.choice(self.policy_queries)}
        if self.session_id:
            payload["session_id"] = self.session_id
        
        with self.client.post(
            "/ask",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("session_id")
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(2)
    def ask_general_question(self):
        """Ask a general question."""
        with self.client.post(
            "/ask",
            json={"query": random.choice(self.general_queries)},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def health_check(self):
        """Check health endpoint."""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    response.success()
                else:
                    response.failure("Health check returned unhealthy status")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def get_stats(self):
        """Get system stats."""
        with self.client.get("/stats", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def check_session(self):
        """Check session info if we have a session."""
        if self.session_id:
            with self.client.get(
                f"/session/{self.session_id}",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    response.success()
                elif response.status_code == 404:
                    # Session might have expired
                    self.session_id = None
                    response.success()
                else:
                    response.failure(f"Got status code {response.status_code}")
