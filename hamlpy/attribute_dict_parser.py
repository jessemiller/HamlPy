import re

# Valid characters for dictionary key
re_key = re.compile(r'[a-zA-Z0-9-_]+')
re_nums = re.compile(r'[0-9\.]+')

class AttributeParser:
    """Parses comma-separated HamlPy attribute values"""
    
    def __init__(self, data, terminator):
        self.terminator=terminator
        self.s = data.lstrip()
        self.length=len(self.s)
        # Index of current character being read
        self.ptr=1

    
    def consume_whitespace(self, include_newlines=False):
        """Moves the pointer to the next non-whitespace character"""
        whitespace = (' ', '\t', '\r', '\n') if include_newlines else (' ', '\t')
        
        while self.ptr<self.length and self.s[self.ptr] in whitespace:
            self.ptr+=1
        return self.ptr

    def consume_end_of_value(self):
        # End of value comma or end of string
        self.ptr=self.consume_whitespace()
        if self.s[self.ptr] != self.terminator:
            if self.s[self.ptr] == ',':
                self.ptr+=1
            else:
                raise Exception("Expected comma for end of value (after ...%s), but got '%s' instead" % (self.s[max(self.ptr-10,0):self.ptr], self.s[self.ptr]))

    def read_until_unescaped_character(self, closing):
        """
        Move the pointer until a *closing* character not preceded by a backslash is found.
        Returns the string found up to that point with any escaping backslashes removed
        """
        initial_ptr=self.ptr
                
        while self.ptr<self.length:
            if self.s[self.ptr]==closing and (self.ptr==initial_ptr or self.s[self.ptr-1]!='\\'):
                break
            self.ptr+=1
        
        value=self.s[initial_ptr:self.ptr].replace('\\'+closing,closing)

        # Consume the closing character
        self.ptr+=1
        
        return value
    
    def parse_value(self):
        self.ptr=self.consume_whitespace()

        # Invalid initial value
        val=False
        if self.s[self.ptr]==self.terminator:
            return val
        
        # String
        if self.s[self.ptr] in ("'",'"'):
            quote=self.s[self.ptr]
            self.ptr += 1
            val = self.read_until_unescaped_character(quote)
        # Django variable
        elif self.s[self.ptr:self.ptr+2] == '={':
            self.ptr+=2
            val = self.read_until_unescaped_character('}')
            val="{{ %s }}" % val
        # Django tag
        elif self.s[self.ptr:self.ptr+2] in ['-{', '#{']:
            self.ptr+=2
            val = self.read_until_unescaped_character('}')
            val=r"{%% %s %%}" % val
        # Boolean Attributes
        elif self.s[self.ptr:self.ptr+4] in ['none','None']:
            val = None
            self.ptr+=4
        # Integers and floats
        else:
            match=re_nums.match(self.s[self.ptr:])
            if match:
                val = match.group(0)
                self.ptr += len(val)

        if val is False:
            raise Exception("Failed to parse dictionary value beginning at: %s" % self.s[self.ptr:])

        self.consume_end_of_value()
        
        return val



class AttributeDictParser(AttributeParser):
    """
    Parses a Haml element's attribute dictionary string and
    provides a Python dictionary of the element attributes
    """

    def __init__(self, s):
        AttributeParser.__init__(self, s, '}')
        self.dict={}
    
    def parse(self):
        while self.ptr<self.length-1:
            key = self.__parse_key()

            # Tuple/List parsing
            self.ptr=self.consume_whitespace()
            if self.s[self.ptr] in ('(', '['):
                tl_parser = AttributeTupleAndListParser(self.s[self.ptr:])
                val = tl_parser.parse()
                self.ptr += tl_parser.ptr
                self.consume_end_of_value()
            else:
                val = self.parse_value()

            self.dict[key]=val
        return self.dict

    def __parse_key(self):
        '''Parse key variable and consume up to the colon'''

        self.ptr=self.consume_whitespace(include_newlines=True)
        
        # Consume opening quote
        quote=None
        if self.s[self.ptr] in ("'",'"'):
            quote = self.s[self.ptr]
            self.ptr += 1

        # Extract key
        if quote:
            key = self.read_until_unescaped_character(quote)
        else:
            key_match = re_key.match(self.s[self.ptr:])
            if key_match is None:
                raise Exception("Invalid key beginning at: %s" % self.s[self.ptr:])
            key = key_match.group(0)
            self.ptr += len(key)

        # Consume colon
        ptr=self.consume_whitespace()
        if self.s[self.ptr]==':':
            self.ptr+=1
        else:
            raise Exception("Expected colon for end of key (after ...%s), but got '%s' instead" % (self.s[max(self.ptr-10,0):self.ptr], self.s[self.ptr]))

        return key

    def render_attributes(self):
        attributes=[]
        for k, v in self.dict.items():
            if k != 'id' and k != 'class':
                # Boolean attributes
                if v==None:
                    attributes.append( "%s" % (k,))
                else:
                    attributes.append( "%s='%s'" % (k,v))
                                       
        return ' '.join(attributes)
    

class AttributeTupleAndListParser(AttributeParser):
    def __init__(self, s):
        if s[0]=='(':
            terminator = ')'
        elif s[0]=='[':
            terminator = ']'
        AttributeParser.__init__(self, s, terminator)

    def parse(self):
        lst=[]

        # Todo: Must be easier way...
        val=True
        while val != False:
            val = self.parse_value()
            if val != False:
                lst.append(val)

        self.ptr +=1
        
        if self.terminator==')':
            return tuple(lst)
        else:
            return lst
        
