  1. Copy wordpress folder into your project (it is a standalone app)
  1. Point your project's settings.py to your WordPress database and add wordpress to your installed app list.
  1. If your wordpress database prefix is not the default, `wp_`, you can set it in your project settings by using `WORDPRESS_TABLE_PREFIX = u'mywpprefix_'`
  1. `manage.py syncdb`