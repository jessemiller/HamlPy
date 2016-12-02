from __future__ import print_function, unicode_literals

import django.views.generic

pouet = [
    'ArchiveIndexView', 'YearArchiveView', 'MonthArchiveView',
    'WeekArchiveView', 'DayArchiveView', 'TodayArchiveView', 'DateDetailView',
    'DetailView', 'CreateView', 'UpdateView', 'DeleteView', 'ListView',
]


NON_HAMLPY_EXTENSIONS = ('.html', '.htm', '.xml')


class HamlExtensionTemplateView(object):
    def get_template_names(self):
        names = super(HamlExtensionTemplateView, self).get_template_names()

        haml_names = []

        for name in names:

            for ext in NON_HAMLPY_EXTENSIONS:
                if name.endswith(ext):
                    base_name = name[:-len(ext)]
                    haml_names.append(base_name + ".haml")
                    haml_names.append(base_name + ".hamlpy")

        return haml_names + names


for view in pouet:
    locals()[view] = type(str(view), (HamlExtensionTemplateView, getattr(django.views.generic, view)), {})
