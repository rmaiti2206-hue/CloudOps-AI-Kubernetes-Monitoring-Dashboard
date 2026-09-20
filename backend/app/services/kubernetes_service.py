from app.core.config import settings


class KubernetesService:
    """
    Real Kubernetes/EKS service.

    This service connects to Kubernetes using:
      - Local kubeconfig when running on your Windows machine
      - In-cluster configuration when running inside Kubernetes

    It provides:
      - Nodes
      - Pods
      - Deployments
      - Services
      - Namespaces
      - Pod logs
      - Kubernetes events
    """

    def __init__(self):
        self.available = False
        self.core = None
        self.apps = None
        self.autoscaling = None
        self._connection_error = None

        try:
            from kubernetes import client, config

            # ---------------------------------------------------------
            # 1. Try local kubeconfig first
            # ---------------------------------------------------------
            try:
                config.load_kube_config()

                self.core = client.CoreV1Api()
                self.apps = client.AppsV1Api()
                self.autoscaling = client.AutoscalingV1Api()

                # Test connection
                self.core.list_namespace(_request_timeout=5)

                self.available = True
                self._connection_error = None

            except Exception as local_error:

                # -----------------------------------------------------
                # 2. If local config fails, try in-cluster config
                # -----------------------------------------------------
                try:
                    config.load_incluster_config()

                    self.core = client.CoreV1Api()
                    self.apps = client.AppsV1Api()
                    self.autoscaling = client.AutoscalingV1Api()

                    self.core.list_namespace(_request_timeout=5)

                    self.available = True
                    self._connection_error = None

                except Exception as cluster_error:
                    self.available = False
                    self._connection_error = (
                        f"Local kubeconfig error: {local_error}; "
                        f"In-cluster config error: {cluster_error}"
                    )

        except ImportError as exc:
            self.available = False
            self._connection_error = (
                "Kubernetes Python package is not installed. "
                "Run: pip install kubernetes"
            )

        except Exception as exc:
            self.available = False
            self._connection_error = str(exc)

    # ================================================================
    # INTERNAL HELPERS
    # ================================================================

    def _ensure_available(self):
        """
        Make sure Kubernetes is connected.

        We intentionally do NOT return demo data.
        If Kubernetes is unavailable, raise a useful error instead.
        """

        if not self.available or self.core is None:
            raise RuntimeError(
                "Kubernetes cluster is not available. "
                f"Connection error: {self._connection_error}"
            )

    @staticmethod
    def _node_status(node):
        """
        Determine the real Kubernetes Ready status.
        """

        for condition in node.status.conditions or []:
            if condition.type == "Ready":
                if condition.status == "True":
                    return "Ready"
                return "NotReady"

        return "Unknown"

    @staticmethod
    def _pod_status(pod):
        """
        Determine a more useful pod status.

        Kubernetes Pod phase can be Running while a container is
        actually waiting because of CrashLoopBackOff, ImagePullBackOff,
        ErrImagePull, etc.

        Therefore we inspect container states first.
        """

        # ------------------------------------------------------------
        # Check init containers
        # ------------------------------------------------------------
        for container in pod.status.init_container_statuses or []:

            state = container.state

            if state and state.waiting:
                if state.waiting.reason:
                    return state.waiting.reason

            if state and state.terminated:
                if state.terminated.reason:
                    return state.terminated.reason

        # ------------------------------------------------------------
        # Check normal containers
        # ------------------------------------------------------------
        for container in pod.status.container_statuses or []:

            state = container.state

            if state and state.waiting:
                if state.waiting.reason:
                    return state.waiting.reason

            if state and state.terminated:
                if state.terminated.reason:
                    return state.terminated.reason

        # ------------------------------------------------------------
        # Fall back to Pod phase
        # ------------------------------------------------------------
        return pod.status.phase or "Unknown"

    @staticmethod
    def _pod_restarts(pod):
        """
        Calculate total container restart count.
        """

        restart_count = 0

        for container in pod.status.container_statuses or []:
            restart_count += container.restart_count or 0

        for container in pod.status.init_container_statuses or []:
            restart_count += container.restart_count or 0

        return restart_count

    # ================================================================
    # CONNECTION STATUS
    # ================================================================

    def health(self):
        """
        Return Kubernetes connection health.
        """

        if not self.available:
            return {
                "available": False,
                "message": "Kubernetes is not connected",
                "error": self._connection_error,
            }

        try:
            nodes = self.core.list_node(_request_timeout=5)

            return {
                "available": True,
                "message": "Kubernetes connection is healthy",
                "nodes": len(nodes.items),
            }

        except Exception as exc:
            return {
                "available": False,
                "message": "Kubernetes API request failed",
                "error": str(exc),
            }

    # ================================================================
    # NODES
    # ================================================================

    def nodes(self):
        """
        Return real Kubernetes nodes.

        Note:
        cpu/memory here represent Kubernetes capacity/allocatable
        information, NOT current utilization percentages.
        """

        self._ensure_available()

        node_list = self.core.list_node()

        output = []

        for node in node_list.items:

            capacity = node.status.capacity or {}
            allocatable = node.status.allocatable or {}

            output.append(
                {
                    "name": node.metadata.name,

                    "status": self._node_status(node),

                    "cpu": capacity.get("cpu", "-"),

                    "memory": capacity.get("memory", "-"),

                    "pods": capacity.get("pods", "-"),

                    "allocatable_cpu": allocatable.get(
                        "cpu",
                        "-"
                    ),

                    "allocatable_memory": allocatable.get(
                        "memory",
                        "-"
                    ),

                    "allocatable_pods": allocatable.get(
                        "pods",
                        "-"
                    ),

                    "labels": node.metadata.labels or {},

                    "creation_timestamp": (
                        node.metadata.creation_timestamp.isoformat()
                        if node.metadata.creation_timestamp
                        else None
                    ),
                }
            )

        return output

    # ================================================================
    # PODS
    # ================================================================

    def pods(self):
        """
        Return all real Kubernetes pods from all namespaces.
        """

        self._ensure_available()

        pod_list = self.core.list_pod_for_all_namespaces()

        output = []

        for pod in pod_list.items:

            restarts = self._pod_restarts(pod)

            status = self._pod_status(pod)

            ready_containers = 0
            total_containers = len(
                pod.status.container_statuses or []
            )

            for container in pod.status.container_statuses or []:
                if container.ready:
                    ready_containers += 1

            output.append(
                {
                    "name": pod.metadata.name,

                    "namespace": pod.metadata.namespace,

                    "status": status,

                    "phase": pod.status.phase or "Unknown",

                    "restarts": restarts,

                    "ready_containers": ready_containers,

                    "total_containers": total_containers,

                    "node": pod.spec.node_name,

                    "pod_ip": pod.status.pod_ip,

                    "host_ip": pod.status.host_ip,

                    "creation_timestamp": (
                        pod.metadata.creation_timestamp.isoformat()
                        if pod.metadata.creation_timestamp
                        else None
                    ),

                    "labels": pod.metadata.labels or {},
                }
            )

        return output

    # ================================================================
    # DEPLOYMENTS
    # ================================================================

    def deployments(self):
        """
        Return real Kubernetes deployments.
        """

        self._ensure_available()

        deployment_list = (
            self.apps.list_deployment_for_all_namespaces()
        )

        output = []

        for deployment in deployment_list.items:

            spec = deployment.spec
            status = deployment.status

            output.append(
                {
                    "name": deployment.metadata.name,

                    "namespace": deployment.metadata.namespace,

                    "desired": spec.replicas or 0,

                    "ready": status.ready_replicas or 0,

                    "available": status.available_replicas or 0,

                    "updated": status.updated_replicas or 0,

                    "unavailable": (
                        status.unavailable_replicas or 0
                    ),

                    "labels": deployment.metadata.labels or {},

                    "creation_timestamp": (
                        deployment.metadata.creation_timestamp.isoformat()
                        if deployment.metadata.creation_timestamp
                        else None
                    ),
                }
            )

        return output

    # ================================================================
    # SERVICES
    # ================================================================

    def services(self):
        """
        Return real Kubernetes services.
        """

        self._ensure_available()

        service_list = (
            self.core.list_service_for_all_namespaces()
        )

        output = []

        for service in service_list.items:

            ports = []

            for port in service.spec.ports or []:

                port_data = {
                    "name": port.name,
                    "port": port.port,
                    "target_port": str(port.target_port),
                    "protocol": port.protocol,
                    "node_port": port.node_port,
                }

                ports.append(port_data)

            output.append(
                {
                    "name": service.metadata.name,

                    "namespace": service.metadata.namespace,

                    "type": service.spec.type,

                    "cluster_ip": service.spec.cluster_ip,

                    "external_ips": (
                        service.spec.external_i_ps or []
                    ),

                    "ports": ports,

                    "selector": service.spec.selector or {},

                    "creation_timestamp": (
                        service.metadata.creation_timestamp.isoformat()
                        if service.metadata.creation_timestamp
                        else None
                    ),
                }
            )

        return output

    # ================================================================
    # NAMESPACES
    # ================================================================

    def namespaces(self):
        """
        Return real Kubernetes namespaces.
        """

        self._ensure_available()

        namespace_list = self.core.list_namespace()

        output = []

        for namespace in namespace_list.items:

            output.append(
                {
                    "name": namespace.metadata.name,

                    "status": (
                        namespace.status.phase
                        if namespace.status
                        else "Unknown"
                    ),

                    "creation_timestamp": (
                        namespace.metadata.creation_timestamp.isoformat()
                        if namespace.metadata.creation_timestamp
                        else None
                    ),

                    "labels": namespace.metadata.labels or {},
                }
            )

        return output

    # ================================================================
    # POD LOGS
    # ================================================================

    def pod_logs(
        self,
        namespace,
        pod,
        container=None
    ):
        """
        Return real logs from a Kubernetes pod.
        """

        self._ensure_available()

        kwargs = {
            "name": pod,
            "namespace": namespace,
            "tail_lines": 200,
        }

        if container:
            kwargs["container"] = container

        try:
            return self.core.read_namespaced_pod_log(
                **kwargs
            )

        except Exception as exc:
            return (
                f"Unable to retrieve logs for pod "
                f"'{pod}' in namespace '{namespace}': {exc}"
            )

    # ================================================================
    # EVENTS
    # ================================================================

    def events(self):
        """
        Return recent real Kubernetes events.
        """

        self._ensure_available()

        event_list = (
            self.core.list_event_for_all_namespaces()
        )

        events = []

        for event in event_list.items:

            timestamp = (
                event.last_timestamp
                or event.event_time
                or event.first_timestamp
            )

            events.append(
                {
                    "type": event.type or "Normal",

                    "reason": event.reason or "Unknown",

                    "object": (
                        event.involved_object.name
                        if event.involved_object
                        else "Unknown"
                    ),

                    "kind": (
                        event.involved_object.kind
                        if event.involved_object
                        else "Unknown"
                    ),

                    "namespace": (
                        event.involved_object.namespace
                        if event.involved_object
                        else None
                    ),

                    "message": event.message or "",

                    "count": event.count or 1,

                    "timestamp": (
                        timestamp.isoformat()
                        if timestamp
                        else None
                    ),
                }
            )

        # Newest events first
        events.sort(
            key=lambda x: x["timestamp"] or "",
            reverse=True
        )

        return events[:100]


# ================================================================
# GLOBAL SERVICE INSTANCE
# ================================================================

k8s = KubernetesService()