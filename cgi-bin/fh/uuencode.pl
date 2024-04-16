############################################################################
#                                                                          #
# uuencode()                        Version 2.0                            #
# Written by Matthew Wright         mattw@worldwidemart.com                #
# Created 10/4/96                   Last Modified 4/7/97                   #
#                                                                          #
# Copyright 1997 Craig Patchett & Matthew Wright.  All Rights Reserved.    #
# This subroutine is part of The CGI/Perl Cookbook from John Wiley & Sons. #
# License to use this program or install it on a server (in original or    #
# modified form) is granted only to those who have purchased a copy of The #
# CGI/Perl Cookbook. (This notice must remain as part of the source code.) #
#                                                                          #
# Function:      Uuencodes a file.                                         #
#                                                                          #
# Usage:         &uuencode($filename);                                     #
#                                                                          #
# Variables:     $filename   --  Full path to file to uuencode             #
#                                Example "/path/to/filename.gif"           #
#                                                                          #
# Returns:       String containing uuencoded file data if successful       #                                           #
#                0 if specified file could no be opened                    #
#                                                                          #
# Uses Globals:  $Error_Message --  Set to text message if error           #
#                                                                          #
# Files Created: None                                                      #
#                                                                          #
############################################################################


sub uuencode {
    local($file) = @_;
    local($uuencoded_data, $line);
    
    if (open(ATTCH, $file)) {

        # Process the file
    
        while (read(ATTCH, $line, 45)) {
            $uuencoded_data .= pack("u", $line);
        } 
        close(ATTCH);
        return($uuencoded_data);
    }
    else {
        
        # Return error if file couldn't be opened
        
        $Error_Message = "Could not open uuencode attachment: $file ($!)";
        return('');
    }
}

1;
