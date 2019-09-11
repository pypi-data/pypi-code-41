from django.db import models
from django.template.defaultfilters import slugify
# Create your models here.


class Category(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField(editable=False)
    created_date = models.DateTimeField(verbose_name="Oluşturulma Tarihi", auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)

        super().save(*args, **kwargs)

class Post(models.Model):
    author = models.ForeignKey("auth.user", related_name="posts", on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name="posts", on_delete=models.CASCADE)

    title = models.CharField(max_length=50, verbose_name="Başlık")
    content = models.TextField(verbose_name="İçerik")
    created_date = models.DateTimeField(verbose_name="Oluşturulma Tarihi", auto_now_add=True)
    slug = models.SlugField(editable=False)
    image = models.ImageField(verbose_name="Image", null=True, blank=False)
    
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)

        super().save(*args, **kwargs)

class Comment(models.Model):
    author = models.ForeignKey("auth.user", related_name="comments", on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")

    content = models.TextField(verbose_name="İçerik")
    created_date = models.DateTimeField(verbose_name="Oluşturulma Tarihi", auto_now_add=True)

    def __str__(self):
        return self.content