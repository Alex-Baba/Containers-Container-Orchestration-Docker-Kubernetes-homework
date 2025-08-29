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
Hello from ConfigMap! | Secret: secret_value
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
  APP_MESSAGE: "Hello from ConfigMap!"
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

Add environment variables to your deployment:

```yaml
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
```

## 6. Build, Push, and Deploy

```sh
docker build -t main-nonroot:latest -f Dockerfile .
docker tag main-nonroot:latest localhost:5000/main:latest
docker push localhost:5000/main:latest
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

## 7. Restart Pod (if needed)

```sh
kubectl get pods
kubectl delete pod <pod-name>
```

## 8. Access Your App

Open [http://localhost:30080](http://localhost:30080) in your browser.

You should see:
```
Hello from ConfigMap! | Secret: secret_value
```

## 9. Troubleshooting

- Check pod logs:
  ```sh
  kubectl logs <pod-name>
  ```
- Check environment variables inside pod:
  ```sh
  kubectl exec -it <pod-name> -- printenv
  ```