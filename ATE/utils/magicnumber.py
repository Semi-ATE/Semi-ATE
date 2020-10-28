'''
Created on Aug 5, 2019

@author: hoeren

References for the magic numbers:
    https://en.wikipedia.org/wiki/List_of_file_signatures
    https://asecuritysite.com/forensics/magic
    https://www.garykessler.net/library/file_sigs.html
'''
import os

extensions = {'.gz'   : [[(0, b'\x1f\x8b\x08')]], # gzip
              '.pdf'  : [[(0, b'\x25\x50\x44\x46\x2d')]],
              '.wav'  : [[(0, b'\x52\x49\x46\x46'), (8, b'\x57\x41\x56\x45')]],
              '.avi'  : [[(0, b'\x52\x49\x46\x46'), (8, b'\x41\x56\x49\x20')]],
              '.mp3'  : [[(0, b'\xFF\xFB')],
                         [(0, b'\x49\x44\x33')]],
              '.stdf' : [[(2, b'\x00\x0A')]],
              '.rpm'  : [[(0, b'\xed\xab\xee\xdb')]],
              '.ico'  : [[(0, b'\x00\x00\x01\x00')]],
              '.z'    : [[(0, b'\x1F\x9D')],
                         [(0, b'1F A0')]],
              '.bz2'  : [[(0, b'\x42\x5A\x68')]],
              '.gif'  : [[(0, b'\x47\x49\x46\x38\x37\x61')],
                         [(0, b'\x47\x49\x46\x38\x39\x61')]],
              '.tiff' : [[(0, b'\x49\x49\x2A\x00')],
                         [(0, b'\x4D\x4D\x00\x2A')]],
              '.exr'  : [[(0, b'\x76\x2F\x31\x01')]],
              '.bpg'  : [[(0, b'\x42\x50\x47\xFB')]],
              '.jpg'  : [[(0, b'\xFF\xD8\xFF\xDB')],
                         [(0, b'\xFF\xD8\xFF\xE0\x00\x10\x4A\x46\x49\x46\x00\x01')],
                         [(0, b'\xFF\xD8\xFF\xEE')],
                         [(0, b'\xFF\xD8\xFF\xE1'), (6, b'\x45\x78\x69\x66\x00\x00')]],
              '.lz'   : [[(0, b'\x4C\x5A\x49\x50')]],
              '.xls'  : [[(0, b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1')]],
              '.zip'  : [[(0, b'\x50\x4B\x03\x04')],
                         [(0, b'\x50\x4B\x05\x06')],
                         [(0, b'\x50\x4B\x07\x08')]],
              '.rar'  : [[(0, b'\x52\x61\x72\x21\x1A\x07\x00')],
                         [(0, b'\x52\x61\x72\x21\x1A\x07\x01\x00')]],
              '.png'  : [[(0, b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A')]],
              '.ps'   : [[(0, b'\x25\x21\x50\x53')]],
              '.ogg'  : [[(0, b'\x4F\x67\x67\x53')]],
              '.psd'  : [[(0, b'\x38\x42\x50\x53')]],
              '.mp3'  : [[(0, b'\xFF\xFB')],
                         [(0, b'\x49\x44\x33')]],
              '.bmp'  : [[(0, b'\x42\x4D')]],
              '.iso'  : [[(0, b'\x43\x44\x30\x30\x31')]],
              '.flac' : [[(0, b'\x66\x4C\x61\x43')]],
              '.midi' : [[(0, b'\x4D\x54\x68\x64')]],
              '.vmdk' : [[(0, b'\x4B\x44\x4D')]],
              '.dmg'  : [[(0, b'\x78\x01\x73\x0D\x62\x62\x60')]],
              '.xar'  : [[(0, b'\x78\x61\x72\x21')]],
              '.tar'  : [[(0, b'\x75\x73\x74\x61\x72\x00\x30\x30')],
                         [(0, b'\x75\x73\x74\x61\x72\x20\x20\x00')]],
              '.7z'   : [[(0, b'\x37\x7A\xBC\xAF\x27\x1C')]], # 7-Zip
              '.xz'   : [[(0, b'\xFD\x37\x7A\x58\x5A\x00\x00')]], # lzma
              '.XML'  : [[(0, b'\x3c\x3f\x78\x6d\x6c\x20')]],
              '.swf'  : [[(0, b'\x43\x57\x53')],
                         [(0, b'\x46\x57\x53')]],
              '.deb'  : [[(0, b'\x21\x3C\x61\x72\x63\x68\x3E')]],
              '.rtf'  : [[(0, b'\x7B\x5C\x72\x74\x66\x31')]],
              '.xcf'  : [[(0, b'\x67\x69\x6d\x70\x20\x78\x63\x66\x20')]],
              '.xlsx' : [[(0, b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1')], #password protected
                         [(0, b'\x50\x4B\x03\x04\x14\x00\x06\x00')]], # not password protected
              '.docx' : [[(0, b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1')], #password protected
                         [(0, b'\x50\x4B\x03\x04\x14\x00\x06\x00')]], # not password protected
              '.pptx' : [[(0, b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1')], #password protected
                         [(0, b'\x50\x4B\x03\x04\x14\x00\x06\x00')]], # not password protected

              }

compression_extensions = ['.gz', '.7z', '.zip', '.xz', '.bz2']
image_extensions = ['.exr', '.tiff', '.ico', '.gif', '.bpg', '.png', '.jpg']
known_extensions = [ext for ext in extensions]

for ext in compression_extensions:
    if ext not in extensions:
        raise Exception("compression extension '%s' has no magic number" % ext)
for ext in image_extensions:
    if ext not in extensions:
        raise Exception("image extension '%s' has no magic number" % ext)

def is_compressed_file(FileName, extensions_of_interest=compression_extensions):
    '''
    This function returns True if it is determined that FileName is compressed, False otherwise.
    Note: it will use the extension_from_magic_number function of this module.
    '''
    ext = extension_from_magic_number_in_file(FileName)
    if len(ext)==1: # a compressed file is unambiguous
        if ext[0] in extensions_of_interest:
            return True
    return False

def is_image_file(FileName, extensions_of_interest=image_extensions):
    '''
    This function returns True if it is determined that FileName is an image, False otherwhise.
    Note: it will use the extension_from_magic_number function of this module.
    '''
    ext = extension_from_magic_number_in_file(FileName)
    if len(ext)==1: # an image file should be unambiguous
        if ext[0] in extensions_of_interest:
            return True
    return False

def extension_from_magic_number_in_file(FileName, extensions_of_interest=known_extensions):
    '''
    This function will try to determine the type of 'FileName' by looking at it's contents.
    returns the supposed extension (with the '.') of the fileType or None if nothing is recognized.

    Note: it doesn't look at the extension of a filename like 'mimetypes' does !
    Ref: https://en.wikipedia.org/wiki/List_of_file_signatures
    '''
    debug = False
    prv = []
    if debug: print(FileName)
    if os.path.exists(FileName) and os.path.isfile(FileName):
        with open(FileName, 'rb') as fd:
            for extension in extensions:
                possibilities = len(extensions[extension])
                if debug: print("\t'%s'" % extension)
                for possibility, magic_number in enumerate(extensions[extension]):
                    parts = len(magic_number)
                    if debug: print("\t\tPossibility %s/%s has %s parts: '%s'" % (possibility+1, possibilities, parts, magic_number))
                    tmp = []
                    for part, definition in enumerate(magic_number):
                        offset, pattern = definition
                        if debug: print("\t\t\t part=%s/%s : offset = %d, magic = %s, lenght = %d bytes" % (part+1, parts, definition[0], definition[1], len(pattern)), end = '')
                        fd.seek(offset)
                        data = fd.read(len(pattern))
                        if debug: print(" --> %s == %s ? " % (data, pattern), end='')
                        if data == pattern:
                            tmp.append(extension)
                            if debug: print('YES')
                        else:
                            if debug: print('NO')
                    if len(tmp) == parts:
                        prv.append(extension)
    retval = []
    for ext in prv:
        if ext in extensions_of_interest:
            retval.append(ext)
    return retval

if __name__ == '__main__':
    from ATE import package_root

    resources_path = os.path.normpath(os.path.join(package_root, r'./../../resources'))
    if not os.path.exists(resources_path) or not os.path.isdir(resources_path):
        raise Exception("'%s' is not valid.")

    doc_path = os.path.normpath(os.path.join(package_root, r'./../../doc'))
    if not os.path.exists(doc_path) or not os.path.isdir(doc_path):
        raise Exception("'%s' is not valid.")

    FileNames = []
    for root, _, files in os.walk(resources_path):
        for file in files:
            if not file.startswith('.'):
                FileNames.append(os.path.join(root, file))
    for root, _, files in os.walk(doc_path):
        for file in files:
            if not file.startswith('.'):
                FileNames.append(os.path.join(root, file))

    for FileName in FileNames:
        print(FileName, extension_from_magic_number_in_file(FileName))
