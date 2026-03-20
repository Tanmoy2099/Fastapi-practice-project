from fastapi import APIRouter

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/")
def get_all_posts():
    return {"message": "Get all posts"}


@router.post("/")
def create_post():
    return {"message": "Create post"}


@router.put("/{post_id}")
def update_post(post_id: str):
    return {"message": f"Update post {post_id}"}


@router.delete("/{post_id}")
def delete_post(post_id: str):
    return {"message": f"Delete post {post_id}"}
