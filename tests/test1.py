from locust import HttpUser, task, between, events
import time
import threading
import random
import string
import requests
from queue import Queue

DYNAMIC_IP = "34.71.158.112:8000"
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
        name = "/api/blogs/author/[user_id]/"
    elif "/api/delete/" in name:
        name = "/api/delete/[post_id]/"    
        
class QuickstartUser(HttpUser):
    wait_time = between(1, 5)
    def on_start(self):
        self.post_queue = Queue()
        self.username = generate_random_string()
        self.password = generate_random_string()

        response = self.client.post("/api/register", json={
            "first_name": "John",
            "last_name": "Doe",
            "username": self.username,
            "password": self.password,
            "email": f"{self.username}@gmail.com"
        })

        if response.status_code == 201:
            print("User created")
        else:
            self.stop()
            raise Exception(f"Register başarısız! Durum kodu: {response.status_code}")

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
            self.stop()
            raise Exception(f"Login başarısız! Durum kodu: {response.status_code}")
        threading.Thread(target=self.delete_posts_in_background, daemon=True).start()

    def on_stop(self):
        while not self.post_queue.empty():
            post_id = self.post_queue.get()
            response = self.client.delete(f"/api/delete/{post_id}/",name = "/api/delete/", headers={"Authorization": f"Bearer {self.access_token}"})
            if response.status_code == 204:
                print(f"Blog deleted with ID: {post_id} on stop")
            else:
                print(f"Failed to delete blog with ID: {post_id} on stop")

    def view_random_post(self, post_id):
        post = self.client.get(f"/api/blog/{post_id}/", headers={"Authorization": f"Bearer {self.access_token}"})
        if post.status_code == 200:
            print(f"Post görüntülendi. Id: {post_id}")
            comments = self.client.get(f"/api/comments/{post_id}/", headers={"Authorization": f"Bearer {self.access_token}"})
            if comments.status_code == 200:
                print(f"Post Id: {post_id} için {len(comments.json())} yorum bulundu.")
        else:
            print("Post görüntüleme başarısız")

    def delete_posts_in_background(self):
        while True:
            try:
                if not self.post_queue.empty():
                    time.sleep(2)
                    post_id = self.post_queue.get()
                    response = self.client.delete(f"/api/delete/{post_id}/",name = "/api/delete/", headers={"Authorization": f"Bearer {self.access_token}"})
                    if response.status_code == 204:
                        print(f"Blog deleted with ID: {post_id}")
                    else:
                        print(f"Failed to delete blog with ID: {post_id}")
                else:
                    time.sleep(3)
            except Exception as e:
                print(f"Error during deletion: {e}")
                break

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
                    post_id = response.json().get("id")
                    print(f"Blog created with ID: {post_id}")
                    self.post_queue.put(post_id)
                else:
                    print("Failed to create blog")
            else:
                print("Failed to get posts")
        else:
            print("Failed to get user")

    