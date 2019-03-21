import pulumi
conf = pulumi.Config('gke')
print(conf.require('name'))