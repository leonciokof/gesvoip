#!/usr/bin/env python
import os
import sys

import dotenv

env_file = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')

if os.path.isfile(env_file):
    dotenv.read_dotenv(env_file)


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gesvoip_project.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
