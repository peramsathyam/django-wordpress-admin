1. Copy wordpress folder into your project (it is a standalone app)
2. Point your project's settings.py to your WordPress database.
3. Either rename or create a copy of the following tables to match the Django naming scheme
* rename wp_post2cat wp_posts_categories
* rename wp_link2cat wp_links_categories

NB: If you are working on a live copy of your database, renaming the tables will break your WordPress install.

Here is a sample MySQL command to rename a database:
ALTER TABLE `my_wp_db`.`wp_post2cat` RENAME TO `my_wp_db`.`wp_posts_catories`;
