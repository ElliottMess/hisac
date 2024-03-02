// Table tabs
$(document).ready(function () {
    $('.tab').click(function () {
        var period = $(this).data('period');
        var urlTopDivers = $('.tabs').data('url-top-divers'); // Get the URL from the data attribute
        // Remove 'active' class from all tabs, then add it to the clicked tab
        $('.tab').removeClass('active');
        $(this).addClass('active');

        // AJAX request to update the content
        $.ajax({
            url: urlTopDivers,
            type: 'get',
            data: { period: period },
            success: function (response) {
                $('#top-divers-container').html(response);
            }
        });
    });
    $('.tab[data-period="month"]').click();

});


function handleFormSubmit(formId, postUrl) {
    const form = document.getElementById(formId);
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        fetch(postUrl, {
            method: 'POST',
            body: formData,
            headers: {'X-CSRFToken': getCookie('csrftoken')}, // Ensure CSRF token is sent
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('message-box').innerText = data.message;
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('message-box').innerText = 'Failed to add diver.';
        });
    });
}

// Function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
