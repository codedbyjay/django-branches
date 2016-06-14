def resource_owner(request):
    resolver = request.resolver_match
    owner = resolver.kwargs.get("owner", "")
    if owner:
        return {
            "owner": owner
        }
    return {}
