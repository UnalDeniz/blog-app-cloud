from django.db import models
from user_api.models import CustomUser

# Create your models here.
class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        abstract = True


class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class Tag(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name


class Blog(BaseModel):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=False)
    content = models.TextField(null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.title


class Comment(BaseModel):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField(null=False)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.blog.title}"
