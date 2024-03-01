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

// Sidebar toggle
// $(document).ready(function toggleSidebar() {
//     var sidebar = document.getElementById("sidebar");
//     if (sidebar.classList.contains("sidebar-collapsed")) {
//         sidebar.classList.remove("sidebar-collapsed");
//         sidebar.classList.add("sidebar-expanded");
//     } else {
//         sidebar.classList.remove("sidebar-expanded");
//         sidebar.classList.add("sidebar-collapsed");
//     }
// });