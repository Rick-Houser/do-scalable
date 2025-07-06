# Kubernetes Scalability Demo

A Flask application that demonstrates horizontal pod autoscaling (HPA) and load distribution across Kubernetes nodes. Built for DigitalOcean Kubernetes (DOKS) clusters.
<br>

## Features

- **Real-time Pod Information**: Shows which specific pod handled each request
- **Node Distribution Visibility**: Displays which cluster node the pod is running on
- **Load Balancing Demo**: Refresh to see requests hit different pods across nodes
- **Horizontal Scaling**: Watch HPA create new pods under load
- **REST API**: JSON endpoint for programmatic access to pod/node data
<br>

## Prerequisites

- Docker installed locally
- DigitalOcean account with billing enabled
- `doctl` CLI tool [installed and authenticated](https://docs.digitalocean.com/reference/doctl/how-to/install/)
- `kubectl` [configured for your DOKS cluster](https://docs.digitalocean.com/products/kubernetes/how-to/connect-to-cluster/)
<br>

## Setup

### Create DOKS Cluster

Create a DigitalOcean Kubernetes cluster with autoscaling enabled:

```bash
doctl kubernetes cluster create scalable-demo-cluster \
  --tag do-scalable \
  --auto-upgrade=true \
  --node-pool "name=worker-pool;count=2;auto-scale=true;min-nodes=1;max-nodes=3;tag=do-scalable"
```

Wait for cluster creation (3-5 minutes):
```bash
doctl kubernetes cluster list
kubectl get nodes
```

### Container Registry Setup
```bash
# Create registry
doctl registry create scalable-demo-registry

# Integrate with cluster
doctl registry kubernetes-manifest | kubectl apply -f -
```
_Alternative: Use Docker Hub or other registries by updating image URLs in k8s/deployment.yaml_

## Local Development

1. **Clone the repository**
   ```bash
   git clone git@github.com:Rick-Houser/do-scalable.git
   cd do-scalable
   ```

2. **Test locally**
   ```bash
   pip install flask requests
   python app.py
   ```
   Visit `http://localhost:5000`

3. **Test with Docker**
   ```bash
   docker build -t do-scalable .
   docker run -p 5000:5000 do-scalable
   ```
<br>

## Deployment

1. **Tag and push to registry**
   ```bash
   docker tag do-scalable registry.digitalocean.com/YOUR_REGISTRY/do-scalable:latest
   docker push registry.digitalocean.com/YOUR_REGISTRY/do-scalable:latest
   ```

2. **Update deployment manifest**
   ```bash
   # Edit k8s/deployment.yaml to use your registry URL
   ```

3. **Deploy to Kubernetes**
   ```bash
   kubectl apply -f k8s/
   ```

4. **Get external IP**
   ```bash
   kubectl get services
   ```
<br>

## Usage

- **Main Demo**: Visit the LoadBalancer external IP
- **API Endpoint**: `GET /api/info` for JSON data
- **Load Testing**: Refresh repeatedly to see different pods/nodes handling requests
<br>

## Test Autoscaling

### Load Testing with DigitalOcean's Load Generator

1. **Deploy the load generator** using DigitalOcean's provided configuration:
    
    ```bash
    kubectl apply -f https://raw.githubusercontent.com/digitalocean/kubernetes-sample-apps/master/load-generator.yaml
    
    ```
    
2. **Monitor HPA and Cluster Autoscaler status**:
    
    ```bash
    # Check HPA status
    kubectl describe hpa scalability-demo
    
    # Check Cluster Autoscaler status
    kubectl get configmap cluster-autoscaler-status -n kube-system -o yaml
    
    ```
    
3. **Scale up load generation** to increase pressure:
    
    ```bash
    kubectl scale deployment/load-generator --replicas 2
    
    ```
    
4. **Observe scaling behavior**:
    - After 5 minutes of sustained CPU spiking, HPA schedules more pods
    - Another 5 minutes later, if cluster capacity is reached, Cluster Autoscaler adds nodes
    - Watch pods distribute across nodes: `kubectl get pods -o wide`
    
5. **Scale down to observe cleanup**:
    
    ```bash
    kubectl scale deployment/load-generator --replicas 1
    
    ```
    
    - After 5 minutes of lowered CPU use, HPA deletes unutilized pods
    - Another 5 minutes later, Cluster Autoscaler scales down excess nodes
    <br>

### Alternative Quick Test

For immediate testing without the full load generator setup:
```bash
kubectl run -i --tty load-generator --rm --image=busybox --restart=Never -- /bin/sh

# Inside the pod:
while true; do wget -q -O- http://YOUR_EXTERNAL_IP; done
```
<br>

### Real-time Monitoring

Watch the scaling process live:
```bash
# Monitor HPA decisions
kubectl get hpa -w

# Watch pod creation/deletion
kubectl get pods -w

# Monitor resource utilization  
kubectl top pods
```
<br>

## Configuration

- **Min Replicas**: 3
- **Max Replicas**: 10
- **CPU Threshold**: 70%
- **Target Port**: 5000
- **Resource Requests**: 100m CPU, 128Mi memory
- **Resource Limits**: 500m CPU, 256Mi memory

## Architecture

- **Pod-level autoscaling**: HPA scales from 3 to 10 replicas based on CPU utilization
- **Node-level autoscaling**: Cluster Autoscaler adds/removes nodes based on capacity
- **Load balancing**: DigitalOcean LoadBalancer distributes traffic across pods
- **Multi-node deployment**: Pods distributed across cluster nodes for high availability