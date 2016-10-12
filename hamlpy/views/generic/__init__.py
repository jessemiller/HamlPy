from __future__ import print_function, unicode_literals

import django.views.generic

pouet = [
    'ArchiveIndexView', 'YearArchiveView', 'MonthArchiveView',
    'WeekArchiveView', 'DayArchiveView', 'TodayArchiveView', 'DateDetailView',
    'DetailView', 'CreateView', 'UpdateView', 'DeleteView', 'ListView',
]


class HamlExtensionTemplateView(object):
    def get_template_names(self):
        names = super(HamlExtensionTemplateView, self).get_template_names()

        haml_names = []

        for name in names:
            if name.endswith((".html", ".htm", ".xml")):
                haml_names.append(name[:-len(".html")] + ".haml")
                haml_names.append(name[:-len(".html")] + ".hamlpy")

        return haml_names + names


for view in pouet:
    locals()[view] = type(view, (HamlExtensionTemplateView, getattr(django.views.generic, view)), {})
