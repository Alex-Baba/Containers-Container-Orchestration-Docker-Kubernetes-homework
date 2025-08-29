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

## 3. Flask App Environment Variables

Your `main.py` uses two environment variables:
- `APP_MESSAGE` (from ConfigMap)
- `APP_SECRET` (from Secret)

It displays both on the homepage:
```
Hello from ConfigMap! I am Groot! | Secret: secret_value
```

## 4. Kubernetes ConfigMap and Secret

Create and apply these files:

**configmap.yaml**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: main-config
data:
  APP_MESSAGE: "Hello from ConfigMap! I am Groot!"
```

**secret.yaml**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: main-secret
type: Opaque
data:
  APP_SECRET: c2VjcmV0X3ZhbHVl # base64 for "secret_value"
```

Apply them:
```sh
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
```

## 5. Deployment Manifest Example

Your `deployment.yaml` should include:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: main-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: main-app
  template:
    metadata:
      labels:
        app: main-app
    spec:
      containers:
        - name: main
          image: localhost:5000/main:latest
          ports:
            - containerPort: 8000
          env:
            - name: APP_MESSAGE
              valueFrom:
                configMapKeyRef:
                  name: main-config
                  key: APP_MESSAGE
            - name: APP_SECRET
              valueFrom:
                secretKeyRef:
                  name: main-secret
                  key: APP_SECRET
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
```

**Liveness and readiness probes** use the `/health` endpoint in your Flask app to check if the container is running and ready to serve traffic.  
If `/health` fails, Kubernetes will restart the container (liveness) or stop sending traffic