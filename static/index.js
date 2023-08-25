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
    const bio = document.getElementById('changebio').value;

    fetch('/users/changebio', {
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
            window.location.href = '/users/' + data['username'];
        }
    })
    .catch(error => console.error('Error:', error));

}

function changeUsername()
{
    const username = document.getElementById('changeusername').value;

    fetch('/checkuser', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({username: username}),
    })
    .then(res => res.json())
    .then(data => {
        if (data['success'] === true)
        {
            fetch('/users/changeusername', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({username: username}),
            })
            .then(res => res.json())
            .then(data => {
                if (data['success'] === true)
                {
                    window.location.href = '/users/' + data['username'];
                }
            }
            )
            .catch(error => console.error('Error:', error));

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

function explore()
{
    window.location.href = '/explore';
}

function circle(id)
{
    fetch('/circle', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({id: id}),
    })
    .then(res => res.json())
    .then(data => {
        if (data['success'] === true)
        {
            const friend = document.getElementById(id);
            friend.style.display = "none";
        }
    });
}

function approve(id)
{
    fetch('/approve', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({id: id}),
    })
    .then(res => res.json())
    .then(data => {
        
        if (data['success'] === true)
        {
            const friend = document.getElementById(id);
            friend.style.display = "none";
        }
    });
}

function checkusername()
{
    const usernameInput = document.getElementById('username_register');
    const username = usernameInput.value;

    fetch('/checkuser', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({username: username}),
    })
    .then(res => res.json())
    .then(data => {

        if (data['success'] === false)
        {
            showAndHideAlert(data['message'], 3000);
            usernameInput.focus();
        }
    })
    .catch(error => console.error('Error:', error));
}

function checkchangeusername()
{
    const usernameInput = document.getElementById('changeusername');
    const username = usernameInput.value;

    fetch('/checkuser', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({username: username}),
    })
    .then(res => res.json())
    .then(data => {

        if (data['success'] === false)
        {

            showAndHideAlertYear(data['message'], 3000);
            usernameInput.focus();
        }
    })
    .catch(error => console.error('Error:', error));
}

function checkemail()
{
    const emailInput = document.getElementById('email');
    const email = emailInput.value;

    fetch('/checkemail', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({email: email}),
    })
    .then(res => res.json())
    .then(data => {

        if (data['success'] === false)
        {
            showAndHideAlert(data['message'], 3000);
            emailInput.focus();
        }
    })
    .catch(error => console.error('Error:', error));
}


function showAndHideAlert(message, timeout) 
{
    const alertElement = document.querySelector(".alert_register");
    alertElement.textContent = message;
    alertElement.style.display = "block";


    setTimeout(function () 
    {
        alertElement.style.display = "none";
    }, timeout);
}


function register()
{
    const username = document.getElementById('username_register').value;
    const email = document.getElementById('email').value;
    const name = document.getElementById('name').value;
    const status = document.getElementById('status').value;
    const profile_picture = document.getElementById('image_register').files[0];
    

    const formData = new FormData();
    formData.append('profile_picture', profile_picture);
    
    if (username === "" || email === "" || name === "" || status === "" || profile_picture === "")
    {
        showAndHideAlert("Please fill all the fields", 3000);
        return;
    }

    const user_details = 
    {
        username: username,
        email: email,
        name: name,
        status: status,
    }

    fetch('/registerj', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(user_details),
    })
    .then(res => res.json())
    .then(data => {
        if (data['success'] === true)
        {
            fetch('/upload', {
                method: 'POST',
                body: formData,
            })
            .then(res => res.json())
            .then(data => {
                if (data['success'] === true)
                {
                    user_details['profile_picture'] = data['image_id'];
                    console.log(user_details);
                    fetch('/record', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(user_details),
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data['success'] === true)
                        {
                            const email_details =
                            {
                                email: data['email'],
                                code : data['code'],

                            };

                            fetch('/send_email', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify(email_details),
                            })
                            .then(res => res.json())
                            .then(data => {
                                if (data['success'] === true)
                                {
                                    window.location.href = '/year';
                                }
                            })
                            
                        }
                        else
                        {
                            showAndHideAlert(data['message'], 3000);
                        }
                    })
                    .catch(error => console.error('Error:', error));
                }
                else
                {
                    showAndHideAlert(data['message'], 3000);
                }
            }
            )
            .catch(error => console.error('Error:', error));

        }
        else
        {
            showAndHideAlert(data['message'], 3000);
        }
    })
    .catch(error => console.error('Error:', error));

}

function checkOldPassword()
{
    const oldPasswordInput = document.getElementById('oldpassword');
    const oldPassword = oldPasswordInput.value;

    fetch('/checkoldpassword', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({oldPassword: oldPassword}),
    })
    .then(res => res.json())
    .then(data => {
            
        if (data['success'] === false)
        {
            showAndHideAlertYear(data['message'], 3000);
            oldPasswordInput.focus();
        }
    })
}

function passwordAnalyse(id)
{
    const passwordInput = document.getElementById(id);
    const password = passwordInput.value;

    if (password.length < 8)
    {
        showAndHideAlertYear('Password has to be at least 8 characters long', 2000);
        passwordInput.focus();

    }

    else if (!hasLowerCase(password))
    {
        showAndHideAlertYear('Password has to contain at least one lowercase letter', 2000);
        passwordInput.focus();
    }

    else if (!hasUpperCase(password))
    {
        showAndHideAlertYear('Password has to contain at least one uppercase letter', 2000);
        passwordInput.focus();
    }

    else if (!hasDigit(password))
    {
        showAndHideAlertYear('Password has to contain at least one number', 2000);
        passwordInput.focus();
    }
}

