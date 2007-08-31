from django.db import models
import urllib2
from django.conf import settings

WP_PREFIX = getattr(settings, 'WORDPRESS_TABLE_PREFIX', u'wp_')


class Category(models.Model):
    cat_id = models.AutoField("ID", primary_key=True)
    cat_name = models.CharField("Name", max_length=165)
    category_nicename = models.SlugField("Slug", prepopulate_from=("cat_name",))
    category_parent = models.ForeignKey("self", verbose_name="Category parent", blank=True, db_column='category_parent')
    category_description = models.TextField("Description", blank=True)
 
    category_count = models.IntegerField(default=0, editable=False)
    link_count = models.IntegerField(default=0, editable=False)
    posts_private = models.IntegerField(default=0, editable=False)
    links_private = models.IntegerField(default=0, editable=False)

    class Meta:
        db_table = u'%scategories' % WP_PREFIX
        verbose_name_plural = 'Categories'

    class Admin:
        list_display = ('cat_id', 'cat_name', 'category_description')

    def __unicode__(self):
        return self.cat_name
    
    def save(self):
        super(Category, self).save()

TARGET_CHOICES = (
    ('', 'none'),
    ('_blank', '_blank'),
    ('_top', '_top'),
)
YES_NO_CHOICE = (
    ('Y', 'Yes'),
    ('N', 'No'),
)
class Link(models.Model):
    link_id = models.AutoField(primary_key=True)
    link_name = models.CharField("Name", max_length=255)
    link_url = models.CharField("Address", max_length=255)
    link_description = models.CharField("Description", blank=True, max_length=255)
    categories = models.ManyToManyField(Category, db_table=u'%slink2cat' % WP_PREFIX, filter_interface=models.HORIZONTAL)
    link_target = models.CharField("Target", choices=TARGET_CHOICES, max_length=75)
    link_visible = models.CharField(max_length=3, choices=YES_NO_CHOICE, default='Y') 
    link_rel = models.CharField("rel", help_text="Link Relationship (XFN)", blank=True, max_length=255)
    #Advanced
    link_image = models.CharField(max_length=255, blank=True)
    link_owner = models.IntegerField(blank=True)
    link_rating = models.IntegerField(blank=True)
    link_updated = models.DateTimeField(auto_now=True)
    link_notes = models.TextField(blank=True)
    link_rss = models.URLField(max_length=255, blank=True)

    class Meta:
        db_table = u'%slinks' % WP_PREFIX
 
    class Admin:
        list_display = ('link_name', 'link_url')
        #TODO add advanced fieldset
        
    def __unicode__(self):
        return self.link_name

        
class WordpressOption(models.Model):
    option_id = models.AutoField(primary_key=True)
    blog_id = models.IntegerField() #TODO change to ForeignKey
    option_name = models.CharField(max_length=192)
    option_can_override = models.CharField(max_length=3)
    option_type = models.IntegerField()
    option_value = models.TextField()
    option_width = models.IntegerField()
    option_height = models.IntegerField()
    option_description = models.TextField()
    option_admin_level = models.IntegerField()
    autoload = models.CharField(max_length=9)

    class Meta:
        db_table = u'%soptions' % WP_PREFIX
        ordering = ['option_name',]

    class Admin:
        list_display = ('option_name', 'option_value', 'option_description',)
        list_filter = ('option_can_override', 'autoload')
        search_fields = ('option_name', 'option_description',)
 
    def __unicode__(self):
        return self.option_name


STATUS_CHOICES = (
    ('open', 'Open'),
    ('closed', 'Closed')
)
POST_CHOICES = (
    ('publish', 'Published'),
    ('draft', 'Draft'),
    ('private', 'Private'),
    ('inherit', 'Inherit'),
)
TYPE_CHOICES = (
    ('post', 'Post'),
    ('page', 'Page'),
    ('attachment', 'File'),
)
class PostManager(models.Manager):
    def get_query_set(self):
        return super(PostManager, self).get_query_set().filter(post_type__exact='post')


