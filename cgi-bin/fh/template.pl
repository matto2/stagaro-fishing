############################################################################
#                                                                          #
# parse_template()                  Version 2.0                            #
# Written by Craig Patchett         craig@patchett.com                     #
#    and Matthew Wright             mattw@worldwidemart.com                #
# Created 9/9/96                    Last Modified 4/6/97                   #
#                                                                          #
# Copyright 1997 Craig Patchett & Matthew Wright.  All Rights Reserved.    #
# This subroutine is part of The CGI/Perl Cookbook from John Wiley & Sons. #
# License to use this program or install it on a server (in original or    #
# modified form) is granted only to those who have purchased a copy of The #
# CGI/Perl Cookbook. (This notice must remain as part of the source code.) #
#                                                                          #
# Function:      Searches a file for variables identified as <<VARIABLE>>  #
#                and substitutes the value with the corresponding key from # 
#                the global associative arrays %VAR, %CONFIG, %FORM, or    #
#                %ENV (the arrays are checked in this order). Lines in the #
#                file beginning with '0:' will only be printed if a        #
#                variable appears on that line and has a value in one of   #
#                the four arrays.                                          #
#                                                                          #
# Usage:         &parse_template($template_file, *FILEHANDLE);             #
#                                                                          #
# Variables:     $template_file --  Full path to file containing template  # 
#                                   Example "/directory/file"              #
#                *FILEHANDLE --     Reference to filehandle to write       #
#                                   parsed file to.                        #
#                                   Example *FILE, *STDOUT                 #
#                                                                          #
# Returns:       0 if $template_file could not be opened                   #
#                1 if successful                                           #
#                                                                          #
# Uses Globals:  %VAR --            Miscellaneous variables assoc array    #
#                %CONFIG --         Configuration variables assoc array    #
#                %FORM --           Form variables assoc array             #
#                %ENV --            Environment variables assoc array      #
#                $Error_Message --  Set to text message if error           #
#                                                                          #
# Files Created: None, but the parsed file is written to FILEHANDLE        #
#                                                                          #
############################################################################


sub parse_template {
    local($template_file, *OUT) = @_;
    local($line, $line_copy, $changes);

    # Open the template file and parse each line
    
    if (!open(TEMPLATE, $template_file)) { 
        $Error_Message = "Could not open $template_file ($!).";
        return(0);
    }
    while ($line = <TEMPLATE>) {

        # Initialize our variables
        
        $line_copy = '';
        $changes = 0;
        
        # Search for variables in the current line
        
        while ($line =~ /<<([^>]+)>>/) {
            
            # Build up the new line with the section of $line prior to the 
            # variable and the value for $var_name (check %VAR, %CONFIG,
            # %FORM, then %ENV for match)
        
            ++$changes;
            if ($VAR{$1}) { $line_copy .= $` . $VAR{$1} }
            elsif ($CONFIG{$1}) { $line_copy .= $` . $CONFIG{$1} }
            elsif ($FORM{$1}) { $line_copy .= $` . $FORM{$1} }
            elsif ($ENV{$1}) { $line_copy .= $` . $ENV{$1} }
            else {
                --$changes;
                $line_copy .= $`;
            }
                 
            # Change $line to the section of $line after the variable
                
            $line = $';
        }
        
        # Set $line according to whether or not any matches were found
            
        $line = $line_copy ? $line_copy . $line : $line;
        
        # Print line depending on presence of 0: and variables existing
         
        if (($line !~ s/^0://) || !$line_copy || $changes) {
            print OUT $line;
        }
    }
    close(TEMPLATE);
    return(1);
}

1;
