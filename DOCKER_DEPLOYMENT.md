# Trainova Feedback Network - Docker Deployment

This guide explains how to deploy the Trainova Feedback Network on a Raspberry Pi using Docker.

## Prerequisites

- Raspberry Pi with Raspberry Pi OS (or any compatible Linux distribution)
- Docker installed on your Raspberry Pi
- Docker Compose installed on your Raspberry Pi

## Installation Instructions

### 1. Install Docker on Raspberry Pi

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
     apt-transport-https \
     ca-certificates \
     curl \
     gnupg \
     lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up the repository
echo \
  "deb [arch=armhf signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Add your user to the docker group
sudo usermod -aG docker $USER

# Apply the new group membership
newgrp docker
```

### 2. Install Docker Compose

```bash
# Install pip if not already installed
sudo apt install -y python3-pip

# Install Docker Compose
sudo pip3 install docker-compose
```

### 3. Deploy Trainova Feedback Network

```bash
# Clone the repository or copy the files to your Raspberry Pi
# Navigate to the project directory
cd trainova_feedback_network_v2

# Build and start the containers
docker-compose up -d

# View logs
docker-compose logs -f
```

## Accessing the Application

Once the container is running, you can access the API:

- API endpoint: http://raspberry-pi-ip:5009

## Managing the Container

```bash
# Stop the application
docker-compose down

# Restart the application
docker-compose restart

# View logs
docker-compose logs -f

# Update (after pulling new code)
docker-compose build --no-cache
docker-compose up -d
```

## Persistent Data

The application data is stored in a Docker volume named `trainova_data`. This ensures your training data and models persist between container restarts and updates.

## Troubleshooting

### If the container fails to start:

Check the logs:

```bash
docker-compose logs
```

### If the application can't be accessed:

Verify the container is running:

```bash
docker ps
```

Check if the port is exposed correctly:

```bash
sudo netstat -tuln | grep 5009
```

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
