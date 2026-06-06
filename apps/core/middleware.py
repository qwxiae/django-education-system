import logging
import time
import uuid

logger = logging.getLogger(__name__)


class RequestLogMiddleware:
    """
    Logs every HTTP request + response with timing and optional user info.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = str(uuid.uuid4())[:8]
        request.request_id = request_id

        user = getattr(request, "user", None)

        logger.info(
            f"[START] id={request_id} "
            f"{request.method} {request.path} "
            f"user={user if user and user.is_authenticated else 'anon'}"
        )

        start_time = time.time()

        try:
            response = self.get_response(request)
        except Exception as e:
            logger.exception(
                f"[ERROR] id={request_id} "
                f"{request.method} {request.path} failed: {str(e)}"
            )
            raise

        duration = time.time() - start_time

        logger.info(
            f"[END] id={request_id} "
            f"{request.method} {request.path} "
            f"status={response.status_code} "
            f"time={duration:.3f}s"
        )

        return response
