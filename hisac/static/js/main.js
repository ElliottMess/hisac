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

function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// Common function to handle form submission
function handleFormSubmit(formId, url) {
    const form = document.getElementById(formId);
    const messageBox = document.getElementById('message-box');

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(this);

        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        })
            .then(response => {
                const status = response.status;
                return response.json().then(data => {
                    if (!response.ok) {
                        // If the response is an error, throw the data
                        throw { message: data.message, status };
                    }
                    return { data, status }; // For successful responses
                });
            })
            .then(({ data, status }) => {
                messageBox.innerText = data.message; // Display the success message
                messageBox.style.color = status === 200 ? 'green' : 'red';
            })
            .catch(error => {
                messageBox.innerText = error.message; // Display the custom error message
                messageBox.style.color = 'red';
            });
    });
}
