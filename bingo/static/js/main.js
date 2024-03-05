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


document.addEventListener("DOMContentLoaded", function () {
    // Handling add_observation form
    handleFormSubmit('add_observation', "{% url 'add_observation' %}");
});
// Initialize Select2 for the creature dropdown
$('#creature').select2({
    placeholder: "Select a species",
    allowClear: true
});
$('#diver').select2({
    placeholder: "Select a diver",
    allowClear: true
});
// Set today's date as the default for date_observed
var today = new Date();
var dd = String(today.getDate()).padStart(2, '0');
var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
var yyyy = today.getFullYear();

today = yyyy + '-' + mm + '-' + dd;
document.getElementById('date_observed').value = today;
