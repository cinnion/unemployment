$(document).ready(function () {
    const table = $('#jobapplications').DataTable({
        ajax: {
            url: '/api/v1/jobapplications/',
            dataSrc: 'job_applications'
        },
        serverSide: true,
        processing: true,
        stateSave: true,
        rowId: 'id',
        'columns': [
            {
                class: 'dt-control',
                orderable: false,
                data: null,
                defaultContent: '',
            },
            {
                data: 'id',
                name: 'id',
                visible: false,
                searchable: false,
            },
            {
                data: 'when',
                name: 'when',
                title: 'When',
                width: '100px',
            },
            {
                data: 'company',
                name: 'company',
                title: 'Company',
                width: '300px',
            },
            {
                data: 'title',
                name: 'title',
                title: 'Job Title',
                render: function(data, type, row, meta) {
                    if (type === 'display') {
                        return '<a href="' + row.posting + '" target="new">' + data + '</a>';
                    }
                    return data;
                }
            },
            {
                data: 'posting',
                name: 'posting',
                title: 'Job Posting',
                visible: false,
            },
            {
                data: 'confirm',
                name: 'confirm',
                title: 'Confirmation',
                visible: false,
            },
            {
                data: 'notes',
                name: 'notes',
                title: 'Notes',
                visible: false,
            },
            {
                data: 'active',
                name: 'active',
                title: 'Still active?',
                render: function(data, type, row) {
                    if (data === true) {
                        return 'Yes';
                    } else {
                        return 'No';
                    }
                },
                width: '100px',
            },
            {
                defaultContent: '<a href="#" onclick="var id=this.closest(\'tr\').id; window.location.href=\'/applications/\' + id + \'/edit\';"><button>Edit</button></a>',
                name: 'edit',
                title: 'Actions',
                width: '100px',
                placeholder: true,
            }
        ],
        'order': [
            [1, 'desc'],
            [2, 'asc'],
        ],
        layout: {
            top1End: function () {
                let toolbar = document.createElement('div');
                toolbar.innerHTML = '<a href="/applications/new-application/"><button id="add">Add</button></a>';

                return toolbar;
            },
            topStart: 'pageLength',
            topEnd: 'search',
            bottomStart: 'info',
            bottomEnd: 'paging',
        }
    });


    const applicationDetailRows = [];

    function applicationDetailFormat(d) {
        let retval = 'Company: ' + d.company + '<br>' +
            'Job Title: ' + d.title + '<br>';

        if (d.posting != '') {
            retval += 'Job posting: <a href="' + d.posting + '" target="_blank">' + d.posting + '</a><br>';
        }

        if (d.confirm != '') {
            retval += 'Confirmation: <a href="' + d.confirm + '" target="_blank">' + d.confirm + '</a><br>';
        }

        if (d.notes != '') {
            retval += 'Notes: ' + d.notes + '<br>';
        }

        return (retval);
    }

    table.on('click', 'tbody td.dt-control', function () {
        let tr = event.target.closest('tr');
        let row = table.row(tr);
        let idx = applicationDetailRows.indexOf(tr.id)

        if (row.child.isShown()) {
            tr.classList.remove('details');
            row.child.hide();

            // Remove from the 'open' array
            applicationDetailRows.splice(idx, 1);
        } else {
            tr.classList.add('details');
            row.child(applicationDetailFormat(row.data())).show();

            // Add to the 'open' array
            if (idx === -1) {
                applicationDetailRows.push(tr.id);
            }
        }
    });

    table.on('draw', () => {
        applicationDetailRows.forEach((id, i) => {
            let el = document.querySelector('#' + id + ' td.dt-control');

            if (el) {
                el.dispatchEvent(new Event('click', {bubbles: true}));
            }
        });
    });

    $("#scrape-post").on("click", function() {
        const $svg = $(this);

        const $input = $svg.closest("span.input-group-text").siblings('input');

        const csrftoken = getCookie("csrftoken");

        const value = $input.val();

        console.log("Value is ", value);

        $.ajax({
            type: "POST",
            url: window.Urls['applications-api:application-scraper'](),
            data: {
                url: value,
            },
            headers: {
                'X-CSRFToken': csrftoken,
            },
        })
        .done(function (data, textStatus, jqXHR) {
            console.log("Clean URL: " + data.clean_url);
            console.log("Post Status: " + data.post_status);
            console.log("Posting ID: " + data.posting_id);
            console.log("Company: " + data.company);
            console.log("Title: " + data.title);
            console.log("Response Data:" + data);
            console.log("Status: " + textStatus);

            var $form = $("#rendered-form");
            $form.find('input[name="company"]').val(data.company);
            $form.find('input[name="title"]').val(data.title);
            $form.find('input[name="posting"]').val(data.clean_url);
            $form.find('input[name="saved_posting"]').val(data.posting_id);
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            if (jqXHR.responseJSON) {
                var errorMessage = jqXHR.responseJSON.error;
                console.log("Error message: " + errorMessage)
            } else if (jqXHR.responseText) {
                try {
                    var rawData = JSON.parse(jqXHR.responseText);
                    console.log("Parsed error message: ", rawData.error);
                } catch (e) {
                    console.log("Plain text error: ", jqXHR.responseText);
                }
            }
        });

    });
});
