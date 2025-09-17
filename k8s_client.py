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

def format_pod(pod):
    return {
        "name": pod.metadata.name,
        "namespace": pod.metadata.namespace,
        "phase": pod.status.phase,
        "node": pod.spec.node_name,
        "host_ip": pod.status.host_ip,
        "pod_ip": pod.status.pod_ip,
        "start_time": str(pod.status.start_time) if pod.status.start_time else None,
        "containers": [{"name": c.name, "image": c.image} for c in pod.spec.containers]
    }

def format_service(svc):
    return {
        "name": svc.metadata.name,
        "namespace": svc.metadata.namespace,
        "type": svc.spec.type,
        "cluster_ip": svc.spec.cluster_ip,
        # fix here: attribute is external_i_ps not external_ips
        "external_ips": svc.spec.external_i_ps,
        "ports": [
            {
                "port": p.port,
                "target_port": p.target_port,
                "protocol": p.protocol
            }
            for p in svc.spec.ports or []
        ]
    }


def format_deployment(dep):
    return {
        "name": dep.metadata.name,
        "namespace": dep.metadata.namespace,
        "replicas": dep.spec.replicas,
        "available_replicas": dep.status.available_replicas,
        "images": [c.image for c in dep.spec.template.spec.containers]
    }

