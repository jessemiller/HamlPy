from hamlpy import hamlpy

class TestNodeFactory():
    
    def test_creates_element_node_with_percent(self):
        node = hamlpy.createNode('%div')
        assert isinstance(node, hamlpy.ElementNode)
        
        node = hamlpy.createNode('   %html')
        assert isinstance(node, hamlpy.ElementNode)
        
    def test_creates_element_node_with_dot(self):
        node = hamlpy.createNode('.className')
        assert isinstance(node, hamlpy.ElementNode)
        
        node = hamlpy.createNode('   .className')
        assert isinstance(node, hamlpy.ElementNode)
        
    def test_creates_element_node_with_hash(self):
        node = hamlpy.createNode('#idName')
        assert isinstance(node, hamlpy.ElementNode)
        
        node = hamlpy.createNode('   #idName')
        assert isinstance(node, hamlpy.ElementNode)
    
    def test_creates_html_comment_node_with_front_slash(self):
        node = hamlpy.createNode('/ some Comment')
        assert isinstance(node, hamlpy.CommentNode)

        node = hamlpy.createNode('     / some Comment')
        assert isinstance(node, hamlpy.CommentNode)
        
    def test_random_text_returns_haml_node(self):
        node = hamlpy.createNode('just some random text')
        assert isinstance(node, hamlpy.HamlNode)
        
        node = hamlpy.createNode('   more random text')
        assert isinstance(node, hamlpy.HamlNode)
    
    def test_correct_symbol_creates_haml_comment(self):
        node = hamlpy.createNode('-# This is a haml comment')
        assert isinstance(node, hamlpy.HamlCommentNode)
        
        
    
        
    