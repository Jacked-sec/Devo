# Fluent Bit Deployment Guide (AWS EKS + Helm + External ConfigMap)

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
``` bash
nano fluent-bit-config.yaml
```
Insert
``` bash
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluent-bit
  namespace: logging
data:

  fluent-bit.conf: |
    [SERVICE]
        Flush        5
        Log_Level    info
        Daemon       Off
        Parsers_File parsers.conf
        storage.path /var/log/flb-storage
        storage.sync normal
        storage.checksum off
        storage.backlog.mem_limit 50M

    [INPUT]
        Name              tail
        Path              /var/log/containers/*.log
        Tag               kube.*
        Parser            cri
        Refresh_Interval  10
        Skip_Long_Lines   On
        Mem_Buf_Limit     50MB
        storage.type      filesystem

    #  Kubernetes metadata
    [FILTER]
        Name                kubernetes
        Match               kube.*
        Keep_Log            On
        K8S-Logging.Parser  On
        K8S-Logging.Exclude On

    #Exclude log fluent-bit 
    [FILTER]
        Name    grep
        Match   kube.*
        Exclude kubernetes.container_name fluent-bit

    # rename log message  syslog output
    [FILTER]
        Name    modify
        Match   kube.*
        Rename  log message

    [OUTPUT]
        Name            syslog
        Match           kube.*
        Host            <relayIP>
        Port            13011
        Mode            tcp
        Syslog_Format   rfc5424
        Syslog_Message_Key message
        Retry_Limit     False

  parsers.conf: |
    [PARSER]
        Name        cri
        Format      regex
        Regex       ^(?<time>[^ ]+) (?<stream>stdout|stderr) (?<log>.*)$
        Time_Key    time
        Time_Format %Y-%m-%dT%H:%M:%S.%L%z
```
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
## log Fluent Bit
``` bash
kubectl logs -n logging -l app.kubernetes.io/name=fluent-bit
```


# Full Deployment Command Summary

``` bash
kubectl create namespace logging
kubectl apply -f fluent-bit-config.yaml
helm repo add fluent https://fluent.github.io/helm-charts
helm repo update
helm install fluent-bit fluent/fluent-bit -n logging -f values.yaml
```
Jacked
