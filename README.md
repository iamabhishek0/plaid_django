# Plaid Django

## Redis

We are using Redis as our message broker for celery. Download [redis](https://redis.io/download) and extract the tar.gz file.

Open the folder and then in terminal run::

    $ make

    $ sudo make install

After that run the redis server::

    $ redis-server

## Celery

Use pip to install necessary dependency::

    $ pip install -r requirements.txt

Migrate the changes for celery results::

    $ python manage.py migrate django_celery_results

Now start the worker process

    $ celery -A plaid_django worker -l info

Now celery worker is running in background. You can call the tasks asynchronously. You can test this by running test_celery() in django shell::

    $ python manage.py shell

    >>> from plaid_link.tests import test_celery
    >>> test_celery()
