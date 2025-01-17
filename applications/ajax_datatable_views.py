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
        {'name': 'actions', 'title': 'Actions', 'placeholder': True, 'searchable': False, 'orderable': False, },
    ]

    def customize_row(self, row, obj):
        row['actions'] = """
                    <a href="#"
                    onclick="var id=this.closest('tr').id.substr(4); window.location.href='/applications/' + id + '/edit'"><button>Edit</button></a>
                """

    def render_row_details(self, pk, request=None):
        obj = self.model.objects.get(pk=pk)
        fields = [f for f in self.model._meta.get_fields() if f.concrete]
        html = '<table class="row-details">'
        for field in fields:
            value = getattr(obj, field.name)
            html += '<tr><td>%s</td>' % field.name
            if field.name in [ 'posting', 'confirm'] and value is not None:
                html += '<td><a href="%s" target="_blank">%s</a></td></tr>' % (value, value)
            else:
                html += '<td>%s</td></tr>' % value
        html += '</table>'
        return html