class Post(models.Model):
    objects = PostManager()
    id = models.AutoField(primary_key=True)
    post_title = models.CharField("Title", max_length=255)
    post_content = models.TextField("Post")
    categories = models.ManyToManyField(Category, db_table=u'%spost2cat' % WP_PREFIX, filter_interface=models.HORIZONTAL)
    #Discussion
    comment_status = models.CharField(choices=STATUS_CHOICES,max_length=45)
    ping_status = models.CharField(choices=STATUS_CHOICES,max_length=18)
    post_password = models.CharField(max_length=60)
    post_name = models.SlugField("Post Slug", prepopulate_from=("post_title",))
    post_status = models.CharField(choices=POST_CHOICES, max_length=30)
    post_date = models.DateTimeField("Post Timestamp", auto_now_add=True)
    post_excerpt = models.TextField("Optional Excerpt")
    to_ping = models.TextField("Send trackbacks to", help_text="Separate multiple URLs with spaces")
    #Not used by posts
    post_date_gmt = models.DateTimeField(auto_now_add=True)
    post_category = models.IntegerField(blank=True, editable=False)
    pinged = models.TextField(blank=True, editable=False)
    post_modified = models.DateTimeField(auto_now=True, editable=False)
    post_modified_gmt = models.DateTimeField(auto_now=True, editable=False)
    post_content_filtered = models.TextField(blank=True, editable=False)
    post_parent = models.IntegerField(default=0, editable=False)
    guid = models.CharField(max_length=255, blank=True, editable=False) 
    menu_order = models.IntegerField(blank=True, editable=False)
    post_type = models.CharField(choices=TYPE_CHOICES, max_length=60, editable=False)
    post_mime_type = models.CharField(max_length=255, editable=False)
    comment_count = models.IntegerField(default=0, editable=False)

    class Meta:
        db_table = u'%sposts' % WP_PREFIX
        ordering = ['-post_date',]

    class Admin:
        manager = PostManager()
        list_display = ('post_title', 'post_date', 'post_categories', 'post_status')
        list_filter = ('post_status', 'categories', 'comment_status', 'ping_status')
        search_fields = ('post_title', 'post_content')
#        date_hierarchy = 'post_date'  #Fails when date is null

    def post_categories(self):
        cat_string = ''
        for c in self.categories.all():
            link = '<a href="./?categories__cat_id__exact=%s" title="Show all posts in %s category">%s</a>' % (c.cat_id, c.cat_name, c.cat_name)
            cat_string = ''.join([cat_string, link, ', '])
        return cat_string.rstrip(', ')
    post_categories.short_description = 'Categories'
    post_categories.allow_tags = True
            
    def __unicode__(self):
        return self.post_title
        
    def save(self):
        self.post_type = 'post'
        super(Page, self).save()
        
        
class PageManager(models.Manager):
    def get_query_set(self):
        return super(PageManager, self).get_query_set().filter(post_type='page')


class Page(models.Model):
    objects = PageManager()
    id = models.AutoField(primary_key=True)
    post_title = models.CharField("Title", blank=True, max_length=255)
    post_content = models.TextField("Page Content")
    comment_status = models.CharField(choices=STATUS_CHOICES,max_length=45)
    ping_status = models.CharField(choices=STATUS_CHOICES,max_length=18)
    post_status = models.CharField("Page Status", choices=POST_CHOICES, max_length=30)
    post_password = models.CharField("Page Password", blank=True, max_length=60)
    post_parent = models.ForeignKey("self", blank=True, db_column='post_parent', related_name="Child")
    post_name = models.SlugField("Page Slug", prepopulate_from=("post_title",))
    post_author = models.IntegerField("Page Author", default=1)
    menu_order = models.IntegerField("Page Order", default=0)
    #unused fields for pages
    to_ping = models.TextField(editable=False, blank=True)
    post_date = models.DateTimeField(editable=False, auto_now_add=True)
    pinged = models.TextField(editable=False, blank=True)
    post_modified = models.DateTimeField(editable=False, auto_now=True)
    post_modified_gmt = models.DateTimeField(editable=False, auto_now=True)
    post_content_filtered = models.TextField(editable=False, blank=True)
    post_excerpt = models.TextField(editable=False, blank=True)
    guid = models.CharField(editable=False, max_length=255, blank=True)
    post_type = models.CharField(editable=False, choices=TYPE_CHOICES, max_length=60)
    post_mime_type = models.CharField(editable=False, max_length=255, blank=True)
    comment_count = models.IntegerField(editable=False, default=0)
    post_date_gmt = models.DateTimeField(editable=False, auto_now_add=True)
    post_category = models.IntegerField(editable=False, blank=True)
        
    class Meta:
        db_table = u'%sposts' % WP_PREFIX
        ordering = ['post_parent', 'menu_order', 'post_date', 'post_title']

    class Admin:
        manager = PageManager()
        list_display = ('__unicode__', 'post_date', 'post_status')
        list_filter = ('post_status',)
        search_fields = ('post_title', 'post_content')

    def __unicode__(self):
        if self.post_parent:
            return '%s :: %s' % (self.post_parent.post_title, self.post_title)
        else:
            return self.post_title

    def save(self):
        self.post_type = 'page'
        super(Page, self).save()


class UploadManager(models.Manager):
    def get_query_set(self):
        return super(UploadManager, self).get_query_set().filter(post_type='attachment')


