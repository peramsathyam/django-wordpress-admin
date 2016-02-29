For those looking to migrate their self-hosted Wordpress site to Django. This app will hook into the existing databases allowing management through Django's admin interface and easy migration to a Django site.

Built using `manage.py inspectdb` with some custom managers thrown in to separate out the different content that is all thrown into one big table (`wp_posts`).