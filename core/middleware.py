
from .utils import set_current_company, remove_current_company
from .models import Company

class TenantMiddleware:
    """
    Middleware that automatically selects the tenant based on the logged-in user.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'company'):
            set_current_company(request.user.company)
        else:
            # Handle cases where user is not logged in or doesn't have a company (e.g. superuser)
            # You might want to unset it to be safe
            remove_current_company()

        response = self.get_response(request)
        
        # Clean up thread locals
        remove_current_company()
        
        return response
