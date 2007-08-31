#This is completely non-destructive and is only adding a few tables and columns to the WP database for use with Django.

#Clone wp_post2cat as wp_posts_categories to allow for Django ManyToMany relationship
CREATE TABLE wp_posts_categories LIKE wp_post2cat;
INSERT wp_posts_categories SELECT * FROM wp_post2cat;
#Clone wp_link2cat as wp_posts_categories to allow for Django ManyToMany relationship
CREATE TABLE wp_links_categories LIKE wp_link2cat;
INSERT wp_links_categories SELECT * FROM wp_link2cat;
#Clone category_parent column to allow for Django ForeignKey relationship
ALTER TABLE wp_categories ADD COLUMN django_parent_id BIGINT(20) AFTER category_parent;
INSERT INTO wp_categories (django_parent_id) SELECT category_parent FROM wp_categories;
#Clone post_parent column to allow for Django ForeignKey relationship
ALTER TABLE wp_posts ADD COLUMN django_parent_id BIGINT(20) AFTER post_parent;
UPDATE wp_posts SET django_parent_id = post_parent;