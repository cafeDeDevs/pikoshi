description = """
## Items

You can **read items**.

## Users

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).
"""

tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "items",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]

meta_info = {
    "contact": {
        "name": "Brian Hayes",
        "url": "https://brianhayes.dev",
        "email": "brianhayes.dev@protonmail.com",
    },
    "description": description,
    "openapi_tags": tags_metadata,
    "summary": "Pikoshi: The Photo Sharing Application With Privacy In Mind By Default 🐱",
    "terms_of_service": "https://example.com/terms/",
    "title": "Pikoshi",
    "version": "0.0.1",
}
