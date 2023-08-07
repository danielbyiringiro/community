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