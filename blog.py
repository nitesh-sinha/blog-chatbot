from dataclasses import dataclass


@dataclass
class Blog:
    blog_name: str
    blog_owner: str
    blog_url: str
    blog_contact: str
