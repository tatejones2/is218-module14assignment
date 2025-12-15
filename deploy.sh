#!/bin/bash

# Production Deployment Script for Digital Ocean
# Usage: ./deploy.sh

set -e

echo "🚀 Starting deployment to Digital Ocean..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and fill in your values"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '#' | xargs)

echo "📦 Building Docker images..."
docker-compose -f docker-compose.prod.yml build

echo "🔄 Pulling latest images..."
docker-compose -f docker-compose.prod.yml pull

echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down || true

echo "🚀 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

echo "⏳ Waiting for services to be healthy..."
sleep 10

echo "✅ Checking service status..."
docker-compose -f docker-compose.prod.yml ps

echo "🌐 Your application should now be available at https://${DOMAIN}"
echo ""
echo "📊 View logs with: docker-compose -f docker-compose.prod.yml logs -f"
echo "🛠️  Manage Caddy with: docker-compose -f docker-compose.prod.yml exec caddy caddy"
