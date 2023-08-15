var commentsLoaded = false; 

function loadComments(post_id)
{
    var commentsDiv = document.getElementById(`display-comments-${post_id}`);
    const commentSection = document.getElementById(`comments-${post_id}`);
    const commentUsername = document.getElementById(`comments-username-${post_id}`);

    if (commentsLoaded) { 
        commentsDiv.innerHTML = '';
        commentsDiv.classList.remove("displayCommentss");
        commentSection.classList.remove('disapear');
        commentUsername.classList.remove('disapear');
        commentsLoaded = false;
        return;
    }

    fetch("/loadcomments", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({post_id: post_id}),
    })
    .then((res) => res.json())
    .then((data) => {
        if (data['success'] === true)
        {
            var comments = data['comments'];
            commentSection.classList.add('disapear');
            commentUsername.classList.add('disapear');
            commentsDiv.classList.add("displayComments");

            for (var i = 0; i < comments.length; i++)
            {
                var comment = comments[i];

                var commentDiv = document.createElement('div');
                var commentdiv_text = document.createElement('div');
                var commentdiv_details = document.createElement('div');
                var commentdiv_user_details = document.createElement('div');
                var commentdiv_user_username = document.createElement('div');
                var commentdiv_user_otherdetails = document.createElement('div');
                commentDiv.classList.add('comment_div');
                commentdiv_text.classList.add('comment_text');
                commentdiv_details.classList.add('comment_details');


                var textElement = document.createElement('p');
                textElement.textContent = comment['text'];

                var usernameElement = document.createElement('p');
                usernameElement.textContent = comment['username'];

                var pictureElement = document.createElement('img');
                pictureElement.src = comment['picture'];
                pictureElement.alt = comment['username'];
                pictureElement.classList.add('comment_picture');

                var timeElement = document.createElement('p');
                timeElement.textContent = comment['time'];

                var classgroupElement = document.createElement('p');
                classgroupElement.textContent = comment['class'];

                var majorElement = document.createElement('p');
                majorElement.textContent = comment['major'];
                commentdiv_user_username.appendChild(usernameElement);
                commentdiv_user_username.classList.add('comment_username');
                commentdiv_user_otherdetails.appendChild(classgroupElement);
                commentdiv_user_otherdetails.appendChild(majorElement);
                commentdiv_user_otherdetails.appendChild(timeElement);
                commentdiv_user_otherdetails.classList.add('other_details');
                commentdiv_user_details.appendChild(commentdiv_user_username);
                commentdiv_user_details.appendChild(commentdiv_user_otherdetails);
                commentdiv_details.appendChild(pictureElement);
                commentdiv_details.appendChild(commentdiv_user_details);
                commentdiv_text.appendChild(textElement);
                
                commentDiv.appendChild(commentdiv_details);
                commentDiv.appendChild(commentdiv_text);

                commentsDiv.appendChild(commentDiv);
            }

            commentsLoaded = true;
        }});
}

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

var queryexecuted = false;

function searchquery()
{
    var inputElement = document.querySelector('.search-input');
    var query = inputElement.value;
    var resultsDiv = document.getElementById('search-results');
    var resultsContainer = document.getElementById('search-results');

    if (query === '' || query === null)
    {
        resultsDiv.innerHTML = '';
        return;
    }

    if (queryexecuted === true)
    {
        resultsDiv.innerHTML = '';
    }

    // Send a fetch request to the Flask server
    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({query: query}),
    })
    .then(res => res.json())
    .then(data => {

        if (data['success'] === true)
        {
            resultsContainer = document.getElementById('search-results');
            if (query.length > 0) {
                resultsContainer.style.display = 'block';
                resultsContainer.style.top = inputElement.offsetTop + inputElement.offsetHeight + 'px';
                resultsContainer.style.left = inputElement.offsetLeft + 'px';
                
            } 
            else 
            {
                resultsContainer.style.display = 'none';
            }
            var data = data['results'];

            var ul = document.createElement('ul');
            ul.className = 'list-group';

            data.forEach(result => {
                var li = document.createElement('li');
                li.className = 'list-group-item';
                var full_name = result['fullname'];
                var username = result['username'];
                li.innerHTML = "<div><div>" + full_name + "</div>" + "<div><a href='/users/" + username + "'>" + "@" + "<strong>" + username + "</strong>" + "</a></div></div>";
                li.classList.add('block');
                ul.appendChild(li);
            });

            resultsContainer.appendChild(ul);
            queryexecuted = true;
        }
        else
        {
            resultsContainer.classList.add('no-results');
            resultsContainer.textContent = 'No results found';
        }
    })
    .catch(error => console.error('Error:', error));
    
}

function toggleDropdown(image) 
{
    // Toggle the display of the dropdown content
    var dropdownContent = image.nextElementSibling;
    dropdownContent.style.display = (dropdownContent.style.display === "block") ? "none" : "block";
}
  
function deletePost(post_id) 
{
    
    var confirmDelete = confirm("Are you sure you want to delete this post?");
    if (confirmDelete) 
    {
        fetch(`/deletepost/${post_id}`, {method: 'POST'})
        .then((res) => res.json())
        .then((data) => {
            if (data['success'] === true) 
            {
                if (data['length'] === 0)
                {
                    const div_class = document.querySelector(".p_container.personal_activity");
                    div_class.style.display = "none";
                    return;
                }
                window.location.reload();
            }
        });

    }
}

function checkIfPostsExist()
{
    const div_class = document.querySelector(".p_container.personal_activity");
    if (div_class === null)
    {
        return;
    }
    const length = div_class.children.length;
    if (length === 0)
    {
        div_class.style.display = "none";
    }
}

function editBio()
{
    const editBioInput = document.querySelector('.bio.disapear');
    const editBioButton = document.querySelector('.edit');
    editBioInput.classList.remove('disapear');
    editBioButton.classList.add('disapear');
}

function Bio()
{
    const bio = document.getElementById('bioinput').value;

    fetch('/bio', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({bio: bio}),
    })
    .then(res => res.json())
    .then(data => {
        if (data['success'] === true)
        {
            const bio = document.getElementById('bio');
            bio.innerHTML = data['bio'];
            const editBioInput = document.querySelector('.bio');
            const editBioButton = document.querySelector('.edit.disapear');
            editBioInput.classList.add('disapear');
            editBioButton.classList.remove('disapear');
        }
    })
    .catch(error => console.error('Error:', error));

}

function redirectOption(selectElement) 
{
    var selectedValue = selectElement.value;
    if (selectedValue) 
    {
        window.location.href = selectedValue;
    }
}

document.addEventListener('DOMContentLoaded',initializeAllLikeStatus);
document.addEventListener('DOMContentLoaded',checkIfPostsExist);
// Initialize like status when the page is fully loaded or reloaded
window.addEventListener('load', initializeAllLikeStatus);
window.addEventListener('load', checkIfPostsExist);