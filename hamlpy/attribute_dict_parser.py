import re

# Valid characters for dictionary key
re_key = re.compile(r'[a-zA-Z0-9-_]+')
re_nums = re.compile(r'[0-9\.]+')

class AttributeParser:
    """Parses comma-separated HamlPy attribute values"""
    
    def __init__(self, data, terminator):
        self.terminator=terminator
        self.s = data.lstrip()
        # Index of current character being read
        self.ptr=1

    def consume_whitespace(self, include_newlines=False):
        """Moves the pointer to the next non-whitespace character"""
        whitespace = (' ', '\t', '\r', '\n') if include_newlines else (' ', '\t')
        
        while self.ptr<len(self.s) and self.s[self.ptr] in whitespace:
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


    def read_until_unescaped_character(self, closing, pos=0):
        """
        Moves the dictionary string starting from position *pos*
        until a *closing* character not preceded by a backslash is found.
        Returns a tuple containing the string which was read (without any preceding backslashes)
        and the number of characters which were read.
        """
        initial_pos=pos

        while pos<len(self.s):
            if self.s[pos]==closing and (pos==initial_pos or self.s[pos-1]!='\\'):
                break
            pos+=1
        return (self.s[initial_pos:pos].replace('\\'+closing,closing), pos-initial_pos+1)

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
            val,characters_read = self.read_until_unescaped_character(quote, pos=self.ptr)
            self.ptr += characters_read
        # Django variable
        elif self.s[self.ptr:self.ptr+2] == '={':
            self.ptr+=2
            val,characters_read = self.read_until_unescaped_character('}', pos=self.ptr)
            self.ptr += characters_read
            val="{{ %s }}" % val
        # Django tag
        elif self.s[self.ptr:self.ptr+2] == '-{':
            self.ptr+=2
            val,characters_read = self.read_until_unescaped_character('}', pos=self.ptr)
            self.ptr += characters_read
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
    
    def parse(self):
        dic={}
        while self.ptr<len(self.s)-1:
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

            dic[key]=val
        return dic

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
            key,characters_read = self.read_until_unescaped_character(quote, pos=self.ptr)
            self.ptr+=characters_read
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

class AttributeTupleAndListParser(AttributeParser):
    def __init__(self, s):
        if s[0]=='(':
            terminator = ')'
        elif s[0]=='[':
            terminator = ']'
        AttributeParser.__init__(self, s, terminator)

    def parse(self):
        print '***', self.s
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
        
