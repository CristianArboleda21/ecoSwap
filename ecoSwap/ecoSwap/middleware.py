from django.http import JsonResponse
from django.core.exceptions import RequestDataTooBig


class RequestSizeMiddleware:
    """
    Middleware para capturar errores de tamaño de petición excesivo
    y devolver una respuesta JSON amigable.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except RequestDataTooBig:
            return JsonResponse(
                {
                    "error": "El tamaño de la petición excede el límite permitido. Tamaño máximo: 15MB",
                    "status": 413
                },
                status=413
            )

    def process_exception(self, request, exception):
        """
        Captura excepciones no manejadas relacionadas con el tamaño de datos.
        """
        if isinstance(exception, RequestDataTooBig):
            return JsonResponse(
                {
                    "error": "El tamaño de la petición excede el límite permitido. Tamaño máximo: 15MB",
                    "status": 413
                },
                status=413
            )
        return None
