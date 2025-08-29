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
          resources:
            requests:
              cpu: 100m
            limits:
              cpu: 500m
```

## 6. Service Manifest Example

Your `service.yaml` should expose your app:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: main-app-service
spec:
  type: NodePort
  selector:
    app: main-app
  ports:
    - protocol: TCP
      port: 8000
      targetPort: 8000
      nodePort: 30080
```

## 7. Ingress Manifest Example

Add an ingress to route traffic from a custom domain:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: main-app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - host: main-app.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: main-app-service
                port:
                  number: 8000
```

Apply it:
```sh
kubectl apply -f ingress.yaml
```

## 8. Hosts File Setup

Add this line to your machine’s hosts file (`C:\Windows\System32\drivers\etc\hosts` on Windows):

```
127.0.0.1 main-app.local
```

## 9. Expose Ingress Controller (Traefik Example)

If using Traefik, port-forward port 80:

```sh
kubectl port-forward -n kube-system svc/traefik 80:80
```

## 10. Horizontal Pod Autoscaler (HPA)

Create `hpa.yaml`:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: main-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: main-app
  minReplicas: 2
  maxReplicas: 5
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 50
```

Apply it:
```sh
kubectl apply -f hpa.yaml
```

Check HPA status:
```sh
kubectl get hpa
kubectl describe hpa main-app-hpa
```

## 11. Access Your App

Open [http://main-app.local](http://main-app.local) in your browser.

You should see:
```
Hello from ConfigMap! I am Groot! | Secret: secret_value
```

## 12. Troubleshooting

- Check pod logs:
  ```sh
  kubectl logs <pod-name>
  ```
- Check environment variables inside pod:
  ```sh
  kubectl exec -it <pod-name> -- env
  ```
- Describe pod for probe status:
  ```sh
  kubectl describe pod <pod-name>
  ```
- Check ingress status:
  ```sh
  kubectl get ingress
  kubectl describe ingress main-app-ingress
  ```
- Check HPA status:
  ```sh
  kubectl get hpa
  kubectl describe hpa main-app
  ```