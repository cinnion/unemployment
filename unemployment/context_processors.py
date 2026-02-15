from .utils import get_build_info


def build_info_processor(request):
    return {"BUILD_INFO": get_build_info()}
