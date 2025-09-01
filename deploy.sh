#!/bin/bash

# Customer Purchase Prediction - Deployment Script
# This script provides easy deployment options for the ML application

set -e

echo "🚀 Customer Purchase Prediction - Deployment Script"
echo "=================================================="

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  local     - Deploy locally with Python virtual environment"
    echo "  docker    - Deploy using Docker container"
    echo "  api       - Deploy only the API service"
    echo "  dashboard - Deploy only the Streamlit dashboard"
    echo "  stop      - Stop all running services"
    echo "  status    - Check status of running services"
    echo ""
    echo "Examples:"
    echo "  $0 local     # Start both API and dashboard locally"
    echo "  $0 docker    # Start both services in Docker"
    echo "  $0 api       # Start only the API service"
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping services..."
    
    # Stop Docker container
    docker stop $(docker ps -q --filter ancestor=customer-purchase-prediction) 2>/dev/null || true
    
    # Kill processes on ports 8000 and 8501
    pkill -f "uvicorn.*8000" 2>/dev/null || true
    pkill -f "streamlit.*8501" 2>/dev/null || true
    
    echo "✅ Services stopped"
}

# Function to check status
check_status() {
    echo "📊 Service Status:"
    echo "=================="
    
    # Check API
    if check_port 8000; then
        echo "✅ API Service: Running on http://localhost:8000"
        curl -s http://localhost:8000/health | jq . 2>/dev/null || echo "   Health check available"
    else
        echo "❌ API Service: Not running"
    fi
    
    # Check Dashboard
    if check_port 8501; then
        echo "✅ Dashboard: Running on http://localhost:8501"
    else
        echo "❌ Dashboard: Not running"
    fi
    
    # Check Docker
    if docker ps | grep -q customer-purchase-prediction; then
        echo "✅ Docker Container: Running"
    else
        echo "❌ Docker Container: Not running"
    fi
}

# Function to deploy locally
deploy_local() {
    echo "🐍 Deploying locally..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    
    # Start API in background
    echo "🚀 Starting API service..."
    cd src/api
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    API_PID=$!
    cd ../..
    
    # Wait for API to start
    sleep 5
    
    # Start Dashboard
    echo "📊 Starting Streamlit dashboard..."
    cd src/dashboard
    streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &
    DASHBOARD_PID=$!
    cd ../..
    
    # Save PIDs for later cleanup
    echo $API_PID > .api.pid
    echo $DASHBOARD_PID > .dashboard.pid
    
    echo "✅ Local deployment complete!"
    echo "🌐 API: http://localhost:8000"
    echo "📊 Dashboard: http://localhost:8501"
    echo "📚 API Docs: http://localhost:8000/docs"
}

# Function to deploy with Docker
deploy_docker() {
    echo "🐳 Deploying with Docker..."
    
    # Build image if not exists
    if ! docker images | grep -q customer-purchase-prediction; then
        echo "🔨 Building Docker image..."
        docker build -t customer-purchase-prediction .
    fi
    
    # Stop existing container
    docker stop $(docker ps -q --filter ancestor=customer-purchase-prediction) 2>/dev/null || true
    
    # Run container
    echo "🚀 Starting Docker container..."
    docker run -d -p 8000:8000 -p 8501:8501 --name customer-prediction-app customer-purchase-prediction
    
    echo "✅ Docker deployment complete!"
    echo "🌐 API: http://localhost:8000"
    echo "📊 Dashboard: http://localhost:8501"
    echo "📚 API Docs: http://localhost:8000/docs"
}

# Function to deploy only API
deploy_api() {
    echo "🔌 Deploying API only..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Start API
    echo "🚀 Starting API service..."
    cd src/api
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
}

# Function to deploy only dashboard
deploy_dashboard() {
    echo "📊 Deploying Dashboard only..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Start Dashboard
    echo "🚀 Starting Streamlit dashboard..."
    cd src/dashboard
    streamlit run app.py --server.port 8501 --server.address 0.0.0.0
}

# Main script logic
case "${1:-}" in
    "local")
        deploy_local
        ;;
    "docker")
        deploy_docker
        ;;
    "api")
        deploy_api
        ;;
    "dashboard")
        deploy_dashboard
        ;;
    "stop")
        stop_services
        ;;
    "status")
        check_status
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