function hasLowerCase(str) {
    return /[a-z]/.test(str);
}

function hasUpperCase(str) {
    return /[A-Z]/.test(str);
}

function hasDigit(str) {
    return /\d/.test(str);
}

function passwordCompare(id,passid)
{
    const password = document.getElementById(passid).value;
    const confirmInput = document.getElementById(id);
    const confirm = confirmInput.value;

    if (password !== confirm)
    {
        showAndHideAlertYear("Passwords do not mach", 2000);
        return;
    }
}

function changepassword()
{
    const oldPasswordInput = document.getElementById('oldpassword');
    const oldPassword = oldPasswordInput.value;

    fetch('/checkoldpassword', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({oldPassword: oldPassword}),
    })
    .then(res => res.json())
    .then(data => {
            
        if (data['success'] === false)
        {
            showAndHideAlertYear(data['message'], 3000);
            oldPasswordInput.focus();
        }
        else
        {
            const newpassword = document.getElementById('newpassword').value;
            const newpasswordconfirm = document.getElementById('confirmnewpassword').value;

            if (newpassword !== newpasswordconfirm)
            {
                showAndHideAlertYear("Passwords do not mach", 2000);
                return;
            }

            fetch('/users/changepassword', {
                method : 'POST',
                headers : {
                    'Content-Type': 'application/json',
                },
                body : JSON.stringify({newpassword : newpassword}),
            })
            .then(res => res.json())
            .then(data => {
                if (data.success === true)
                {
                    window.location.href = '/users/' + data.username;
                }
            })

        }
    })
}

function showAndHideAlertYear(message, timeout) 
{
    const alertElement = document.querySelector(".alert_year");
    alertElement.textContent = message;
    alertElement.style.display = "block";

    setTimeout(function () 
    {
        alertElement.style.display = "none";
    }, timeout);
}

function codeCompare(regId)
{
    const codeInput = document.getElementById('code');
    const code = codeInput.value;

    fetch('/code_compare', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({code: code, regId: regId}),
    })
    .then(res => res.json())
    .then(data => {
    if (data['success'] === false)
        {
            showAndHideAlertYear(data['message'], 3000);
            codeInput.focus();
        }
    });
}

function year(regId)
{
    const code = document.getElementById('code').value;
    const password = document.getElementById('password').value;
    const confirm = document.getElementById('confirm').value;
    const major = document.getElementById('major').value;
    const year = document.getElementById('class').value;

    if (code === '' || password === '' || confirm === '' || major === '' || year === '' || regId === '')
    {
        showAndHideAlertYear("Please fill in all the fields", 3000);
        return;
    }

    const user_details =
    {
        code: code,
        password: password,
        confirm: confirm,
        major: major,
        year: year,
        id: regId,
    };

    fetch('/yearpost', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(user_details),
    })
    .then(res => res.json())
    .then(data => {
        if (data['success'] === true)
        {
            window.location.href = '/';
        }
        else
        {
            showAndHideAlertYear(data['message'], 3000);
        }
    })
}

function loginUsername()
{
    const usernameInput = document.getElementById('loginusername');
    const usename = usernameInput.value;

    if (usename === '')
    {
        showAndHideAlertYear("Please enter your username", 3000);
        return;
    }

    fetch('/login_username', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({username: usename}),
    })
    .then(res => res.json())
    .then(data => {data['success'] === false
        if (data['success'] === false)
        {
            showAndHideAlertYear(data['message'], 3000);
        }
    });
}

function loginall()
{
    const username = document.getElementById('loginusername').value;
    const passwordInput = document.getElementById('loginpassword');
    const password = passwordInput.value;

    if (password === '')
    {
        showAndHideAlertYear("Please fill in your password", 3000);
        passwordInput.focus();
        return;
    }

    const user_details =
    {
        username: username,
        password: password,
    };

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(user_details),
    })
    .then(res => res.json())
    .then(data => {
        if (data['success'] === true)
        {
            window.location.href = '/';
        }
        else
        {
            showAndHideAlertYear(data['message'], 3000);
        }
    })
}

function savegroup()
{
    const classg = document.getElementById('class').value;
    
    fetch('/users/changegroup', {
        method: 'POST',
        headers : {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({classg: classg}),
    })
    .then(res => res.json())
    .then(data => {

        if (data.success === true)
        {
            window.location.href = '/users/' + data.username;
        }
        else
        {
            showAndHideAlertYear(data.message, 3000);
        }
    })
}

function savemajor()
{
    const major = document.getElementById('major').value;
    
    fetch('/users/changemajor', {
        method: 'POST',
        headers : {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({major: major}),
    })
    .then(res => res.json())
    .then(data => {

        if (data.success === true)
        {
            window.location.href = '/users/' + data.username;
        }
        else
        {
            showAndHideAlertYear(data.message, 3000);
        }
    })
}

document.addEventListener('DOMContentLoaded',initializeAllLikeStatus);
document.addEventListener('DOMContentLoaded',checkIfPostsExist);

window.addEventListener('load', initializeAllLikeStatus);
window.addEventListener('load', checkIfPostsExist);

document.addEventListener('DOMContentLoaded', () => {
    const currentPath = window.location.pathname;
    if (currentPath.endsWith('year')) 
    { 
        showAndHideAlertYear("Check the code in your email", 4000);
    }
});
