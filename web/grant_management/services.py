from web.grant_management.flows import GrantManagementFlow


def start_flow(grant_application):
    return GrantManagementFlow.start.run(grant_application=grant_application)
