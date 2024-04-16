#!/usr/local/bin/perl

###########################################################################
#                              cgi-lib.sol                                #
#                                                                         #
# This script was written by Selena Sol (selena@eff.org                   #
# http://www.eff.org/~erict) having been inspired by countless other      #
# perl authors.  Feel free to copy, cite, reference, sample, borrow or    #
# plagiarize the contents.  However, please let me know where it goes so  #
# that I can at least watch and take part in the development of the       #
# memes. Information wants to be free, support public domain freeware.    #
#                                                                         #
###########################################################################


###########################################################################
#                                 counter                                 #
###########################################################################

  sub counter
    {

# Assign to the local variable $counter_file, the filename that we passed 
# to this subroutine from the main script.

    local($counter_file) = @_;

# Open up the counter file.  If the counter file cannot be opened, 
# however, access the &open_error routine passing it the filename

    open (COUNTER_FILE, "$counter_file") || &open_error($counter_file);

# Check to see what number the counter is currently on and assign that 
# value to $_

    while (<COUNTER_FILE>)
      {
      $item_number = "$_";
      }
    close (COUNTER_FILE);

# Add one to that number, change the counter file to the new number, 
# return the number to the mian script, and close the counterfile.

    $item_number += 1;
    open (NOTE, ">$counter_file") || &open_error($counter_file);
    print NOTE "$item_number\n";
    close (NOTE);
    return $item_number;
    }

###########################################################################
#                               open_error                                #
###########################################################################

  sub open_error
    {

# Assign to the local variable $file_name, the filename that we passed
# to this subroutine from the referenceing routine.

    local ($filename) = @_;

# Let the client know that the script was unable to open the requested file
# and then die so that the routine does not continue

    print "I am really sorry, but for some reason I was unable to open
    <P>$filename<P>  Would you please make sure that the filename is
    correctly defined in define_variables.pl, actually exists, and has the
    right permissions relative to the web browser.  Thanks!";
    die;
    }

###########################################################################
#                               header_tags                               #
###########################################################################

  sub header_tags
    {
    local ($title) = @_;
    $header_tags = "<HTML>\n<HEAD>\n<TITLE>$title</TITLE>\n</HEAD>\n";
    return $header_tags;
    }

###########################################################################
#                           table_header                                  #
###########################################################################

  sub table_header
    {

# Assign to the local variable $file_name, the filename that we passed
# to this subroutine from the referenceing routine.

    local (@headings) = @_;
    local ($table_header);

# Now dump the HTML arguments into the $table_tag variable.

    foreach $table_field (@headings)
      {
      $table_header .= "<TH>$table_field</TH>\n";
      }
    $table_header .= "\n";
    return $table_header;
    }

###########################################################################
#                           select_tag                                    #
###########################################################################

  sub select_tag
    {

# Assign to the local variable $file_name, the filename that we passed
# to this subroutine from the referenceing routine.

    local ($name, $size, $multiple) = @_;
    local ($select_tag, $select_argument);
    local (@select_arguments, @select_values, %SELECT_ARGUMENTS);
    %SELECT_ARGUMENTS = ("NAME", "$name",
                         "SIZE", "$size",
  		     	 "MULTIPLE", "$multiple");
    @select_arguments = keys %SELECT_ARGUMENTS;
    @select_values = values %SELECT_ARGUMENTS;
    $select_tag = "";
    $select_argument = "";

# Now dump the HTML arguments into the $table_tag variable.

    $select_tag .= "<SELECT ";
    foreach $select_argument (@select_arguments)
      {
      if ($select_argument eq "multiple")
        {
        $select_tag .= "MULTIPLE ";
        }    
      elsif ($SELECT_ARGUMENTS{$select_argument} ne "")
        {
        $select_tag .= "$select_argument = \"$SELECT_ARGUMENTS{$select_argument}\" ";
        }
      }
    $select_tag .= ">\n";
    return $select_tag;
    }

###########################################################################
#                        select_options                                   #
###########################################################################

  sub select_options
    {

# Assign to the local variable $file_name, the filename that we passed
# to this subroutine from the referenceing routine and initialize $table.

    local (@select_options) = @_;
    local ($select_options);
    $select_options = "";

# Add the categories that we were sent from the referring routine to the
# Select Box, making sure to select the first of the categories

    foreach $option (@select_options)
      {
      $select_options .= "<OPTION>$option\n";
      }

# Complete the HTML necessary for the Category select table and return
# the variable to be printed out by the main routine.

    $select_options .= "</SELECT>\n";
    return $select_options;
    }

