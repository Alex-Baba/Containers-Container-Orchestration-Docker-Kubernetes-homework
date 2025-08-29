# Flask App Deployment Guide

## 1. Build and Run with Docker

```sh
docker build -t main:latest .
docker run -p 8000:8000 main:latest
```

## 2. Run with Docker Compose

```sh
docker-compose up --build
```
Access the app at [http://localhost:8000](http://localhost:8000).

## 3. Push Image to Local Registry (for Kubernetes)

Start a local registry if not running:
```sh
docker run -d -p 5000:5000 --name registry registry:2
```

Tag and push your image:
```sh
docker tag main:latest localhost:5000/main:latest
docker push localhost:5000/main:latest
```

## 4. Deploy on Kubernetes (Rancher Desktop)

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

## 5. Troubleshooting

- Check pod status:
  ```sh
  kubectl get pods
  ```
- View pod logs:
  ```sh
  kubectl logs <pod-name>
  ```