import os
import pulumi
import pulumi_kubernetes
from pulumi import ResourceOptions
from pulumi_kubernetes.apps.v1 import Deployment
from pulumi_kubernetes.core.v1 import Namespace, Pod, Service
from pulumi_gcp import container

conf = pulumi.Config('gke')
gcp_conf = pulumi.Config('gcp')

stack_name = conf.require('name')
gcp_project = gcp_conf.require('project')
gcp_zone = gcp_conf.require('zone')

app_name = 'cicd-app'
app_label = {'appClass':app_name}
cluster_name = app_name

image_tag = ''
if 'CIRCLE_SHA1' in os.environ:
    image_tag = os.environ['CIRCLE_SHA1']
else:
    image_tag = 'latest'

docker_image = 'ariv3ra/orb-pulumi-gcp:{0}'.format(image_tag)

machine_type = 'g1-small'

cluster = container.Cluster(
    cluster_name,
    initial_node_count=3,
    min_master_version='latest',
    node_version='latest',
    node_config={
        'machine_type': machine_type,
        'oauth_scopes': [
            "https://www.googleapis.com/auth/compute",
            "https://www.googleapis.com/auth/devstorage.read_only",
            "https://www.googleapis.com/auth/logging.write",
            "https://www.googleapis.com/auth/monitoring",
        ],
    }
)

# Set the Kubeconfig file values here
def generate_k8_config(master_auth, endpoint, context):
    config = '''apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: {masterAuth}
    server: https://{endpoint}
  name: {context}
contexts:
- context:
    cluster: {context}
    user: {context}
  name: {context}
current-context: {context}
kind: Config
preferences: {prefs}
users:
- name: {context}
  user:
    auth-provider:
      config:
        cmd-args: config config-helper --format=json
        cmd-path: gcloud
        expiry-key: '{expToken}'
        token-key: '{tokenKey}'
      name: gcp
    '''.format(masterAuth=master_auth, context=context, endpoint=endpoint, 
            prefs='{}', expToken = '{.credential.token_expiry}', tokenKey='{.credential.access_token}')

    return config
    
gke_masterAuth = cluster.master_auth['clusterCaCertificate']
gke_endpoint = cluster.endpoint
gke_context = gcp_project+'_'+gcp_zone+'_'+cluster_name

k8s_config = pulumi.Output.all(gke_masterAuth,gke_endpoint,gke_context).apply(lambda args: generate_k8_config(*args))

cluster_provider = pulumi_kubernetes.Provider(cluster_name, kubeconfig=k8s_config)
ns = Namespace(cluster_name, __opts__=ResourceOptions(provider=cluster_provider))

gke_deployment = Deployment(
    app_name,
    metadata={
        'namespace': ns,
        'labels': app_label,
    },
    spec={
        'replicas': 3,
        'selector':{'matchLabels': app_label},
        'template':{
            'metadata':{'labels': app_label},
            'spec':{
                'containers':[
                    {
                        'name': app_name,
                        'image': docker_image,
                        'ports':[{'name': 'port-5000', 'container_port': 5000}]
                    }
                ]
            }
        }
    },
    __opts__=ResourceOptions(provider=cluster_provider)
)

deploy_name = gke_deployment

gke_service = Service(
    app_name,
    metadata={
        'namespace': ns,
        'labels': app_label,
    },
    spec={
        'type': "LoadBalancer",
        'ports': [{'port': 80, 'target_port': 5000}],
        'selector': app_label,
    },
    __opts__=ResourceOptions(provider=cluster_provider)
)

pulumi.export("kubeconfig", k8s_config)
pulumi.export("app_endpoint_ip", gke_service.status['load_balancer']['ingress'][0]['ip'])