function like(post_id)
{
    const likeCount = document.getElementById(`vibes-count-${post_id}`);
    const likeImage = document.getElementById(`vibe-image-${post_id}`);

    fetch(`/liked/${post_id}`, {method: 'POST'})
        .then((res) => res.json())
        .then((data) => {
            likeCount.innerHTML = data['likes'];
            if (data['liked'] === false)
            {
                likeImage.src = "/static/vibed.jpeg";
            }
            else 
            {
                likeImage.src = "/static/vibe.png";
            }
        });  
}

function openPostEditor()
{
    const url = "/newpost";
    window.location.href = url;
}

function initializeLikeStatus(post_id) {
    const likeImage = document.getElementById(`vibe-image-${post_id}`);
    
    fetch(`/liked/${post_id}`, {method: 'POST'})
        .then((res) => res.json())
        .then((data) => {
            if (data['liked'] === false) {
                likeImage.src = "/static/vibed.jpeg";
            } else {
                likeImage.src = "/static/vibe.png";
            }
        });
}

function initializeAllLikeStatus() {
    const imgElements = document.querySelectorAll('.vibe-button img[data-post-id]');
    imgElements.forEach((imgElement) => {
        const post_id = imgElement.getAttribute('data-post-id');
        initializeLikeStatus(post_id);
    });
}

document.addEventListener('DOMContentLoaded', initializeAllLikeStatus);

// Initialize like status when the page is fully loaded or reloaded
window.addEventListener('load', initializeAllLikeStatus);