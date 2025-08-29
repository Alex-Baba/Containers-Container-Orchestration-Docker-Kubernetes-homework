# Flask App Deployment Guide

## 1. Build and Run with Docker

```sh
docker build -t main-nonroot -f Dockerfile .
docker run -p 8000:8000 main-nonroot
```

## 2. Dockerfile Improvements

- Uses multi-stage build for a smaller image.
- Runs as a non-root user (`appuser`).
- Installs `curl` in the final image for health checks.
- Adds a `/health` endpoint in the Flask app.
- Includes a Docker `HEALTHCHECK` that checks `http://localhost:8000/health`.

## 3. Check Container Health

After running the container, check health status:

```sh
docker ps
```
Look for `(healthy)` in the STATUS column.

For detailed health info:

```sh
docker inspect --format='{{json .State.Health}}' <container_id>
```

## 4. Run with Docker Compose

```sh
docker-compose up --build
```
Access the app at [http://localhost:8000](http://localhost:8000).

## 5. Push Image to Local Registry (for Kubernetes)

Start a local registry if not running:
```sh
docker run -d -p 5000:5000 --name registry registry:2
```

Tag and push your image:
```sh
docker tag main-nonroot localhost:5000/main:latest
docker push localhost:5000/main:latest
```

## 6. Deploy on Kubernetes (Rancher Desktop)

Apply the manifests:
```sh
kubectl apply -f service.yaml
```

### Access the App

- **NodePort:**  
  Open [http://localhost:30080](http://localhost:30080)

- **Port Forwarding:**  
  ```sh
  kubectl port-forward service/main-app-service 8000:8000
  ```
  Then open [http://localhost:8000](http://localhost:8000)

## 7. Troubleshooting

- Check pod status:
  ```sh
  kubectl get pods
  ```
- View pod logs:
  ```sh
  kubectl logs
  ```