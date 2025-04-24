extension graphV1

resource localDevApplication 'Microsoft.Graph/applications@v1.0' = {
  displayName: 'Local identity'
  uniqueName: 'local-identity'
}

resource resourceSp 'Microsoft.Graph/servicePrincipals@v1.0' = {
  appId: localDevApplication.appId
}

output principalId string = resourceSp.id
