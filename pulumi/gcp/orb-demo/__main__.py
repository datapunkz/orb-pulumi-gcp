import pulumi
from pulumi_gcp import storage

from pulumi_gcp import compute

docker_image = 'ariv3ra/python-cicd-workshop'

disk = {
    'initializeParams': {
        'image': 'projects/cos-cloud/global/images/cos-stable-69-10895-62-0'
    }
}

meta_data = {"gce-container-declaration":"spec:\n  containers:\n    - name: test-docker\n      image: '" + docker_image +"'\n      stdin: false\n      tty: false\n  restartPolicy: Always\n"}

addr = compute.address.Address(resource_name='poc')
external_ip = addr.address

network = compute.Network("network")
network_interface = [
    {
        'network': network.id,
        'accessConfigs': [{'nat_ip': external_ip}],
    }
]

firewall = compute.Firewall("firewall", network=network.self_link, allows=[{
    'protocol': "tcp",
    'ports': ["22", "5000"]
}])

instance = compute.Instance('poc', name='poc', boot_disk=disk, machine_type='g1-small',
                            network_interfaces=network_interface, metadata=meta_data)

# Export the DNS name of the bucket
pulumi.export('instance_name', instance.name)
pulumi.export('instance_network', instance.network_interfaces)
pulumi.export('external_ip', addr.address)