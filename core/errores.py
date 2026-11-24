class ErrorNegocio(Exception):
    """Se lanza cuando una operación viola una regla de negocio.
    Las vistas mostrarán su mensaje al usuario."""