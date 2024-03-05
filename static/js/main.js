document.getElementById('add_observation').addEventListener('submit', function (e) {
    e.preventDefault();
    var data = new FormData(this);
    fetch("{% url 'add_observation' %}", {
        method: 'POST',
        body: data,
    })
        .then(response => response.json())
        .then(data => {
            // Display the success message
            alert(data.message);
        })
        .catch(error => console.error('Error:', error));
});

// Add the event listener to the add_diver form
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('add_diver').addEventListener('submit', function (e) {
        e.preventDefault();
        var data = new FormData(this);
        fetch("{% url 'add_diver' %}", {
            method: 'POST',
            body: data,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'error') {
                    document.getElementById('diver-form-error').innerText = data.message; // Display error message
                    document.getElementById('diver-form-success').innerText = ''; // Clear previous success message
                } else {
                    document.getElementById('diver-form-success').innerText = data.message; // Display success message
                    document.getElementById('diver-form-error').innerText = ''; // Clear previous error message
                    // Optionally, clear the form fields
                    document.getElementById('add_diver').reset();
                }
            })
            .catch(error => console.error('Error:', error));
    });
});
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
