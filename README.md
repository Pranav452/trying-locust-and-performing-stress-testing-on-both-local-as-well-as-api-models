# LLM API with Load Testing and Performance Monitoring

A comprehensive FastAPI-based LLM service that supports both local (Ollama) and cloud (OpenAI) models, featuring built-in performance monitoring, rate limiting, and stress testing capabilities.

## Features

- **Multi-Backend Support**: Switch between Ollama (local) and OpenAI (cloud) models
- **Performance Monitoring**: Prometheus metrics integration with Grafana dashboards
- **Rate Limiting**: User-based governance and request throttling
- **Load Testing**: Comprehensive Locust-based stress testing suite
- **Containerized Deployment**: Docker Compose for easy deployment
- **Health Checks**: Built-in health monitoring for all services
- **Token Counting**: Accurate token usage tracking and billing metrics

## Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────┐
│   Load Testing  │    │  FastAPI App │    │  Monitoring │
│    (Locust)     │───▶│   (main.py)  │───▶│ (Prometheus)│
└─────────────────┘    └──────────────┘    └─────────────┘
                              │                     │
                              ▼                     ▼
                       ┌──────────────┐    ┌─────────────┐
                       │    Models    │    │   Grafana   │
                       │ Ollama/OpenAI│    │ (Dashboard) │
                       └──────────────┘    └─────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- OpenAI API key (optional, for OpenAI backend)

### 1. Clone and Setup

```bash
git clone https://github.com/Pranav452/trying-locust-and-performing-stress-testing-on-both-local-as-well-as-api-models.git
cd deployment_maybr
```

### 2. Environment Configuration

Create a `.env` file:

```bash
# Model Backend Configuration
MODEL_BACKEND=ollama  # or "openai"
OPENAI_API_KEY=your_openai_api_key_here  # Required only for OpenAI backend
OLLAMA_URL=http://localhost:11434  # Ollama server URL
```

### 3. Docker Deployment

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f llm-services
```

### 4. Service URLs

- **API Service**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Metrics Endpoint**: http://localhost:8000/metrics

## API Endpoints

### Core Endpoints

#### `POST /generate`
Generate text using the configured LLM backend.

**Request Body:**
```json
{
  "prompt": "What is machine learning?",
  "max_tokens": 128,
  "temperature": 0.8,
  "user_id": "user123"
}
```

**Response:**
```json
{
  "text": "Machine learning is a subset of artificial intelligence...",
  "token_used": 45,
  "tokens_in": 15,
  "tokens_out": 30,
  "latency": 1.234
}
```

#### `GET /health`
Health check endpoint for monitoring service availability.

#### `GET /metrics`
Prometheus metrics endpoint for monitoring and alerting.

#### `GET /`
Root endpoint showing service information and current backend.

## Load Testing

### Running Load Tests

The project includes comprehensive load testing using Locust:

```bash
# Install dependencies (if running locally)
pip install -r requirements.txt

# Start the API service first
uvicorn main:app --reload

