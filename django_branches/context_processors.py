def page(request):
    return {
        "page": request.resolver_match.url_name
    }