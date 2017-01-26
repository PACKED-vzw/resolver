$(document).ready(function () {
    jobFinished(job_id);
});


function jobFinished(job_id) {
    $.ajax({
        url: '/resolver/api/importer/' + job_id + '/status',
        method: 'GET',
        success: function (data) {
            if (data.status == 'Running') {
                setTimeout(function () {
                    jobFinished(job_id)
                }, 5000);
            } else {
                $('#i_status').replaceWith('Finished');
                $('#i_status_message').replaceWith('<p>The import job has finished. Redirecting to the results page.</p>');
                setTimeout(function () {
                    window.location.replace('/resolver/api/importer/' + job_id + '/finished');
                }, 10000);
            }
        },
        error: function (jqXHR, status, error) {
            $('#i_status').replaceWith('Failed');
            $('#i_status_message').replaceWith('<p>The import job has failed. Redirecting to the error page.</p>');
            setTimeout(function () {
                window.location.replace('/resolver/api/importer/' + job_id + '/failed');
            }, 10000);
        }
    });
    //('/resolver/api/importer/' + job_id + '/status')
}
