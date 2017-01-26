$(document).ready(function () {
    jobFinished(job_id);
});


function jobFinished(job_id) {
    $.ajax({
        url: '/resolver/api/importer/' + job_id + '/status',
        method: 'GET',
        error: function (data) {
            $('#i_status').replaceWith('<span id="i_status">Failed</span>');
            $('#i_status_message').replaceWith('<p>The import job has failed. Redirecting to the error page.</p>');
        },
        success: function (data) {
            var url;
            if (data.status == 'Running') {
                setTimeout(function () {
                    jobFinished(job_id);
                }, 5000);
            } else if (data.status == 'Finished') {
                $('#i_status').replaceWith('<span id="i_status">Finished</span>');
                $('#i_status_message').replaceWith('<p>The import job has finished. Redirecting to the results page.</p>');
                url = '/resolver/csv/import/' + job_id + '/finished';
                window.location.replace(url);
            } else {
                $('#i_status').replaceWith('<span id="i_status">Failed</span>');
                $('#i_status_message').replaceWith('<p>The import job has failed. Redirecting to the error page.</p>');
                url = '/resolver/csv/import/' + job_id + '/failed';
                window.location.replace(url);
            }
        }
    });
}