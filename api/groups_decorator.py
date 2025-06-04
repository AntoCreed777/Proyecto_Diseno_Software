from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

def group_required(group_name):
    """
    Decorador para restringir el acceso a una vista solo a los usuarios que pertenezcan a un grupo específico.
    
    Args:
        group_name (str): Nombre del grupo requerido para acceder a la vista.
    
    Returns:
        function: Vista decorada que solo permite el acceso a usuarios autenticados y pertenecientes al grupo indicado.
    
    Si el usuario no está autenticado o no pertenece al grupo, retorna un error 403 (Acceso denegado).
    
    Ejemplo de uso:
        @group_required('Admin')
        def vista_admin(request):
            pass
    """
    def decorator(view_func):
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.groups.filter(name=group_name).exists():
                return HttpResponseForbidden("Acceso denegado.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
