from nose.tools import eq_

from hamlpy.elements import Element

class TestElement(object):

		def test_pulls_tag_name_off_front(self):
		    sut = Element('%div.class')
		    eq_(sut.tag, 'div')
		    
		def test_default_tag_is_div(self):
		    sut = Element('.class#id')
		    eq_(sut.tag, 'div')
		    
		def test_parses_id(self):
		    sut = Element('%div#someId.someClass')
		    eq_(sut.id, 'someId')
		    
		    sut = Element('#someId.someClass')
		    eq_(sut.id, 'someId')
		    
		def test_no_id_gives_empty_string(self):
		    sut = Element('%div.someClass')
		    eq_(sut.id, '')
		
		def test_parses_class(self):
		    sut = Element('%div#someId.someClass')
		    eq_(sut.classes, 'someClass')
		    
		def test_properly_parses_multiple_classes(self):
		    sut = Element('%div#someId.someClass.anotherClass')
		    eq_(sut.classes, 'someClass anotherClass')
		    
		def test_no_class_gives_empty_string(self):
		    sut = Element('%div#someId')
		    eq_(sut.classes, '')
		    
		
		    
		
		    
		    
		    
		    
		    
		    
		    