import unittest

from hamlpy.views.generic import CreateView, DetailView, UpdateView


class DummyCreateView(CreateView):
    template_name = 'create.html'


class DummyDetailView(DetailView):
    template_name = 'detail.htm'


class DummyUpdateView(UpdateView):
    template_name = 'update.xml'


class DjangoViewsTest(unittest.TestCase):

    def test_get_template_names(self):
        assert DummyCreateView().get_template_names() == ['create.haml', 'create.hamlpy', 'create.html']
        assert DummyDetailView().get_template_names() == ['detail.haml', 'detail.hamlpy', 'detail.htm']
        assert DummyUpdateView().get_template_names() == ['update.haml', 'update.hamlpy', 'update.xml']
