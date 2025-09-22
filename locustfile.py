import json
import time
from locust import HttpUser, task, between
from locust.exception import RescheduleTask

import random

class LLMUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Create unique user ID for this locust user
        self.user_id = f"load_test_user_{random.randint(1000, 9999)}"
        
        # Try health check but don't fail if it doesn't work immediately
        try:
            response = self.client.get("/health", timeout=5)
            if response.status_code == 200:
                print(f"User {self.user_id} started - Health check: {response.json()}")
            else:
                print(f"User {self.user_id} started - Health check failed: {response.status_code}")
        except Exception as e:
            print(f"User {self.user_id} started - Health check error: {e}")
    
    @task(3)  # Higher weight for short text generation
    def generate_short_text(self):
        payload = {
            "prompt": random.choice([
                "What is the capital of France?",
                "What is the capital of Germany?",
                "What is the capital of Italy?",
                "What is the capital of Spain?",
                "What is the capital of Portugal?",
                "What is the capital of Greece?",
                "What is the capital of Turkey?",
                "Hello, how are you?",
                "Tell me a joke",
                "What's the weather like?",
            ]),
            "max_tokens": random.randint(20, 50),
            "temperature": random.uniform(0.5, 1.0),
            "user_id": self.user_id,
        }
        with self.client.post("/generate", json=payload, catch_response=True, name="generate_short") as response:
            if response.status_code == 200:
                try:
                    result = response.json()
                    if "text" in result and result["text"]:
                        # Log metrics info
                        tokens_used = result.get("token_used", 0)
                        latency = result.get("latency", 0)
                        response.success()
                        print(f"Short text - User: {self.user_id}, Tokens: {tokens_used}, Latency: {latency:.3f}s")
                    else:
                        response.failure(f"Response missing text field: {response.text}")
                except json.JSONDecodeError as ex:
                    response.failure(f"Failed to decode JSON response: {response.text} - {ex}")
            else:
                response.failure(f"Failed to generate text: {response.status_code} - {response.text}")

    @task(1)  # Lower weight for long text generation
    def generate_long_text(self):
        payload = {
            "prompt": random.choice([
                "Write a detailed explanation about machine learning and artificial intelligence.",
                "Explain the history of computer science in detail.",
                "Describe the process of software development from start to finish.",
                "What are the benefits and challenges of cloud computing?",
                "Explain quantum computing and its potential applications.",
                "Tell me about the evolution of programming languages.",
            ]),
            "max_tokens": random.randint(100, 200),
            "temperature": random.uniform(0.3, 0.8),
            "user_id": self.user_id,
        }
        with self.client.post("/generate", json=payload, catch_response=True, name="generate_long") as response:
            if response.status_code == 200:
                try:
                    result = response.json()
                    if "text" in result and result["text"]:
                        # Log metrics info
                        tokens_used = result.get("token_used", 0)
                        latency = result.get("latency", 0)
                        response.success()
                        print(f"Long text - User: {self.user_id}, Tokens: {tokens_used}, Latency: {latency:.3f}s")
                    else:
                        response.failure(f"Response missing text field: {response.text}")
                except json.JSONDecodeError as ex:
                    response.failure(f"Failed to decode JSON response: {response.text} - {ex}")
            else:
                response.failure(f"Failed to generate text: {response.status_code} - {response.text}")

    @task(1)  # Occasionally check metrics
    def check_metrics(self):
        with self.client.get("/metrics", catch_response=True, name="check_metrics") as response:
            if response.status_code == 200:
                metrics_text = response.text
                # Count some key metrics
                request_count = metrics_text.count('llm_requests_total')
                token_count = metrics_text.count('llm_input_tokens_total')
                response.success()
                print(f"Metrics check - Found {request_count} request metrics, {token_count} token metrics")
            else:
                response.failure(f"Failed to get metrics: {response.status_code}")
                
from locust import events

# Track total requests and errors for summary
total_requests = 0
total_errors = 0

@events.request.add_listener
def my_request_handler(request_type, name, response_time, response_length, response, exception, start_time, context, **kwargs):
    global total_requests, total_errors
    total_requests += 1
    
    if exception:
        total_errors += 1
        print(f"❌ Request {name} failed: {exception}")
    else:
        if name in ["generate_short", "generate_long"]:
            try:
                result = response.json()
                tokens = result.get("token_used", 0)
                latency = result.get("latency", 0)
                print(f"✅ {name}: {response_time:.0f}ms, {tokens} tokens, {latency:.2f}s processing")
            except:
                print(f"✅ {name}: {response_time:.0f}ms")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print(f"\n🏁 Load test completed!")
    print(f"📊 Total requests: {total_requests}")
    print(f"❌ Total errors: {total_errors}")
    print(f"✅ Success rate: {((total_requests - total_errors) / total_requests * 100):.1f}%" if total_requests > 0 else "N/A")
