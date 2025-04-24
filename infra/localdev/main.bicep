module user 'local-identity.bicep' = {
  name: 'local-identity'
}

module cognitiveServicesOpenAiUser 'role.bicep' = {
  name: 'local-identity-role'
  params: {
    principalId: user.outputs.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
  }
}

module mlServiceRoleDataScientist 'role.bicep' = {
  name: 'ml-service-role-data-scientist'
  params: {
    principalId: user.outputs.principalId
    roleDefinitionId: 'f6c7c914-8db3-469d-8ca1-694a8f32e121'
    principalType: 'ServicePrincipal'
  }
}

module mlServiceRoleSecretsReader 'role.bicep' = {
  name: 'ml-service-role-secrets-reader'
  params: {
    principalId: user.outputs.principalId
    roleDefinitionId: 'ea01e6af-a1c1-4350-9563-ad00f8c72ec5'
    principalType: 'ServicePrincipal'
  }
}

module monitorReader 'role.bicep' = {
  name: 'monitor-reader'
  params: {
    principalId: user.outputs.principalId
    roleDefinitionId: '43d0d8ad-25c7-4714-9337-8ba259a9fe05'
    principalType: 'ServicePrincipal'
  }
}

module monitorPublisher 'role.bicep' = {
  name: 'monitor-publisher'
  params: {
    principalId: user.outputs.principalId
    roleDefinitionId: '3913510d-42f4-4e42-8a64-420c390055eb'
    principalType: 'ServicePrincipal'
  }
}

module searchIndexContributor 'role.bicep' = {
  name: 'search-index-contributor'
  params: {
    principalId: user.outputs.principalId
    roleDefinitionId: '8ebe5a00-799e-43f5-93ac-243d3dce84a7'
    principalType: 'ServicePrincipal'
  }
}

module servicebusSender 'role.bicep' = {
  name: 'servicebus-sender'
  params: {
    principalId: user.outputs.principalId
    roleDefinitionId: '69a216fc-b8fb-44d8-bc22-1f3c2cd27a39'
    principalType: 'ServicePrincipal'
  }
}
