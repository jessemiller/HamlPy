import django.views.generic

from hamlpy import HAML_EXTENSIONS

pouet = [
    'ArchiveIndexView', 'YearArchiveView', 'MonthArchiveView',
    'WeekArchiveView', 'DayArchiveView', 'TodayArchiveView', 'DateDetailView',
    'DetailView', 'CreateView', 'UpdateView', 'DeleteView', 'ListView',
]

NON_HAML_EXTENSIONS = ('html', 'htm', 'xml')


class HamlExtensionTemplateView(object):
    def get_template_names(self):
        names = super(HamlExtensionTemplateView, self).get_template_names()

        haml_names = []

        for name in names:

            for ext in NON_HAML_EXTENSIONS:
                if name.endswith('.' + ext):
                    base_name = name[:-len(ext)]

                    for haml_ext in HAML_EXTENSIONS:
                        haml_names.append(base_name + haml_ext)

        return haml_names + names


for view in pouet:
    locals()[view] = type(str(view), (HamlExtensionTemplateView, getattr(django.views.generic, view)), {})
