""" Class for configuration files. """
import json
import re
import sys


E_FILENOTFOUND = 1
E_INVALIDPERMS = 2

# Keyword for no block header
NOBLOCK = 'ZEROBLOCK'


def find_missing(lst):
    """ Find missing number in list of numbers. """
    if not lst:
        return [0]
    if len(lst) == 1:
        return [1]
    return [x for x in range(lst[0], lst[-1]+1)
            if x not in lst]


class Block:
    """ Class for the block definitions. """
    def __init__(self, block_name):
        self.blockid = 0
        self.name = block_name
        self.settings = {}

    def set_blockid(self, id_num):
        """ Sets the block ID. """
        self.blockid = id_num

    def add_setting(self, key, value):
        """ Adds a setting to the dictionary of settings. """
        if key is not None:
            self.settings.update({str(key): str(value)})

    def update_setting(self, key, value):
        """ Updates a setting to the dictionary of settings. """
        if key is not None:
            self.settings.update({str(key), str(value)})

    def delete_setting(self, key):
        """ Removes a setting from the dictionary of settings. """
        if key in self.settings:
            del self.settings[key]


class ServiceConfig:  # pylint: disable=R0902
    """ Class for the configuration files. """
    def __init__(self, filepath, filetype,  # pylint: disable=R0913
                 blocks=None, closer='', definer='=', commenter='#'):
        if blocks is not None:
            self.blocks = blocks
            self.block_index = len(self.blocks) - 1
        else:
            self.blocks = []
            self.block_index = -1
        self.filetype = filetype
        self.filepath = filepath
        self.output = ''
        self.closer = closer
        self.definer = definer
        self.commenter = commenter

    def clear_settings(self):
        """ Clears the instance's settings. """
        self.blocks = []
        self.block_index = -1

    def load_blocktype(self, content):
        """ Parses the contents into block settings. """
        contents = content.split('\n')
        for cts in contents:
            # find the next block
            if cts:
                if cts[-1] == '{':
                    blockname = re.findall('\w+(?:-\w+)*', cts)
                    self.add_block(blockname[0])
                elif self.block_index != -1 and self.definer in cts:
                    key = cts.split(self.definer, 1)[0]
                    key = key.strip()
                    value = cts.split(self.definer, 1)[1]
                    value = value.strip()
                    self.add_setting(key, value)
                elif self.block_index == -1 and self.definer in cts:
                    self.add_block(NOBLOCK)

    def load(self, filepath=None):
        """ Loads the settings from a file. """
        if not filepath:
            filepath = self.filepath
        self.clear_settings()
        filehandler = open(filepath, 'r')
        if filehandler.mode == 'r':
            contents = filehandler.read()
            if self.filetype == 'braced':
                self.load_blocktype(contents)
            filehandler.close()

    def add_block(self, block_name):
        """ Adds a new block. """
        if self.blocks == []:
            next_id = 0
        else:
            current_id_list = list(map(lambda x: x.blockid, self.blocks))
            next_id = find_missing(current_id_list)
            if next_id:
                next_id = next_id[0]
            else:
                next_id = self.blocks[-1].blockid + 1
        block = Block(block_name)
        block.set_blockid(next_id)
        self.block_index = next_id
        self.blocks.append(block)

    def add_setting(self, key, value,  # pylint: disable=R0912,R0913
                    block_id=None, block_name=None, match=None):
        """ Adds a setting to the dictionary of settings. """
        # TODO: Rewrite, Allow for settings outside of blocks
        if key is not None:
            if block_id is None and block_name is None:
                for block in self.blocks:
                    if block.blockid == self.block_index:
                        block.add_setting(key, value)
            elif block_id is not None:
                for block in self.blocks:
                    if block.blockid == block_id:
                        block.add_setting(key, value)
            elif block_name is not None:
                for block in self.blocks:
                    if block.name == block_name:
                        block.add_setting(key, value)
            elif match is not None:
                for block in self.blocks:
                    if key in block and value == block[key]:
                        block.add_setting(key, value)

    def update_setting(self, key, value,  # pylint: disable=R0913
                       block_id=None, block_name=None, match=None):
        """ Updates a setting to the dictionary of settings. """
        if key is not None:
            self.add_setting(key, value, block_id, block_name, match)

    def delete_setting(self, key, block_id=None, block_name=None):
        """ Removes a setting from the block. """
        if key is not None:
            if block_id is None and block_name is None:
                for block in self.blocks:
                    if block.blockid == self.block_index:
                        block.delete_setting(key)
            elif block_id is not None:
                for block in self.blocks:
                    if block.blockid == block_id:
                        block.delete_setting(key)
            elif block_name is not None:
                for block in self.blocks:
                    if block.name == block_name:
                        block.delete_setting(key)

    def format_braced(self):
        """ Formats the output in bracked block format. """
        output = ''
        for block in self.blocks:
            if block.name != NOBLOCK:
                output += block.name + ' {' + '\n'
            for key in block.settings:
                output += ('    ' + key + self.definer +
                           block.settings[key] + self.closer + '\n')
            if block.name != NOBLOCK:
                output += '}\n'
        return output

    def format_ini(self):
        """ Formats the output in INI like format. """
        output = ''
        for block in self.blocks:
            if block.name != NOBLOCK:
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
            if block.name != NOBLOCK:
                output += (self.commenter + ' ' + block.name + '\n')
            for key in block.settings:
                output += (key + self.definer + block.settings[key] +
                           self.closer + '\n')
            output += '\n'
        return output

    def format(self) -> str:
        """ Formats the output according to the filetype. """
        if self.filetype == 'jsonarray':
            self.output = json.dumps(self.format_jsonarray())
        elif self.filetype == 'braced':
            self.output = self.format_braced()
        elif self.filetype == 'ini':
            self.output = self.format_ini()
        else:
            self.output = self.format_raw()
        return self.output

    def save(self):
        """ Saves the configuration file. """
        self.output = self.format()
        print(self.output)

    def print(self):
        """ Prints the configuration file. """
        self.output = self.format()
        print(self.output)

    def set_filepath(self, filepath):
        """ Sets the configuration file path. """
        self.filepath = filepath