###########################################################################
#                         build_input_form                                #
###########################################################################

  sub build_input_form
    {

# Assign to the local variable $file_name, the filename that we passed
# to this subroutine from the referenceing routine.

    local ($variable_name, $form_type, $field_name) = @_;
    local ($input_form);
    $input_form = "";

    $input_form .= "<TR>\n";
    $input_form .= &table_header ("$field_name");
    $input_form .= "<TD>";
    $input_form .= &make_form_row ("$field_name", "$variable_name", 
                                     "$form_type");
    $input_form .= "</TD></TR>\n";
    return $input_form;
    }

###########################################################################
#                           make_form_row                                 #
###########################################################################

  sub make_form_row
    {

# Assign to the local variable $file_name, the filename that we passed
# to this subroutine from the referenceing routine.

    local ($name, $variable_name, $type) = @_;
    local (@options_and_arguments);
    @options_and_arguments = ();
    ($type, @options_and_arguments) = split(/\|/, $type);
    local ($form_row);
    $form_row = "";

    if ($type eq "text")
      {
      $form_row .= "<INPUT TYPE = \"text\" NAME = \"$variable_name\" ";
      foreach $argument (@options_and_arguments)
        {
        $form_row .= "$argument ";
        }
        $form_row .= ">";
      }

    if ($type eq "textarea")
      {
      $form_row .= "<TEXTAREA NAME = \"$variable_name\" "; 
      foreach $argument (@options_and_arguments)
        {
        $form_row .= "$argument ";
        }
        $form_row .= "></TEXTAREA>";
      }

    if ($type eq "invisible")
      {
      $form_row .= "$item_number";
      }

    if ($type eq "select")
      {
      $number = shift (@options_and_arguments);
      $multiple = shift (@options_and_arguments);
      $form_row .= &select_tag("$variable_name", "$number");
          
      $form_row .= &select_options(@options_and_arguments);
      $form_row .= "</SELECT>";
      }
    return $form_row;
    }

###########################################################################
#                      get_database_rows                                  #
###########################################################################

  sub get_database_rows
    {
    local ($datafile, @keywords) = @_;
    open (DATABASE, "$datafile");
    while (<DATABASE>)
      {
      unless ($_ =~ /^COMMENT:/)
        {
        push (@database_rows, $_);
        }
      }
    @database_rows;
    close (DATABASE);
    }

###########################################################################
#                           table_rows                                    #
###########################################################################

  sub table_rows
    {

# Assign to the local variable $file_name, the filename that we passed
# to this subroutine from the referenceing routine.

    local (@row) = @_;
    local ($table_cell);

# Now dump the HTML arguments into the $table_tag variable.

    foreach $table_field (@row)
      {
      $table_field =~ s/~~/\|/g;
      $table_cell .= "<TD>$table_field</TD>\n";
      }
    $table_cell .= "\n";
    return $table_cell;
    }

#######################################################################
#                            GetFileLock                              #
#######################################################################

sub GetFileLock {  
    local ($lock_file) = @_;

    local ($endtime);  
    $endtime = 60;
    $endtime = time + $endtime;
#   We set endtime to wait 60 seconds

    while (-e $lock_file && time < $endtime) {
        # Do Nothing
    }
    open(LOCK_FILE, ">$lock_file");    
#    flock(LOCK_FILE, 2); # 2 exclusively locks the file
} # end of get_file_lock

#######################################################################
#                            ReleaseFileLock                          #
#######################################################################

sub ReleaseFileLock {
    local ($lock_file) = @_;
       
# 8 unlocks the file
#    flock(LOCK_FILE, 8);
    close(LOCK_FILE);
    unlink($lock_file);

} # end of ReleaseFileLock   

#######################################################################
#                            EncryptWrap                              #
#######################################################################

 
sub EncryptWrap {
    local ($field, $salt) = @_;
 
    $field = crypt ($field, $salt);
 
    $field;
 
} # end of encrypt

1;