# Run load tests
locust -f locustfile.py --host=http://localhost:8000
```

### Load Test Features

- **Multiple Test Scenarios**: Short and long text generation
- **User Simulation**: Realistic user behavior patterns
- **Metrics Collection**: Real-time performance monitoring
- **Error Handling**: Comprehensive error tracking and reporting
- **Rate Limiting Tests**: Validates governance controls

### Test Configuration

- **Short Text Generation**: 20-50 tokens, higher frequency
- **Long Text Generation**: 100-200 tokens, lower frequency
- **Metrics Monitoring**: Periodic health checks
- **User Identification**: Unique user IDs for rate limiting

## Monitoring and Metrics

### Prometheus Metrics

The service exposes comprehensive metrics:

- `llm_requests_total`: Total number of requests by backend/model/status
- `llm_request_latency_seconds`: Request processing latency
- `llm_active_requests`: Current number of active requests
- `llm_input_tokens_total`: Total input tokens processed
- `llm_output_tokens_total`: Total output tokens generated
- `llm_tokens_per_second`: Token processing rate
- `llm_rate_limit_exceeded_total`: Rate limit violations
- `llm_user_request_count_total`: Per-user request counts

### Grafana Dashboards

Access Grafana at http://localhost:3000 with credentials `admin/admin`.

**Recommended Dashboard Panels:**
- Request rate and latency trends
- Token usage and costs
- Error rates and success metrics
- User activity and rate limiting
- Model performance comparisons

## Rate Limiting and Governance

### Rate Limit Configuration

```python
RATE_LIMIT = {
    "anonymous": 100,    # requests per hour
    "user": 1000,       # requests per hour
    "default": 5        # requests per hour
}
```

### User Management

- **Anonymous Users**: Limited to 100 requests/hour
- **Authenticated Users**: Up to 1000 requests/hour
- **Default Users**: 5 requests/hour fallback
- **Custom Limits**: Configurable per-user limits

## Development

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Project Structure

```
deployment_maybr/
├── main.py              # FastAPI application and core logic
├── governance.py        # Rate limiting and user management
├── metrics.py          # Prometheus metrics definitions
├── locustfile.py       # Load testing scenarios
├── requirements.txt    # Python dependencies
├── dockerfile         # Container image definition
├── docker-compose.yml # Multi-service orchestration
├── prometheus/
│   └── prometheus.yml # Monitoring configuration
├── logs/              # Application logs
└── ollama/           # Local model storage (gitignored)
```

### Key Components

- **main.py**: Core FastAPI application with model switching logic
- **governance.py**: Rate limiting and user access controls
- **metrics.py**: Prometheus metrics collection and recording
- **locustfile.py**: Comprehensive load testing scenarios

## Model Backends

### Ollama (Local)

- **Model**: TinyLlama (lightweight, fast inference)
- **Deployment**: Local container with persistent storage
- **Benefits**: No API costs, data privacy, customizable
- **Use Cases**: Development, privacy-sensitive applications

### OpenAI (Cloud)

- **Model**: GPT-4.1-nano (high-quality responses)
- **Deployment**: API-based integration
- **Benefits**: High quality, no local resources required
- **Use Cases**: Production applications, high-quality outputs

## Performance Optimization

### Recommended Settings

- **Connection Pooling**: Reuse HTTP connections
- **Async Processing**: Non-blocking request handling
- **Health Checks**: Proactive service monitoring
- **Caching**: Consider response caching for repeated queries
- **Resource Limits**: Configure appropriate Docker resource limits

### Scaling Considerations

- **Horizontal Scaling**: Multiple API service instances
- **Load Balancing**: Distribute requests across instances
- **Database**: Consider persistent storage for user data
- **Monitoring**: Comprehensive alerting and dashboards

## Security

### Best Practices

- **API Key Management**: Store sensitive keys in environment variables
- **Rate Limiting**: Prevent abuse and ensure fair usage
- **Input Validation**: Sanitize all user inputs
- **HTTPS**: Use TLS in production environments
- **Authentication**: Implement proper user authentication

### Environment Variables

```bash
MODEL_BACKEND=ollama          # Backend selection
OPENAI_API_KEY=sk-...        # OpenAI API key (if using OpenAI)
OLLAMA_URL=http://ollama:11434  # Ollama service URL
```

## Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   - Verify Ollama service is running: `docker-compose logs ollama`
   - Check model availability: `curl http://localhost:11434/api/tags`

2. **OpenAI API Errors**
   - Verify API key is set correctly
   - Check API quota and billing status

3. **High Latency**
   - Monitor system resources
   - Check model loading times
   - Verify network connectivity

4. **Rate Limiting Issues**
   - Check user limits in governance.py
   - Monitor rate limit metrics in Prometheus

### Logs and Debugging

```bash
# View service logs
docker-compose logs -f llm-services

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Test API manually
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello", "user_id": "test"}'
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review logs and metrics for debugging information

---

**Built with FastAPI, Ollama, Prometheus, and Locust for comprehensive LLM service testing and monitoring.**
