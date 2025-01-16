from ajax_datatable.views import AjaxDatatableView
from .models import JobApplication


class ApplicationsAjaxDatatableView(AjaxDatatableView):

    model = JobApplication
    title = 'Job Applications'
    initial_order = [["when", "desc"],
                     [ "company", "desc"],
                     # [ "id", "desc" ],
                     ]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'all']]
    search_values_separator = '+'

    column_defs = [
        AjaxDatatableView.render_row_tools_column_def(),
        {'name': 'id', 'visible': False, },
        {'name': 'when', 'visible': True, },
        {'name': 'company', 'visible': True, },
        {'name': 'title', 'visible': True, },
        {'name': 'active', 'visible': True, },
        # {'name': 'actions', 'title': 'Actions', 'placeholder': True, 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):
        row['Actions'] = """
            <a href="{% url 'applications:application-details' appid=app.id %}"><button>View/Edit</button></a>
        """