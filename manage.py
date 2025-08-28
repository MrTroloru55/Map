# map/manage.py
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'map.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()


#Как это используется?
#Вы никогда не меняете этот файл вручную. Вместо этого вы запускаете его из терминала для выполнения различных задач, например:
#    python manage.py runserver — запускает локальный веб-сервер для разработки.
#    python manage.py makemigrations — создает миграции для вашей базы данных.
#    python manage.py migrate — применяет миграции к базе данных.
#    python manage.py createsuperuser — создает учетную запись администратора.
#Таким образом, manage.py — это сердце взаимодействия с вашим Django-проектом через командную строку.