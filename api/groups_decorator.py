from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from functools import wraps

def group_required(group_names):
    """
    Decorador para restringir el acceso a una vista solo a los usuarios que pertenezcan a uno o más grupos específicos.
    
    Args:
        group_names (str or list): Nombre del grupo o lista de nombres de grupos requeridos para acceder a la vista.
                                  El usuario debe pertenecer al menos a uno de los grupos especificados.
    
    Returns:
        function: Vista decorada que solo permite el acceso a usuarios autenticados y pertenecientes al menos a uno de los grupos indicados.
    
    Si el usuario no está autenticado o no pertenece a ninguno de los grupos, retorna un error 403 (Acceso denegado).
    
    Ejemplo de uso:
        @group_required('Admin')
        def vista_admin(request):
            pass
            
        @group_required(['Admin', 'Moderador'])
        def vista_admin_o_moderador(request):
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Convertir a lista si es un string
            if isinstance(group_names, str):
                groups_list = [group_names]
            else:
                groups_list = group_names
            
            # Verificar si el usuario pertenece al menos a uno de los grupos
            user_belongs_to_group = request.user.groups.filter(name__in=groups_list).exists()
            
            if not user_belongs_to_group:
                groups_str = ', '.join(groups_list)
                return HttpResponseForbidden(f"Acceso denegado. Se requiere pertenecer a uno de estos grupos: {groups_str}")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
