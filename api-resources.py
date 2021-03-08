#!/usr/bin/env python3
import time
import requests
from kubernetes import client, config
from kubernetes.client import configuration
from pprint import pprint
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_kubeapi_request(path):
    response = s.get(host+path, headers=headers, verify=False)
    if response.ok:
        response.encoding = 'utf-8'
        return response.json()
    else:
        return 0

def get_resource_details(resource_path):
    resourceobjs = get_kubeapi_request(resource_path)
    if (resourceobjs == 0):
        return 0
    else:
        return resourceobjs["items"]


s = "Global"
host = "Global"
token = "Global"
headers = "Global"
namespaces_dict = "Global"
namespaces_dict = dict()

config.load_kube_config()
host = configuration.Configuration()._default.host
token = configuration.Configuration()._default.api_key['authorization']
headers = {"Accept": "application/json, */*", "Authorization": token}
s = requests.session()

# Get namespaces for iterating over namespaced resources
namespaces = get_kubeapi_request("/api/v1/namespaces")
namespaces_dict = namespaces["items"]

# Get Core V1 API resources
corev1resources = get_kubeapi_request("/api/v1")
for corev1resource in corev1resources["resources"]:
    if "/" not in corev1resource["name"]:
        if ( corev1resource["namespaced"] ):
            print ("====== Namespaced: v1/"+corev1resource["name"])
            for namespace in namespaces_dict:
                results = get_resource_details("/api/v1/namespaces/"+namespace["metadata"]["name"]+"/"+corev1resource["name"])
                if results:
                    for result in results:
                        if "ownerReferences" in result["metadata"].keys():
                            print(result["metadata"]["selfLink"]+" is owned by: ", end='')
                            for oRef in result["metadata"]["ownerReferences"]:
                                print (oRef["apiVersion"]+"/namespaces/"+namespace["metadata"]["name"]+"/"+oRef["kind"]+"/"+oRef["name"])
                        else:
                            print (result["metadata"]["selfLink"])
        else:
            print ("====== Non-Namespaced: v1/"+corev1resource["name"])
            results = get_resource_details("/api/v1/"+corev1resource["name"])
            if results:
                for result in results:
                        if "ownerReferences" in result["metadata"].keys():
                            print(result["metadata"]["selfLink"]+" is owned by: ", end='')
                            for oRef in result["metadata"]["ownerReferences"]:
                                print (oRef["apiVersion"]+"/"+oRef["kind"]+"/"+oRef["name"])
                        else:
                            print (result["metadata"]["selfLink"])

# Get other  API resources
apis = get_kubeapi_request("/apis/")
for api in apis["groups"]:
    versions = api["versions"]
    for version in versions:
        apisresources = get_kubeapi_request("/apis/"+version["groupVersion"])
        for apiresource in apisresources["resources"]:
            if "/" not in apiresource["name"]:
                if (apiresource["namespaced"]):
                    print ("====== Namespaced: "+version["groupVersion"]+"/"+apiresource["name"])
                    for namespace in namespaces_dict:
                        results = get_resource_details("/apis/"+version["groupVersion"]+"/namespaces/"+namespace["metadata"]["name"]+"/"+apiresource["name"])
                        if results:
                            for result in results:
                                if "ownerReferences" in result["metadata"].keys():
                                    print(result["metadata"]["selfLink"]+" is owned by: ", end='')
                                    for oRef in result["metadata"]["ownerReferences"]:
                                        print (oRef["apiVersion"]+"/namespaces/"+namespace["metadata"]["name"]+"/"+oRef["kind"]+"/"+oRef["name"])
                                else:
                                    print (result["metadata"]["selfLink"])
                else:
                    print ("====== Non-namespaced: "+version["groupVersion"]+"/"+apiresource["name"])
                    results = get_resource_details("/apis/"+version["groupVersion"]+"/"+apiresource["name"])
                    if results:
                        for result in results:
                            if "ownerReferences" in result["metadata"].keys():
                                print(result["metadata"]["selfLink"]+" is owned by: ", end='')
                                for oRef in result["metadata"]["ownerReferences"]:
                                    print (oRef["apiVersion"]+"/"+oRef["kind"]+"/"+oRef["name"])
                            else:
                                print (result["metadata"]["selfLink"])