class Upload(models.Model):
    id = models.AutoField(primary_key=True)
    guid = models.FileField("File", upload_to='uploads', core=True)
    post_title = models.CharField("Title", blank=True, max_length=255)
    post_content = models.TextField("Description", blank=True)
    #Don't know of a good way to have uploads link to Posts and Pages, so I just chose Posts
    post_parent = models.ForeignKey(Post, verbose_name="Associated Post", edit_inline=True, db_column='post_parent')
    #Not used for file uploads    
    post_date = models.DateTimeField(auto_now_add=True, editable=False)
    post_date_gmt = models.DateTimeField(auto_now_add=True, editable=False)
    post_author = models.IntegerField(default=1, editable=False)
    post_category = models.IntegerField(default=0, editable=False)
    post_excerpt = models.TextField(blank=True, editable=False)
    post_name = models.SlugField("Slug", prepopulate_from=('post_title',), editable=False)
    to_ping = models.TextField(blank=True, editable=False)
    pinged = models.TextField(blank=True, editable=False)
    post_modified = models.DateTimeField(auto_now=True, editable=False)
    post_modified_gmt = models.DateTimeField(auto_now=True, editable=False)
    post_content_filtered = models.TextField(blank=True, editable=False)
    menu_order = models.IntegerField(default=0, editable=False)
    post_type = models.CharField(choices=TYPE_CHOICES, max_length=60, editable=False)
    post_mime_type = models.CharField(max_length=255, editable=False)
    comment_count = models.IntegerField(blank=True, editable=False)
    objects = UploadManager()
    class Meta:
        db_table = u'%sposts' % WP_PREFIX
        ordering = ['post_date',]
    class Admin:
        manager = UploadManager()
        list_display = ('post_title', 'post_parent', 'post_mime_type', 'post_date', 'post_content',)
        list_filter = ('post_mime_type',)
    def __unicode__(self):
        return self.post_title
    def save(self):
        try:    #TODO clean this up and handle errors gracefully
            info = urllib2.urlopen(field_data).info()
            self.post_mime_type = info['content-type']
        except: #couldn't determine file mime type
            pass 
        self.post_type = 'attachment'
        super(Upload, self).save()

class PostMeta(models.Model):
    meta_id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, edit_inline=True)
    meta_key = models.CharField(max_length=255, blank=True, core=True)
    meta_value = models.TextField(blank=True)
 
    class Meta:
        db_table = u'wp_postmeta'
        verbose_name = 'Custom Field'

    def __unicode__(self):
        return self.post.post_title

class PageMeta(models.Model):
    meta_id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Page, edit_inline=True)
    meta_key = models.CharField(max_length=255, blank=True, core=True)
    meta_value = models.TextField(blank=True)

    class Meta:
        db_table = u'%spostmeta' % WP_PREFIX
        verbose_name = 'Custom Field'

    def __unicode__(self):
        return self.post.post_title


APPROVED_CHOICES = (
    ('0', 'No'),
    ('1', 'Yes'),
    ('spam', 'Spam'),
)
class WordpressComment(models.Model):
    '''You probably would not want to use this model for new comments coming into your Django site. There are much better alternatives. It is just here to preserve the old comments'''
    comment_id = models.AutoField(primary_key=True)
    comment_post = models.ForeignKey(Post)
    comment_author = models.TextField()
    comment_author_email = models.CharField(max_length=255)
    comment_author_url = models.URLField(verify_exists=False)
    comment_author_ip = models.IPAddressField(max_length=255)
    comment_date = models.DateTimeField()
    comment_date_gmt = models.DateTimeField()
    comment_content = models.TextField()
    comment_karma = models.IntegerField()
    comment_approved = models.CharField(choices = APPROVED_CHOICES, max_length=12)
    comment_agent = models.CharField(max_length=255)
    comment_type = models.CharField(max_length=60)
    comment_parent = models.IntegerField() #TODO change to ForeignKey
    user_id = models.IntegerField()

    class Meta:
        db_table = u'%scomments' % WP_PREFIX
        ordering = ['-comment_date', 'comment_post']

    class Admin:
        list_display= ('edit', 'author', 'comment_post', 'comment_date')
        list_filter = ('comment_approved', 'comment_type')

    def author(self):
        if self.comment_author_url:
            link = '<a href="%s">%s</a>' % (self.comment_author_url, self.comment_author_url)
        else:
            link = '<a href="%s">%s</a>' % (self.comment_author_email, self.comment_author_email)
        return '%s | %s | IP: <a href="http://ws.arin.net/cgi-bin/whois.pl?queryinput=%s">%s</a>' % (self.comment_author, link, self.comment_author_ip, self.comment_author_ip)
    author.allow_tags = True
    
    def edit(self):
        return 'Edit'
        
    def __unicode__(self):
        return 'Comment on %s' % (self.comment_post.post_title,)
        

class WordpressUser(models.Model):
    id = models.AutoField(primary_key=True)
    user_login = models.CharField(max_length=180)
    user_pass = models.CharField(max_length=192)
    user_nicename = models.CharField(max_length=150)
    user_email = models.CharField(max_length=255)
    user_url = models.CharField(max_length=255)
    user_registered = models.DateTimeField(auto_now_add=True)
    user_activation_key = models.CharField(max_length=180)
    user_status = models.IntegerField()
    display_name = models.CharField(max_length=255)

    class Meta:
        db_table = u'%susers' % WP_PREFIX
        
        
class UserMeta(models.Model):
    umeta_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(WordpressUser)
    meta_key = models.CharField(max_length=255, blank=True)
    meta_value = models.TextField(blank=True)

    class Meta:
        db_table = u'%susermeta' % WP_PREFIX