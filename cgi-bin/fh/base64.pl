############################################################################
#                                                                          #
# base64_encode_file()              Version 1.0                            #
# Written by Craig Patchett         craig@patchett.com                     #
# Created 9/30/96                   Last Modified 3/21/97                  #
#                                                                          #
# Copyright 1997 Craig Patchett & Matthew Wright.  All Rights Reserved.    #
# This subroutine is part of The CGI/Perl Cookbook from John Wiley & Sons. #
# License to use this program or install it on a server (in original or    #
# modified form) is granted only to those who have purchased a copy of The #
# CGI/Perl Cookbook. (This notice must remain as part of the source code.) #
#                                                                          #
# Function:      Convert a file to base64 format, as defined in RFC 1521   #
#                                                                          #
# Usage:         &base64_encode_file($file);                               #
#                                                                          #
# Variables:     $file -- Full pathname of file to be encoded.             #
#                         Example '/user/images/filename.gif'              #
#                                                                          #
# Returns:       String containing encoded data if successful              #
#                Null string if unsuccessful (file could not be opened)    #
#                                                                          #
# Uses Globals:  $Error_Message -- Sets to an error message if $file could #
#                                  not be opened.                          #
#                                                                          #
# Files Created: None                                                      #
#                                                                          #
############################################################################


sub base64_encode_file {

    # Initialize variables
    
    local($file) = $_[0];
    local($encoded, $line) = '';
    local($len, $bytes, $pad) = 0;
    
    # Open the file
    
    if (open (DATA, "<$file")) {

        # Process the data
        
        while ($bytes = read(DATA, $line, 45)) {
        
            $len += $bytes;
            
            # uuencode the line and remove the first and last characters
            
            $encoded .= substr(pack('u', $line), 1);
            chop($encoded);            
        }
        # Convert from uuencoded to base64
        
        $encoded =~ tr| -_`|A-Za-z0-9+/A|;
        $pad = (3 - ($len % 3)) % 3;
        substr($encoded, -$pad, $pad) = '=' x $pad;
        $encoded =~ s/(.{76})/$1\n/g;
    }
    else {
        $Error_Message = "The file \"$file\" could not be opened ($!).";
    }
        
    # Return the result (null if the file couldn't be opened)
    
    return($encoded);
}

1;
