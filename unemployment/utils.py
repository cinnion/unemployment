import json
import os
from django.conf import settings


def get_build_info():
    build_info_path = os.path.join(settings.BASE_DIR, 'build_info.json')
    if os.path.exists(build_info_path):
        with open(build_info_path, 'r') as f:
            return json.load(f)
    return {
        "BUILD_NUMBER": "N/A",
        "BUILD_ID": "N/A",
        "JOB_NAME": "N/A",
        "BUILD_URL": "N/A",
        "GIT_COMMIT": "N/A",
        "GIT_BRANCH": "N/A",
        "BUILD_DATE": "N/A",
    }
