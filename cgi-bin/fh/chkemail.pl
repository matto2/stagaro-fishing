############################################################################
#                                                                          #
# email_check()                     Version 1.0                            #
# Written by Matthew Wright         mattw@worldwidemart.com                #
# Created 8/1/96                    Last Modified 3/23/97                  #
#                                                                          #
# Copyright 1997 Craig Patchett & Matthew Wright.  All Rights Reserved.    #
# This subroutine is part of The CGI/Perl Cookbook from John Wiley & Sons. #
# License to use this program or install it on a server (in original or    #
# modified form) is granted only to those who have purchased a copy of The #
# CGI/Perl Cookbook. (This notice must remain as part of the source code.) #
#                                                                          #
# Function:      Checks an email address to see if it passes a simple      #
#                syntax check. (This routine will not check to see if the  #
#                address is an actual address.)                            #
#                                                                          #
# Usage:         &email_check($email_address);                             #
#                                                                          #
# Variables:     $email_address -- String containing the address to check  #
#                                  Example: 'someone@somewhere.com'        #
#                                                                          #
# Returns:       0 if the email address is invalid                         #
#                1 if the address is in a valid format                     #
#                                                                          #
# Uses Globals:  None                                                      #
#                                                                          #
# Files Created: None                                                      #
#                                                                          #
############################################################################


sub email_check {
    local($email) = $_[0];

    # Check that the email address doesn't have 2 @ signs, a .., a @., a 
    # .@ or begin or end with a .

    if ($email =~ /(@.*@)|(\.\.)|(@\.)|(\.@)|(^\.)|(\.$)/ || 

        # Allow anything before the @, but only letters numbers, dashes and 
        # periods after it.  Also check to make sure the address ends in 2 or 
        # three letters after a period and allow for it to be enclosed in [] 
        # such as [164.104.50.1]
    
        ($email !~ /^.+\@localhost$/ && 
         $email !~ /^.+\@\[?(\w|[-.])+\.[a-zA-Z]{2,3}|[0-9]{1,3}\]?$/)) {
        return(0);
    }

    # If it passed the above test, it is valid.
    
    else {
        return(1);
    }
}

1;
