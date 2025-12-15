# Production Deployment Guide - Digital Ocean with Caddy & Docker

## Prerequisites

- Digital Ocean Droplet (Ubuntu 22.04+ recommended)
- Domain pointing to your droplet's IP address
- SSH access to your droplet
- Docker and Docker Compose installed on the droplet

## Step 1: Initial Droplet Setup

SSH into your droplet:
```bash
ssh root@your_droplet_ip
```

Update system packages:
```bash
apt-get update && apt-get upgrade -y
```

Install Docker:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

Install Docker Compose:
```bash
apt-get install -y docker-compose-plugin
```

Create app directory:
```bash
mkdir -p /opt/fastapi-app
cd /opt/fastapi-app
```

## Step 2: Clone Your Repository

```bash
git clone <your-repo-url> .
# Or if updating existing deployment
git pull origin main
```

## Step 3: Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit the .env file with production values:
```bash
nano .env
```

**Important values to set:**
- `DB_PASSWORD`: Strong random password for PostgreSQL
- `JWT_SECRET_KEY`: Generate with: `openssl rand -hex 32`
- `JWT_REFRESH_SECRET_KEY`: Generate with: `openssl rand -hex 32`
- `DOMAIN`: Your domain (tatejonesis218project3.com)
- `CADDY_EMAIL`: Your email for SSL certificate notifications

Example .env content:
```
DB_PASSWORD=MyS3cur3DBP@ssw0rd!
JWT_SECRET_KEY=a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2
JWT_REFRESH_SECRET_KEY=f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3b2a1
DOMAIN=tatejonesis218project3.com
CADDY_EMAIL=admin@example.com
REDIS_URL=redis://redis:6379/0
```

## Step 4: DNS Configuration

Update your domain's DNS records to point to your droplet's IP:

**A Record:**
- Name: @ (or your domain)
- Type: A
- Value: your_droplet_ip

**Optional CNAME Records:**
- Name: www
- Type: CNAME
- Value: @

Wait for DNS propagation (usually 5-30 minutes).

## Step 5: Deploy the Application

Make the deploy script executable:
```bash
chmod +x deploy.sh
```

Run the deployment:
```bash
./deploy.sh
```

This will:
1. Build Docker images
2. Pull latest images
3. Stop existing containers
4. Start all services (web, database, Caddy)
5. Configure SSL certificates automatically

## Step 6: Verify Deployment

Check container status:
```bash
docker-compose -f docker-compose.prod.yml ps
```

View logs:
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

Check specific service:
```bash
docker-compose -f docker-compose.prod.yml logs web
docker-compose -f docker-compose.prod.yml logs caddy
docker-compose -f docker-compose.prod.yml logs db
```

Visit your domain in browser:
```
https://tatejonesis218project3.com
```

## Caddy Management

### View SSL Certificate Status
```bash
docker-compose -f docker-compose.prod.yml exec caddy caddy list-certs
```

### Reload Configuration
```bash
docker-compose -f docker-compose.prod.yml exec caddy caddy reload
```

### View Caddy Logs
```bash
docker-compose -f docker-compose.prod.yml logs caddy
```

## Maintenance

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f web
```

### Restart Services
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Update Application
```bash
git pull origin main
./deploy.sh
```

### Backup Database
```bash
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres fastapi_db > backup-$(date +%Y%m%d-%H%M%S).sql
```

### Database Shell Access
```bash
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -d fastapi_db
```

## Troubleshooting

### SSL Certificate Issues
```bash
# View Caddy logs
docker-compose -f docker-compose.prod.yml logs caddy

# Renew certificate manually
docker-compose -f docker-compose.prod.yml exec caddy caddy reload
```

### Application Won't Start
```bash
# Check web app logs
docker-compose -f docker-compose.prod.yml logs web

# Check database connection
docker-compose -f docker-compose.prod.yml exec web python -c "from app.database import engine; print('DB OK')"
```

### Port Already in Use
```bash
# Find process using port 80 or 443
lsof -i :80
lsof -i :443

# Kill process if needed
kill -9 <PID>
```

### High Memory Usage
```bash
# Check container stats
docker stats
```

## Firewall Configuration (Optional but Recommended)

```bash
# Allow SSH
ufw allow 22/tcp

# Allow HTTP
ufw allow 80/tcp

# Allow HTTPS
ufw allow 443/tcp

# Enable firewall
ufw enable
```

## Security Best Practices

1. ✅ Change all default passwords in .env
2. ✅ Use strong, random JWT secrets
3. ✅ Keep Docker images updated
4. ✅ Enable firewall
5. ✅ Use SSH keys instead of passwords
6. ✅ Monitor application logs regularly
7. ✅ Set up automated backups

## Monitoring & Alerts

Monitor disk space:
```bash
df -h
```

Monitor resource usage:
```bash
docker stats
```

## Rollback Procedure

If deployment fails:
```bash
# View previous image
docker images

# Restart with previous image (if available)
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

## Useful Commands

```bash
# SSH into container
docker-compose -f docker-compose.prod.yml exec web bash

# Rebuild specific service
docker-compose -f docker-compose.prod.yml build --no-cache web

# Remove unused images/containers
docker system prune

# Check environment in container
docker-compose -f docker-compose.prod.yml exec web env
```

## Support

For issues, check:
1. Application logs: `docker-compose -f docker-compose.prod.yml logs -f web`
2. Caddy logs: `docker-compose -f docker-compose.prod.yml logs -f caddy`
3. Database logs: `docker-compose -f docker-compose.prod.yml logs -f db`
4. System logs: `/var/log/syslog`
