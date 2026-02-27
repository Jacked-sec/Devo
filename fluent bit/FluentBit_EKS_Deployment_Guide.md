# 🚀 Fluent Bit Deployment Guide (AWS EKS + Helm + External ConfigMap)

## 📌 Architecture Overview

    EKS Node
       ↓
    Fluent Bit (DaemonSet via Helm)
       ↓ TCP 13011 / 13012
    EC2 Ubuntu (rsyslog / relay)

------------------------------------------------------------------------

# 1️⃣ Install Helm (If Not Installed)

## Linux / macOS

``` bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
helm version
```

------------------------------------------------------------------------

# 2️⃣ Create Namespace

``` bash
kubectl create namespace logging
kubectl get ns
```

------------------------------------------------------------------------

# 3️⃣ Apply Fluent Bit ConfigMap

Ensure you already created:

-   `fluent-bit-config.yaml`
-   Configured with:
    -   Port `13011`
    -   Port `13012` (if required)

Apply configuration:

``` bash
kubectl apply -f fluent-bit-config.yaml
kubectl get configmap -n logging
```

------------------------------------------------------------------------

# 4️⃣ Add Helm Repository

``` bash
helm repo add fluent https://fluent.github.io/helm-charts
helm repo update
```

------------------------------------------------------------------------

# 5️⃣ Create values.yaml (Use Existing ConfigMap)

Create file:

``` bash
nano values.yaml
```

Insert:

``` yaml
kind: DaemonSet

existingConfigMap: fluent-bit

serviceAccount:
  create: true

rbac:
  create: true

daemonSetVolumes:
  - name: varlog
    hostPath:
      path: /var/log

daemonSetVolumeMounts:
  - name: varlog
    mountPath: /var/log
```

------------------------------------------------------------------------

# 6️⃣ Install Fluent Bit via Helm

``` bash
helm install fluent-bit fluent/fluent-bit   --namespace logging   -f values.yaml
```

------------------------------------------------------------------------

# 7️⃣ Verify Deployment

Check Pods:

``` bash
kubectl get pods -n logging -o wide
```

Check Logs:

``` bash
kubectl logs -n logging -l app.kubernetes.io/name=fluent-bit
```

------------------------------------------------------------------------

# 🔄 Updating Configuration

If you modify `fluent-bit-config.yaml`:

``` bash
kubectl apply -f fluent-bit-config.yaml
kubectl rollout restart daemonset fluent-bit -n logging
```

------------------------------------------------------------------------

# 🛠 Troubleshooting

## Test Network Connectivity to Relay

``` bash
kubectl exec -it -n logging <pod-name> -- sh
nc -vz <relayIP> 13011
```

## Confirm ConfigMap is Mounted

``` bash
kubectl describe pod -n logging <pod-name>
```

------------------------------------------------------------------------

# 📁 Recommended Repository Structure

    .
    ├── fluent-bit-config.yaml
    ├── values.yaml
    └── FluentBit_EKS_Deployment_Guide.md

------------------------------------------------------------------------

# 🎯 Full Deployment Command Summary

``` bash
kubectl create namespace logging
kubectl apply -f fluent-bit-config.yaml
helm repo add fluent https://fluent.github.io/helm-charts
helm repo update
helm install fluent-bit fluent/fluent-bit -n logging -f values.yaml
```

------------------------------------------------------------------------

# ✅ Production Best Practices

-   Enable filesystem buffering
-   Set Mem_Buf_Limit
-   Use Retry_Limit False
-   Define CPU & memory limits in DaemonSet
-   Open Security Group ports 13011 / 13012
-   Monitor EPS and resource usage

------------------------------------------------------------------------

# 🔐 Optional Enhancements

-   TLS syslog
-   High Availability relay
-   Multi-port routing (C1 / C2 split)
-   EPS tuning for 10k+ logs/sec
-   Centralized log monitoring dashboard

------------------------------------------------------------------------

© Deployment Guide - Fluent Bit on AWS EKS
