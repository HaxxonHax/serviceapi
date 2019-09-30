""" Class for configuration files. """
import json


def find_missing(lst):
    """ Find missing number in list of numbers. """
    return [x for x in range(lst[0], lst[-1]+1)
            if x not in lst]


class Block:
    """ Class for the block definitions. """
    def __init__(self, block_name):
        self.id = 0
        self.name = block_name
        self.settings = {}

    def set_id(self, id_num):
        """ Sets the block ID. """
        self.id = id_num

    def add_setting(self, key, value):
        """ Adds a setting to the dictionary of settings. """
        if key is not None:
            self.settings.update({key: value})

    def update_setting(self, key, value):
        """ Updates a setting to the dictionary of settings. """
        if key is not None:
            self.settings.update(key, value)

    def delete_setting(self, key):
        """ Removes a setting from the dictionary of settings. """
        if key in self.settings:
            del self.settings[key]


class ServiceConfig:
    """ Class for the configuration files. """
    def __init__(self, filepath, filetype, blocks=None, settings=None,
                 closer='', definer='=', commenter='#'):
        if settings is not None:
            self.settings = settings
        else:
            self.settings = {}
        if blocks is not None:
            self.blocks = blocks
        else:
            self.blocks = []
        self.filetype = filetype
        self.filepath = filepath
        self.output = ''
        self.block_index = 0
        self.closer = closer
        self.definer = definer
        self.commenter = commenter

    def add_block(self, block_name):
        """ Adds a new block. """
        if len(self.blocks) == 0:
            next_id = 0
        else:
            current_id_list = list(map(lambda x: x.id, self.blocks))
            next_id = find_missing(current_id_list)
            if len(next_id) == 0:
                next_id = self.blocks[0].id + 1
            else:
                next_id = next_id[0]
        block = Block(block_name)
        block.set_id(next_id)
        self.block_index = next_id
        self.blocks.append(block)

    def add_setting(self, key, value, block_id=None, block_name=None):
        """ Adds a setting to the dictionary of settings. """
        if key is not None:
            if block_id is None and block_name is None:
                for block in self.blocks:
                    if block.id == self.block_index:
                        block.add_setting(key, value)
            elif block_id is not None:
                for block in self.blocks:
                    if block.id == block_id:
                        block.add_setting(key, value)
            elif block_name is not None:
                for block in self.blocks:
                    if block.name == block_name:
                        block.add_setting(key, value)

    def update_setting(self, key, value, block_id=None, block_name=None):
        """ Updates a setting to the dictionary of settings. """
        if key is not None:
            self.add_setting(key, value, block_id, block_name)

    def delete_setting(self, key, block_id=None, block_name=None):
        """ Removes a setting from the block. """
        if key is not None:
            if block_id is None and block_name is None:
                for block in self.blocks:
                    if block.id == self.block_index:
                        block.delete_setting(key)
            elif block_id is not None:
                for block in self.blocks:
                    if block.id == block_id:
                        block.delete_setting(key)
            elif block_name is not None:
                for block in self.blocks:
                    if block.name == block_name:
                        block.delete_setting(key)

    def format_blocks(self):
        """ Formats the output in bracked block format. """
        output = ''
        for block in self.blocks:
            output += block.name + '{' + '\n'
            for key in block.settings:
                output += (key + self.definer + block.settings[key] +
                           self.closer + '\n')
            output += '}\n'
        return output

    def format_ini(self):
        """ Formats the output in INI like format. """
        output = ''
        for block in self.blocks:
            output += '[' + block.name + ']' + '\n'
            for key in block.settings:
                output += (key + self.definer + block.settings[key] +
                           self.closer + '\n')
            output += '\n'
        return output

    def format_jsonarray(self):
        """ Formats the blocks in JSON format. """
        jsonarray_output = []
        for block in self.blocks:
            jsonarray_output.append({block.name: block.settings})
        return jsonarray_output

    def format_raw(self):
        """ Formats the output in RAW format. """
        output = ''
        for block in self.blocks:
            output += (self.commenter + ' ' + block.name +
                       self.closer + '\n')
            for key in block.settings:
                output += (key + self.definer + block.settings[key] +
                           self.closer + '\n')
            output += '\n'
        return output

    def format(self) -> str:
        """ Formats the output according to the filetype. """
        if self.filetype == 'jsonarray':
            self.output = json.dumps(self.format_jsonarray())
        elif self.filetype == 'blocks':
            self.output = self.format_blocks()
        elif self.filetype == 'ini':
            self.output = self.format_ini()
        else:
            self.output = self.format_raw()
        return self.output

    def save(self):
        """ Saves the configuratin file. """
        self.output = self.format()
        print(self.output)

