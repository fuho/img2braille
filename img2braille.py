#!/usr/bin/python
# vim:fileencoding=utf-8
import Image
"""img2braille module takes an imgae and converts it into braille text"""

def img2bin(img,sub_w =2, sub_h = 4):
    """Converts image data to a [x,y]list of 0s and 1s.
    First it corrects the size of image data to multiple of braille char
    width and height. Then black pixels will be set to 1, all other
    pixels will be set to 0"""
    img_w, img_h = img.size
    fix_w = img_w
    fix_h = img_h
    #Correct the size of image
    if img_w % sub_w: fix_w += sub_w - img_w % sub_w
    if img_h % sub_h: fix_h += sub_h - img_h % sub_h
    #Generate an empty output [X][Y] list of lists
    output = [[0 for y in range(fix_h)] for x in range(fix_w)]
    #Populate list with data from img
    img_data = list(img.getdata())
    for x in range(img_w):
        for y in range(img_h):
            index = img_w * y + x
            output[x][y] = int(not bool(img_data[index]))
    return output

def mapBraille(index):
    """Returns unicode Braille letter with index index"""
    result = unichr(10240 + index)
    return result

def bin2index(b_img, sub_w = 2, sub_h = 4):
    """Returns [x][y] list of  integer values. b_img must have coorect size!"""
    result = []
    b_img_w = len(b_img)
    b_img_h = len(b_img[0])
    new_w = b_img_w / sub_w
    new_h = b_img_h / sub_h
    output = [[0 for y in range(new_h)] for x in range(new_w)]
    for y in range(new_h):
        for x in range(new_w):
            #For each position in selection get value
            block = []
            for sub_x in range(sub_w):
                for sub_y in range(sub_h):
                    j = x * sub_w + sub_x 
                    k = y * sub_h + sub_y
                    #Add to index = ?*2^n, 0 if empty
                    block.append(b_img[j][k])
            output[x][y] = block2index(block)
    return output

def block2index(block):
    """Converts one pixel block (2x4, but flattened by columns) to
    its index(position of braille char).0 dots = 0; 8 dots = ff = 255
    
    ## <-- one braille character of 8 pixels
    ##  
    ##  03  <-- order of bits in one char(positions)
    ##  14      this char comes as "01263457"
        25 |° |  <--this would be represented in binary as "01110101"
        67 | °|     this char comes as a list "1,0,1,1,0,1,1,0"      
           |°°|     pos 0 = dot   x 2^0    pos 4 = dot   x 2^4
           |° |     pos 1 = empty x 2^1    pos 5 = dot   x 2^5
                    pos 2 = dot   x 2^2    pos 6 = dot   x 2^6
                    pos 3 = empty x 2^3    pos 7 = empty x 2^7
                    
                    = 1*1 + 0*2 + 1*4 + 0*8 + 1*16 + 1*32 + 1*64 + 0*128
                    = 117 = 117th unicode braille cahracter"""
    index = 0
    if block[0]: index +=       1
    if block[1]: index +=       2
    if block[2]: index +=       4
    if block[3]: index +=       64
    if block[4]: index +=       8
    if block[5]: index +=       16
    if block[6]: index +=       32
    if block[7]: index +=       128
    return index

def index2str(matrix, line_end = "\n"):
    """Returns string with braille, based on [x,y] matrix
    of indexes."""
    m_w = len(matrix)
    m_h = len(matrix[0])
    result = ""
    for y in range(m_h):
        for x in range(m_w):
            result += mapBraille(matrix[x][y])
        result += line_end
    return result

def getBraille(in_file, encoding = "utf-8"):
    """Returns braille string, based on image in_file"""
    try:
        image = Image.open(in_file)
        res_img2bin         = img2bin(image,2,4)
        res_bin2index       = bin2index(res_img2bin,2,4)
        return index2str(res_bin2index,"\n").encode(encoding).strip()
        
    except:
        print("-ERROR- Problem opening image file:"+`in_file`)
        

def makeBraille(in_file,out_file = "braille_out.txt"):
    """Writes braille string based on image in_file to file out_file"""
    braille = getBraille(in_file)
    if not braille: print("\tNo braille, no write!");return False
    try:
        with open(out_file,"w") as file:
            file.write(braille)
        return "-SUCCESS- File "+`out_file`+" written to disk."
    except:
        error = ("-ERROR- Problem storing saving to file: "+`out_file`)
        return False, error

def printHelp(scriptname = "img2braille.py"):
    """Print out help when not wrong arguments and other situations."""
    helptext = "Script takes two arguments, argument one is "\
    " input image filename, second argument is output filename.\n"\
    "EXAMPLE use: "+scriptname+" image.gif text.txt"
    print(helptext)
    
#Main program if run from command line
if __name__ == "__main__":
    """First argument is source image, second argument is output file"""
    import sys
    def_filename_out = "img2braille_default_output.txt"

    
    if len(sys.argv) == 0: print("How did you get here?")
    elif len(sys.argv) == 1: printHelp(sys.argv[0])
    elif len(sys.argv) == 2: print(getBraille(sys.argv[1]))
    elif len(sys.argv) == 3: makeBraille(sys.argv[1], sys.argv[2])
    else: print("Error - too many arguments");printHelp(sys.argv[0])
