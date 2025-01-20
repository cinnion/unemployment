$(document).ready(function(){
    $('#jobapplications').DataTable({
        ajax: {
            url: '/api/jobapplications/',
            dataSrc: 'job_applications'
        },
        serverSide: true,
        processing: true,
        rowId: 'id',
        'columns': [
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
            [ 1, 'desc' ],
            [ 2, 'asc' ],
        ],
    });
});