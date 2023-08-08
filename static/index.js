function addComment(post_id, user_id) {
    const commentInput = document.getElementById(`comment-input-${post_id}`);
    const commentCount = document.getElementById(`comments-count-${post_id}`);
    const comment = commentInput.value;

    if (comment.trim() === '') 
    {
        return;
    }

    const commentData = {
        post_id: post_id,
        text: comment,
        user_id: user_id,
    };

    console.log(commentData);

    fetch('/addcomment', {
        method :'POST',
        headers : {
            'Content-Type': 'application/json',
        },

        body: JSON.stringify(commentData),
    })
    .then((res) => res.json())
    .then((data) => {

        if (data['success'] === true)
        {
            commentInput.value = '';
            commentCount.innerHTML = data['count'];
            const comment_text = data['text'];
            const comment_username = data['username'];
            const commentSection = document.getElementById(`comments-${post_id}`);
            const commentUsername = document.getElementById(`comments-username-${post_id}`);
            commentSection.innerHTML = comment_text;
            commentUsername.classList.add('comment-username');
            commentUsername.innerHTML = comment_username;
        }

    });


}

function most_recent(post_id)
{

    fetch('/comments', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({post_id: post_id}),
    })

    .then((res) => res.json())
    .then((data) => {

        if (data['success'] === true)
        {
            const comment_text = data['text'];
            const comment_username = data['username'];
            const commentSection = document.getElementById(`comments-${post_id}`);
            const commentUsername = document.getElementById(`comments-username-${post_id}`);
            commentSection.innerHTML = comment_text;
            commentUsername.classList.add('comment-username');
            commentUsername.innerHTML = comment_username;
        }

    });

}

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
        most_recent(post_id);
    });
}

document.addEventListener('DOMContentLoaded', initializeAllLikeStatus);

// Initialize like status when the page is fully loaded or reloaded
window.addEventListener('load', initializeAllLikeStatus);