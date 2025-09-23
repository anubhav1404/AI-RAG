# k8s_client.py
import os
from kubernetes import client, config
from kubernetes.client import ApiException

def load_kube_config():
    """
    Load kube config from KUBECONFIG env var if present, else default locations,
    else assume in-cluster config.
    """
    kubeconfig = os.getenv("KUBECONFIG")
    try:
        if kubeconfig:
            config.load_kube_config(config_file=kubeconfig)
        else:
            # try default kubeconfig (e.g. ~/.kube/config)
            try:
                config.load_kube_config()
            except Exception:
                # fallback to in-cluster
                config.load_incluster_config()
    except Exception as e:
        raise RuntimeError(f"Failed to load kube config: {e}")

def core_api():
    load_kube_config()
    return client.CoreV1Api()

def apps_api():
    load_kube_config()
    return client.AppsV1Api()

# -------------------
# Namespace-specific
# -------------------

def list_pods(namespace="default", label_selector=None):
    api = core_api()
    try:
        pods = api.list_namespaced_pod(namespace=namespace, label_selector=label_selector)
        return [format_pod(p) for p in pods.items]
    except ApiException as e:
        return {"error": f"{e}"}

def list_services(namespace="default"):
    api = core_api()
    try:
        services = api.list_namespaced_service(namespace=namespace)
        return [format_service(s) for s in services.items]
    except ApiException as e:
        return {"error": f"{e}"}

def list_deployments(namespace="default"):
    api = apps_api()
    try:
        deployments = api.list_namespaced_deployment(namespace=namespace)
        return [format_deployment(d) for d in deployments.items]
    except ApiException as e:
        return {"error": f"{e}"}

# -------------------
# All namespaces
# -------------------

def list_pods_all(label_selector=None):
    api = core_api()
    try:
        pods = api.list_pod_for_all_namespaces(label_selector=label_selector)
        return [format_pod(p) for p in pods.items]
    except ApiException as e:
        return {"error": f"{e}"}

def list_services_all():
    api = core_api()
    try:
        services = api.list_service_for_all_namespaces()
        return [format_service(s) for s in services.items]
    except ApiException as e:
        return {"error": f"{e}"}

def list_deployments_all():
    api = apps_api()
    try:
        deployments = api.list_deployment_for_all_namespaces()
        return [format_deployment(d) for d in deployments.items]
    except ApiException as e:
        return {"error": f"{e}"}

# -------------------
# Formatters
# -------------------

def format_pod(pod):
    return {
        "name": pod.metadata.name,
        "namespace": pod.metadata.namespace,
        "phase": getattr(pod.status, "phase", None),
        "node": getattr(pod.spec, "node_name", None),
        "host_ip": getattr(pod.status, "host_ip", None),
        "pod_ip": getattr(pod.status, "pod_ip", None),
        "start_time": str(pod.status.start_time) if getattr(pod.status, "start_time", None) else None,
        "containers": [{"name": c.name, "image": c.image} for c in getattr(pod.spec, "containers", []) or []]
    }

def format_service(svc):
    return {
        "name": svc.metadata.name,
        "namespace": svc.metadata.namespace,
        "type": getattr(svc.spec, "type", None),
        "cluster_ip": getattr(svc.spec, "cluster_ip", None),
        # Kubernetes Python client uses snake_case for externalIPs
        "external_ips": getattr(svc.spec, "external_i_ps", []),
        "ports": [
            {
                "port": p.port,
                "target_port": p.target_port,
                "protocol": p.protocol
            }
            for p in getattr(svc.spec, "ports", []) or []
        ]
    }

def format_deployment(dep):
    return {
        "name": dep.metadata.name,
        "namespace": dep.metadata.namespace,
        "replicas": getattr(dep.spec, "replicas", None),
        "available_replicas": getattr(dep.status, "available_replicas", None),
        "images": [c.image for c in getattr(dep.spec.template.spec, "containers", []) or []]
    }

