from locust import HttpUser, task, between, events
import time
import random
import string
import requests

DYNAMIC_IP = "http://35.223.245.38:8000"
post_ids = []

def save_user_credentials(username, password):
    with open("users.txt", "a") as file:
        file.write(f"{username},{password}\n")

def generate_random_string(length=9):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_random_tag():
    tags = ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"]
    return random.choice(tags)

def get_random_category():
    categories = ["Category1", "Category2", "Category3", "Category4", "Category5"]
    return random.choice(categories)

@events.request.add_listener
def normalize_request_name(request_type, name, response_time, response_length, **kwargs):
    if "/api/blogs/author/" in name:
        name = "/api/blogs/author/[id]/"

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("Test tamamlandı. Kullanıcı gönderileri kontrol ediliyor...")
    with open("users.txt", "r") as file:
        for line in file:
            username, password = line.strip().split(",")
            response = requests.post(
                    f"{DYNAMIC_IP}/api/token/",
                    json={"email": f"{username}@gmail.com", "password": password}
                )

            if response.status_code == 200:
                access_token = response.json()["access"]
                user_response = user_response = requests.get(
                        f"{DYNAMIC_IP}/api/user",
                        headers={"Authorization": f"Bearer {access_token}"}
                    )
                if user_response.status_code == 200:
                    user_id = user_response.json()["user"]["id"]
                    posts_response = requests.get(
                            f"{DYNAMIC_IP}/api/blogs/author/{user_id}/",
                            headers={"Authorization": f"Bearer {access_token}"}
                        )
                    if posts_response.status_code == 200:
                        posts = posts_response.json()
                        print(f"Kullanıcı {username} için {len(posts)} gönderi bulundu.")
                        for post in posts:
                            post_id = post["id"]
                            post_delete = requests.delete(
                                    f"{DYNAMIC_IP}/api/delete/{post_id}/",
                                    headers={"Authorization": f"Bearer {access_token}"}
                            )
                            if post_delete.status_code == 204:
                                print(f"Kullanıcı {username} için {post_id} numaralı gönderi silindi.")
                            else:
                                print(f"Kullanıcı {username} için {post_id} numaralı gönderi silinemedi.")
                    else:
                        print(f"Kullanıcı {username} gönderilerine erişilemedi.")
                else:
                    print(f"Kullanıcı {username} bilgilerine erişilemedi.")
            else:
                print(f"Kullanıcı {username} giriş yapamadı.")

        
class QuickstartUser(HttpUser):

    def on_start(self):
        self.username = generate_random_string()
        self.password = generate_random_string()

        self.client.post("/api/register", json={
            "first_name": "John",
            "last_name": "Doe",
            "username": self.username,
            "password": self.password,
            "email": f"{self.username}@gmail.com"
        })

        response = self.client.post("/api/token/", json={
            "email": f"{self.username}@gmail.com",
            "password": self.password
        })

        if response.status_code == 200:
            self.access_token = response.json()["access"]
            self.refresh_token = response.json()["refresh"]
            save_user_credentials(self.username, self.password)
            print("Login successful")
        else:
            self.access_token = None
            self.refresh_token = None
            print("Login failed")

    def view_random_post(self, post_id):
        post = self.client.get(f"/api/blog/{post_id}/", headers={"Authorization": f"Bearer {self.access_token}"})
        if post.status_code == 200:
            print(f"Post görüntülendi. Id: {post_id}")
            comments = self.client.get(f"/api/comments/{post_id}/", headers={"Authorization": f"Bearer {self.access_token}"})
            if comments.status_code == 200:
                print(f"Post Id: {post_id} için {len(comments.json())} yorum bulundu.")
        else:
            print("Post görüntüleme başarısız")

    @task
    def view_home_page(self):
        response = self.client.get("/api/blog", headers={"Authorization": f"Bearer {self.access_token}"})
        if response.status_code == 200:
            print("Viewed home page")
        else:
            print("Failed to view home page")
    
    @task
    def view_profile(self):
        response = self.client.get("/api/user", headers={"Authorization": f"Bearer {self.access_token}"})
        if response.status_code == 200:
            id = response.json()["user"]["id"]
            response = self.client.get(f"/api/blogs/author/{id}/",name="/api/blogs/author/[id]/")
            if response.status_code == 200:
                print("Viewed profile")
            else:
                print("Failed to view profile with id")
        else:
            print("Failed to view profile")

    @task
    def create_blog(self):
        response = self.client.get("/api/user", headers={"Authorization": f"Bearer {self.access_token}"})
        if response.status_code == 200:
            id = response.json()["user"]["id"]
            response = self.client.get(f"/api/blogs/author/{id}/",name="/api/blogs/author/[id]/")
            if response.status_code == 200:
                files = {
                    "image": ("/Users/erselcanakcili/Downloads/christmas-tree-8445553.jpg", open("/Users/erselcanakcili/Downloads/christmas-tree-8445553.jpg", "rb"), "image/jpg"),
                }
                data = {
                    "title": "Test Title",
                    "content": "Test Content",
                    "category": get_random_category(),
                    "tags": get_random_tag(),
                }
                response = self.client.post("/api/create", files=files, data=data, headers={"Authorization": f"Bearer {self.access_token}"})
                if response.status_code == 201:
                    print("Created blog")
                else:
                    print("Failed to create blog")
            else:
                print("Failed to get posts")
        else:
            print("Failed to get user")

    