from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    # Llama al manejador de excepciones predeterminado de DRF
    response = exception_handler(exc, context)

    # Si existe una respuesta (es decir, un error manejado por DRF)
    if response is not None:
        # Reestructura la salida para devolver solo un mensaje
        errors = response.data
        # Verifica si hay un solo mensaje de error
        if isinstance(errors, dict):
            first_error = list(errors.values())[0]
            response.data = {
                "message": first_error[0] if isinstance(first_error, list) else first_error
            }
    return response
