############################################################################
#                                                                          #
# lock()                            Version 2.0                            #
# Written by Craig Patchett         craig@patchett.com                     #
# Created 9/16/96                   Last Modified 3/28/97                  #
#                                                                          #
# Copyright 1997 Craig Patchett & Matthew Wright.  All Rights Reserved.    #
# This subroutine is part of The CGI/Perl Cookbook from John Wiley & Sons. #
# License to use this program or install it on a server (in original or    #
# modified form) is granted only to those who have purchased a copy of The #
# CGI/Perl Cookbook. (This notice must remain as part of the source code.) #
#                                                                          #
# Function:      Creates an exclusive lock for a file. The lock will       #
#                only work if other programs accessing the file are also   #
#                using this subroutine.                                    #
#                                                                          #
# Usage:         &lock($filename, $LOCK_DIR[, $MAX_WAIT]);                 #
#                                                                          #
# Variables:     $filename --   Name of file being locked.                 #
#                               Example "filename.html"                    #
#                $LOCK_DIR --   Path of directory to store lock files      #
#                               Should be "/tmp/" on UNIX sytems           #
#                               Example "/home/lockdir/"                   #
#                $MAX_WAIT --   Maximum seconds to wait if the file is     #
#                               already locked                             #
#                                                                          #
# Returns:       0 if successful                                           #
#                1 if $LOCK_DIR/$filename.tmp could not be created         #
#                2 if $filename is currently in use                        #
#                3 if lock file could not be created or opened             #
#                                                                          #
# Uses Globals:  $Error_Message for descriptive error messages             #
#                $NAME_LEN for maximum filename length                     #
#                                                                          #
# Files Created: Creates $LOCK_DIR/$filename.tmp                           #
#                Creates $LOCK_DIR/$filename.lok (exists only while file   #
#                  is locked)                                              #
#                                                                          #
############################################################################


sub lock {
    
    # Initialize variables
    
    local($filename, $LOCK_DIR, $MAX_WAIT) = @_; 
    local($wait, $lock_pid);
    local($temp_file) = "$LOCK_DIR$$.tmp";
    $Error_Message = '';
    
    local($lock_file) = $filename;
    $lock_file =~ tr/\/\\:.//d;         # Remove file separators/periods
    if ($NAME_LEN && ($NAME_LEN < length($lock_file))) {
        $lock_file = substr($lock_file, -$NAME_LEN);
    }
    $lock_file = "$LOCK_DIR$lock_file.lok";
    
    # Create temp file with PID
    
    if (!open(TEMP, ">$temp_file")) {
        $Error_Message = "Could not create $temp_file ($!).";
        return(1);
    }           
    print TEMP $$;
    close(TEMP);
    
    # Test for lock file
    
    if (-e $lock_file) {

        # Wait for unlock if lock file exists
        
        for ($wait = $MAX_WAIT; $wait; --$wait) {
            sleep(1);
            last unless -e $lock_file;
        }
    }
    
    # Check to see if there's still a valid lock
    
    if ((-e $lock_file) && (-M $lock_file < 0)) {
        
        # The file is still locked but has been modified since we started
                    
        unlink($temp_file);
        $Error_Message = "The file \"$filename\" is currently in use. Please try again later.";
        return(2);
    }
    else {

        # There is either no lock or the lock has expired
        
        if (!rename($temp_file, $lock_file)) { 

            # Problem creating the lock file
        
            unlink($temp_file);
            $Error_Message = "Could not lock file \"$filename\" ($!).";
            return(3);
        }
        
        # Check to make sure the lock is ours

        if (!open(LOCK, "<$lock_file")) {
            $Error_Message = "Could not verify lock for file \"$filename\" ($!).";
            return(3);
        }
        $lock_pid = <LOCK>;
        close(LOCK);        
        if ($lock_pid ne $$) { 
            $Error_Message = "The file \"$filename\" is currently in use. Please try again later.";
            return(2);
        }
        else { return(0) }
    }
}


############################################################################
#                                                                          #
# unlock()                          Version 2.0                            #
# Written by Craig Patchett         craig@patchett.com                     #
# Created 9/16/96                   Last Modified 3/28/97                  #
#                                                                          #
# Copyright 1997 Craig Patchett & Matthew Wright.  All Rights Reserved.    #
# This subroutine is part of The CGI/Perl Cookbook from John Wiley & Sons. #
# License to use this program or install it on a server (in original or    #
# modified form) is granted only to those who have purchased a copy of The #
# CGI/Perl Cookbook. (This notice must remain as part of the source code.) #
#                                                                          #
# Function:      Unlocks a file that has been locked using lock().         #
#                                                                          #
# Usage:         &unlock($filename, $LOCK_DIR);                            #
#                                                                          #
# Variables:     $filename --   Name of file being locked.                 #
#                               Example "filename.html"                    #
#                $LOCK_DIR --   Path of directory to store lock files      #
#                               Should be "/tmp/" on UNIX sytems           #
#                               Example "/home/lockdir/"                   #
#                                                                          #
# Returns:       0 if successful                                           #
#                1 if the lock file could not be deleted                   #
#                                                                          #
# Uses Globals:  $Error_Message for descriptive error messages             #
#                $NAME_LEN for maximum filename length                     #
#                                                                          #
# Files Created: Removes $LOCK_DIR/$filename.lok                           #
#                                                                          #
############################################################################


sub unlock {
    
    # Initialize variables
    
    local($filename, $LOCK_DIR) = @_;
    local($lock_file) = $filename;
    $Error_Message = '';
    
    $lock_file =~ tr/\/\\:.//d;         # Remove file separators/periods
    if ($NAME_LEN < length($lock_file)) {
        $lock_file = substr($lock_file, -$NAME_LEN);
    }
    $lock_file = "$LOCK_DIR$lock_file.lok";
    
    # Check to make sure the lock is ours

    if (!open(LOCK, "<$lock_file")) {
        $Error_Message = "Could not access the lock file for \"$filename\" ($!).";
        return(1);
    }
    $lock_pid = <LOCK>;
    close(LOCK);        
    if ($lock_pid ne $$) { 
        $Error_Message = "The file \"$filename\" is locked by another process.";
        return(2);
    }

    # Release the lock by unlinking the lock file
    
    if (!unlink($lock_file)) {
        $Error_Message = "Could not unlock file \"$filename\" ($!).";
        return(3);
    }
    return(0);
}

1;
