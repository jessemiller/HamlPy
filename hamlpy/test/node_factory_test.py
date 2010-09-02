from hamlpy import nodes

class TestNodeFactory():
    
    def test_creates_element_node_with_percent(self):
        node = nodes.create_node('%div')
        assert isinstance(node, nodes.ElementNode)
        
        node = nodes.create_node('   %html')
        assert isinstance(node, nodes.ElementNode)
        
    def test_creates_element_node_with_dot(self):
        node = nodes.create_node('.className')
        assert isinstance(node, nodes.ElementNode)
        
        node = nodes.create_node('   .className')
        assert isinstance(node, nodes.ElementNode)
        
    def test_creates_element_node_with_hash(self):
        node = nodes.create_node('#idName')
        assert isinstance(node, nodes.ElementNode)
        
        node = nodes.create_node('   #idName')
        assert isinstance(node, nodes.ElementNode)
    
    def test_creates_html_comment_node_with_front_slash(self):
        node = nodes.create_node('/ some Comment')
        assert isinstance(node, nodes.CommentNode)

        node = nodes.create_node('     / some Comment')
        assert isinstance(node, nodes.CommentNode)
        
    def test_random_text_returns_haml_node(self):
        node = nodes.create_node('just some random text')
        assert isinstance(node, nodes.HamlNode)
        
        node = nodes.create_node('   more random text')
        assert isinstance(node, nodes.HamlNode)
    
    def test_correct_symbol_creates_haml_comment(self):
        node = nodes.create_node('-# This is a haml comment')
        assert isinstance(node, nodes.HamlCommentNode)
        
    def test_equals_symbol_creates_variable_node(self):
        node = nodes.create_node('= some.variable')
        assert isinstance(node, nodes.VariableNode)
    
    def test_dash_symbol_creates_tag_node(self):
        node = nodes.create_node('- for something in somethings')
        assert isinstance(node, nodes.TagNode)
