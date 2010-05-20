from hamlpy import nodes

class TestNodeFactory():
    
    def test_creates_element_node_with_percent(self):
        node = nodes.createNode('%div')
        assert isinstance(node, nodes.ElementNode)
        
        node = nodes.createNode('   %html')
        assert isinstance(node, nodes.ElementNode)
        
    def test_creates_element_node_with_dot(self):
        node = nodes.createNode('.className')
        assert isinstance(node, nodes.ElementNode)
        
        node = nodes.createNode('   .className')
        assert isinstance(node, nodes.ElementNode)
        
    def test_creates_element_node_with_hash(self):
        node = nodes.createNode('#idName')
        assert isinstance(node, nodes.ElementNode)
        
        node = nodes.createNode('   #idName')
        assert isinstance(node, nodes.ElementNode)
    
    def test_creates_html_comment_node_with_front_slash(self):
        node = nodes.createNode('/ some Comment')
        assert isinstance(node, nodes.CommentNode)

        node = nodes.createNode('     / some Comment')
        assert isinstance(node, nodes.CommentNode)
        
    def test_random_text_returns_haml_node(self):
        node = nodes.createNode('just some random text')
        assert isinstance(node, nodes.HamlNode)
        
        node = nodes.createNode('   more random text')
        assert isinstance(node, nodes.HamlNode)
    
    def test_correct_symbol_creates_haml_comment(self):
        node = nodes.createNode('-# This is a haml comment')
        assert isinstance(node, nodes.HamlCommentNode)
        
    def test_equals_symbol_creates_variable_node(self):
        node = nodes.createNode('= some.variable')
        assert isinstance(node, nodes.VariableNode)
    
    def test_dash_symbol_creates_tag_node(self):
        node = nodes.createNode('- for something in somethings')
        assert isinstance(node, nodes.TagNode)
        
        
    
        
    