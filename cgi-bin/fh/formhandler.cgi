#!/usr/bin/perl

############################################################################
#                                                                          #
# FormHandler                       Version 2.0                            #
# Written by Matthew Wright         mattw@worldwidemart.com                #
# Created 05/31/96                  Last Modified 3/6/97                   #
#                                                                          #
# Copyright 1997 Craig Patchett & Matthew Wright.  All Rights Reserved.    #
# This program is part of The CGI/Perl Cookbook from John Wiley & Sons.    #
# License to use this program or install it on a server (in original or    #
# modified form) is granted only to those who have purchased a copy of The #
# CGI/Perl Cookbook. (This notice must remain as part of the source code.) #
#                                                                          #
############################################################################


############################################################################
# Define configuration constants                                           #
############################################################################

# @REFERERS contains the host names and IP addresses of the domains which
# are allowed to use this copy of FormHandler to parse their forms.

@REFERERS = ('stagnaros.com');

# @ALLOWED_ATTACH_DIRS is an array which specifies which directories 
# people can attach files from.  By default, this is set to all, however 
# if people should only be able to attach files from a directory such as 
# /users, set this variable to: @ALLOWED_ATTACH_DIRS = ('/users/');
# Comment this out if you only wish to use @RESTRICTED_ATTACH_DIRS

#@ALLOWED_ATTACH_DIRS = ('');

# @RESTRICTED_ATTACH_DIRS is an array which specifies directories on the 
# server which files cannot be attached from.  By default this is set to 
# /etc, since no one should be able to attach a file such as 
# /etc/passwd.

@RESTRICTED_ATTACH_DIRS = ('/etc/');

# %CONFIG defines which form fields should be considered configuration
# fields rather than standard data fields. Each of the default variables
# defined in the array below have special meaning to FormHandler and are
# usually set using hidden fields. Default values used in the array will
# be overridden by form fields with the same name. Any variable that should
# be considered a configuration variable must be defined in this array.

%CONFIG = ('recipient', '',                    'subject', '', 
           'email', '',                        'realname', '', 
           'first_name', '',                   'last_name', '', 
           'field_names', '',                  'sort', '', 
           'print_config', '',                 'env_report', '', 
           'redirect', '',                     'required', '', 
           'error_html_template', '',          'success_html_template', '', 
           'email_template', '',               'reply_message_template', '', 
           'reply_message_attach', '',         'reply_message_subject', '', 
           'reply_message_from', '',           'log_template', '', 
           'log_filename', '',                 'log_fields', '', 
           'log_delimiter', '||',              'log_uid', '', 
           'bcc', '',                          'cc', '', 
           'mail_list', '');

# This is host name of your web server.  If the name of your web server is
# host.xxx, set this to 'host.xxx'.

$WEB_SERVER = 'vom.com';

# This is the server name of your SMTP server.  For example, if your service
# provider is host.net, try setting this to host.net or smtp.host.net

$SMTP_SERVER = 'smtp.vom.com';

# $LOCK_DIR is the default directory where all lock files will be 
# placed.

$LOCK_DIR = '/home/domains/stagnaros_com/tmp/';

# $MAX_WAIT is the max number of seconds the lock script will wait 
# before overiding the lock file.

$MAX_WAIT = 5;

# $REQUIRE_DIR is the directory in which all of your required files are
# placed.  On most systems, if you leave the required files in the same
# directory as the CGI script, you can leave this variable blank.  
# Otherwise, if you move the required files to another directory, specify
# the full path here.

$REQUIRE_DIR = '';


############################################################################
# Get Required subroutines which need to be included.                      #
############################################################################

# Push the $REQUIRE_DIR onto the @INC array for include file directories.

push(@INC, $REQUIRE_DIR) if $REQUIRE_DIR;

# Require Necessary Routines for this script to run.

require 'parsform.pl';
require 'locksubs.pl';
require 'template.pl';
require 'base64.pl';
require 'uuencode.pl';
require 'sendmail.pl';
require 'chkemail.pl';
require 'formdate.pl';


############################################################################
# Check that the form is coming from a web site that is included in the    #
# @REFERERS array.  If not, sent out an error.  Otherwise, continue with   #
# the script.                                                              #
############################################################################

# Set the flag to 0 so the referer will fail by default.

$check_referer = "0";

# Get the hostname out of the referring URL.  If there is no 
# referring URL, set flag to 1, since some browsers don't pass the 
# HTTP_REFERER environment variable.

if ($ENV{'HTTP_REFERER'} =~ m#http://([^/]+)#) {
    $hostname = $1;
}
else {
    $check_referer = 1;
}

# If there is a hostname found, check it against the hostnames in the 
# @REFERERS array until a match is found.  Set flag to 1 if match is 
# found.

if ($hostname) {
    foreach $referer (@REFERERS) {
        if ($hostname =~ /$referer/i) {
            $check_referer = 1;
            last;
        }
    }
}

# If flag is not set to 1, throw an error to the &error subroutine.

if (!$check_referer) {
    &error("$ENV{'HTTP_REFERER'} is not allowed access to this program.");
}


############################################################################
# Parse the form contents and put configuration fields into %CONFIG and    #
# other fields in %FORM.  This is an external subroutine which was required#
############################################################################

if (!&parse_form) {
    &error($Error_Message);
}


############################################################################
# If the field names configuration field has been filled in, parse it and  #
# define field names which may be used later in the script.                #
############################################################################

if ($CONFIG{'field_names'}) {
    @field_names = split(/&/, $CONFIG{'field_names'});

    # For each of the field names specified in the field_names form 
    # field, split the old name and new name by = sign and then set the new 
    # names in the %ALT_NAME array.
    
    foreach $field_name (@field_names) {
        ($def_name, $def_value) = split(/=/, $field_name);
        $ALT_NAME{$def_name} = $def_value;
    }
}


############################################################################
# Check any fields which may be required with the 'required' configuration #
# variable.  Also check e-mail addresses to make sure they are semi-valid. #
############################################################################

# Check the email field and if it contains an obviously bad e-mail 
# address, simply set the field blank, so that things like auto-reply 
# will not bother sending to a bad address.  Also, if this is blank 
# and the user has required this field, an error will be thrown later 
# on, when it loops through all required fields.

if (!&email_check($CONFIG{'email'})) {
    $CONFIG{'email'} = "";
}

# Since recipient field is required to be a valid e-mail address or 
# be set to 'none', this checks that it is.

if (!&email_check($CONFIG{'recipient'}) && $CONFIG{'recipient'} !~ /^none$/i) {
    push(@missing_required_fields, "recipient (invalid address format)");
}

# Split required fields by commas in the 'required' configuration field.

@required = split(/,/, $CONFIG{'required'});

# For each of the form fields specified in the @required array, 
# determined from the required form field, make sure it is not 
# blank.  Push any blank fields onto the w@missing_required_fields array.

foreach $required (@required) {
    if (!($CONFIG{$required}) && !($FORM{$required})) {
        push(@missing_required_fields, $required);
    }
}

# If the @missing_required_fields array exists, then thrown an error.

if (@missing_required_fields) {
    &error('missing_required_fields');
}


############################################################################
# Get dates for use in templates and logs.                                 #                
############################################################################

# Get the current time in seconds.

$current_time = time;

# Set the date field in the %CONFIG array for use in templates.

$CONFIG{'date'} = &format_date($current_time, "<weekday>, <month> <d>, <year> at <mtimesec>");

# Create a log_date for use in the logs.  If the delimiter specified 
# was : or / then use - as the delimiter.  Otherwise specify in normal 
# clock and date format.

if ($CONFIG{'log_delimiter'} ne ':' && $CONFIG{'log_delimiter'} ne '/') {
    $CONFIG{'log_date'} = &format_date($current_time, "<mtimesec> <0m>/<0d>/<yr>");
}
else {
    $CONFIG{'log_date'} = "<mh>-<0n>-<0s> <0m>-<0d>-<yr>"; 
}


############################################################################
# If there are any users we are sending a carbon copy or a blind carbon    #
# copy to, define them here.  Also, if this is a mailing list, define all  #
# of the users.                                                            #
############################################################################

# Define any multiple users we might send this message to.

if ($CONFIG{'cc'} || $CONFIG{'bcc'} || $CONFIG{'mail_list'}) {

    # If the cc form field contains a reference to a file, open up the 
    # file, read in the addresses, check each one to make sure it is valid 
    # and then add it to the new cc config field containing a list of 
    # all Carbon Copy recipients of the message.
    
    if ($CONFIG{'cc'} =~ /file:(.+)/) {
        $cc_file = $1;
        $CONFIG{'cc'} = '';
        
        open(CC, $cc_file) 
          || &error("Couldn't open file $cc_file ($!).");
        while (<CC>) {
            chop if /\n$/;
            @cc_addresses = split(/,/, $_);
            foreach $cc_address (@cc_addresses) {
                if (&email_check($cc_address)) {
                    $CONFIG{'cc'} .= "$cc_address,";
                }
            }
        }
        chop $CONFIG{'cc'};
        close(CC);
    }
    
    # Otherwise, if the cc form field contains a list of carbon copy 
    # recipients, split them by commas and then pseudo-verify each address.  
    # Add all verified addresses back into the config field.
    
    elsif ($CONFIG{'cc'}){
        @cc_addresses = split(/,/, $CONFIG{'cc'});
        $CONFIG{'cc'} = '';
        foreach $cc_address (@cc_addresses) {
            if (&email_check($cc_address)) {
                $CONFIG{'cc'} .= "$cc_address,";
            }
        }
        chop $CONFIG{'cc'};
    }       
    
    # If the bcc form field contains a reference to a file, open up the 
    # file, read in the addresses, check each one to make sure it is valid 
    # and then add it to the new bcc config field containing a list of 
    # all Blind Carbon Copy recipients of the message.
    
    if ($CONFIG{'bcc'} =~ /file:(.+)/) {
        $bcc_file = $1;
        $CONFIG{'bcc'} = '';
        
        open(BCC, $bcc_file) 
          || &error("Couldn't open file $bcc_file ($!).");
        while (<BCC>) {
            chop if /\n$/;
            @bcc_addresses = split(/,/, $_);
            foreach $bcc_address (@bcc_addresses) {
                if (&email_check($bcc_address)) {
                    $CONFIG{'bcc'} .= "$bcc_address,";
                }
            }
        }
        chop $CONFIG{'bcc'};
        close(BCC);
    }
    
    # Otherwise, if the bcc form field contains a list of carbon copy 
    # recipients, split them by commas and then pseudo-verify each  
    # address. Add all verified addresses back into the config field.
    
    elsif ($CONFIG{'bcc'}) {    
        @bcc_addresses = split(/,/, $CONFIG{'bcc'});
        $CONFIG{'bcc'} = '';
        foreach $bcc_address (@bcc_addresses) {
            if (&email_check($bcc_address)) {
                $CONFIG{'bcc'} .= "$bcc_address,";
            }
        }
        chop $CONFIG{'bcc'};
    }   

    # If the mail_list form field contains a reference to a file, open up 
    # the file, read in the addresses, check each one to make sure it is 
    # valid and then add it to the new mail_list config field containing a 
    # list of all mail list recipients of the message.
    
    if ($CONFIG{'mail_list'} =~ /file:(.+)/) {
        $list_file = $1;
        $CONFIG{'mail_list'} = '';
        
        open(LIST, $list_file) 
          || &error("Couldn't open $list_file ($!).");
        while (<LIST>) {
            chop if /\n$/;
            @list_addresses = split(/,/, $_);
            foreach $list_address (@list_addresses) {
                if (&email_check($list_address)) {
                    $CONFIG{'mail_list'} .= "$list_address,";
                }
            }
        }
        chop $CONFIG{'mail_list'};
        close(LIST);
    }
    
    # Otherwise, if the mail_list form field contains a list of message 
    # recipients, split them by commas and then pseudo-verify each 
    # address. Add all verified addresses back into the config field.
    
    elsif ($CONFIG{'mail_list'}) {   
        @list_addresses = split(/,/, $CONFIG{'list'});
        $CONFIG{'mail_list'} = '';
        foreach $list_address (@list_addresses) {
            if (&email_check($list_address)) {
                $CONFIG{'mail_list'} .= "$list_address,";
            }
        }
        chop $CONFIG{'mail_list'};
    }
}


############################################################################
# Send Form Results through E-Mail to the recipient.  If a template is     #
# defined, use that to send the message.  Otherwise, send a generic        #
# response.                                                                #
############################################################################

# Determine who the message is from.
    
if ($CONFIG{'realname'} && $CONFIG{'email'}) {
    $from = "($CONFIG{'realname'}) $CONFIG{'email'}";
}
elsif (($CONFIG{'first_name'} || $CONFIG{'last_name'}) && $CONFIG{'email'}) {
    $from = "($CONFIG{'first_name'} $CONFIG{'last_name'}) $CONFIG{'email'}";
}
elsif ($CONFIG{'email'}) {
    $from = $CONFIG{'email'};
}
else {
    $from = "anonymous\@$ENV{'REMOTE_HOST'}";
}

# Determine the message subject

if ($CONFIG{'subject'}) {
    $subject = $CONFIG{'subject'};
}               
else {
    $subject = "FormHandler Results";
}

# Prepare the generic results message
        
if ((!$CONFIG{'email_template'}  
        && ($CONFIG{'recipient'} !~ /^none$/i || $CONFIG{'mail_list'}))
        || !($CONFIG{'redirect'} || $CONFIG{'success_html_template'})) {
    $results = "The following information was submitted by\n";
    $results .= "$from on $CONFIG{'date'}\n";
    $results .= ('-' x 75) . "\n\n";

    # If any print_config fields are defined, print the corresponding 
    # FormHandler configuration fields to the e-mail message.
    
    if ($CONFIG{'print_config'}) {
        @print_config = split(/,/, $CONFIG{'print_config'});
        foreach $print_config (@print_config) {
        
            # If field names have been specified for these config fields, 
            # make sure they get printed into the e-mail.
            
            if ($CONFIG{$print_config} && $ALT_NAME{$print_config}) {
                $results .= "$ALT_NAME{$print_config}: $CONFIG{$print_config}\n";
            }
            elsif ($CONFIG{$print_config}) {
                $results .= "$print_config: $CONFIG{$print_config}\n";
            }
        }
        $results .= "\n";
    }
    
    # Sort the fields if so specified
    
    if ($CONFIG{'sort'} eq 'alphabetic') {
        @sorted_fields = sort keys %FORM;
    }
    elsif ($CONFIG{'sort'} =~ /^order:(.+)/) {
        @sorted_fields = split(/,/, $1);
    }
    else {
        @sorted_fields = keys %FORM;
    }
    
    # Print the fields in the appropriate order.

    foreach $sorted_field (@sorted_fields) {
    
        # Print the name and value pairs in FORM array.
        
        if ($ALT_NAME{$sorted_field} && $FORM{$sorted_field}) {
            $results .= "$ALT_NAME{$sorted_field}: $FORM{$sorted_field}\n";
        }
        elsif ($FORM{$sorted_field}) {
            $results .= "$sorted_field: $FORM{$sorted_field}\n";
        }
        $SORTED_FIELD{$sorted_field} = 1;
    }
    $results .= "\n";
    
    # Print any additional fields not included in the sort order
            
    foreach $field_name (keys %FORM) {
        if (!$SORTED_FIELD{$field_name}) {
            if ($ALT_NAME{$field_name}) {
                $results .= "$ALT_NAME{$field_name}: $FORM{$field_name}\n";
            }
            else {
                $results .= "$field_name: $FORM{$field_name}\n";
            }
        }
    }    
    $results .= "\n" . ('-' x 75) . "\n\n";

    # Print Any Environment Variables that were specified.
    
    foreach $env_variable (split(/,/, $CONFIG{'env_report'})) {
        $results .= "$env_variable: $ENV{$env_variable}\n";
    }
}

# Determine how to format the message

if ($CONFIG{'email_template'} && &valid_directory($CONFIG{'email_template'})) {
    $message = $CONFIG{'email_template'};
}
elsif ($CONFIG{'recipient'} !~ /^none$/i || $CONFIG{'mail_list'}) {
    $message = $results;
}

# Send the message(s)

if ($CONFIG{'recipient'} !~ /^none$/i) {
    if (&send_email($subject, $from, $CONFIG{'recipient'}, $CONFIG{'cc'},  
                    $CONFIG{'bcc'}, $message, '', '')) {
        &error($Error_Message);
    }
}
foreach $recipient (split(/,/, $CONFIG{'mail_list'})) {
    if (&send_email($subject, $from, $recipient, $CONFIG{'cc'}, 
                    $CONFIG{'bcc'}, $message, '', '')) {
        &error($Error_Message);
    }
}


############################################################################
# This sends out a reply message and/or it's file attachments.             #
############################################################################

if (($CONFIG{'reply_message_template'} || $CONFIG{'reply_message_attach'}) 
  && $CONFIG{'email'}) {

    # Determine who the message is going to.
    
    $to = $from;

    # Determine who the reply message is from. Default to recipient if no 
    # one is speicified.
    
    if ($CONFIG{'reply_message_from'}) {
        $from = $CONFIG{'reply_message_from'};
    }
    else {
        $from = $CONFIG{'recipient'};
    }

    # Determine the subject for the reply message
    
    if ($CONFIG{'reply_message_subject'}) {
        $subject = $CONFIG{'reply_message_subject'};
    }
    else {
        $subject = "FormHandler Reply Message";
    }

   # If attachments are specified, prepare the file and encoding arrays.
    
    if ($CONFIG{'reply_message_attach'}) {
        local(@attachments) = split(/,/, $CONFIG{'reply_message_attach'});
        foreach $attachment (@attachments) {
            if ($attachment =~ /^(text|uuencode|mime):(.+)$/) {
                $filetype = $1;
                $filename = $2;

                # If the file is allowed to be attached, go ahead and add 
                # it to both arrays.
                
                if (&valid_directory($filename)) {
                    push(@files, $filename);
                    if ($filetype eq 'mime') { push(@encoding, 'base64') }
                    else { push(@encoding, $filetype) }
                }
            }
        }
     
        # Join the arrays together with commas into variables for passing to 
        # the send_email routine.
        
        $file = join(',', @files);
        $encoding = join(',', @encoding);
    }
    
    # If there is a reply message template, use it as the body, 
    # otherwise, just send the attachments that were requested.
    
    if (&send_email($subject, $from, $to, '', '', 
                    $CONFIG{'reply_message_template'}, $file, $encoding)) {
        &error($Error_Message);
    }
}


############################################################################
# Log Response if a log filename and either log fields or log template are #
# given.                                                                   #
############################################################################

if ($CONFIG{'log_filename'} 
  && ($CONFIG{'log_fields'} || $CONFIG{'log_template'})) {

    # Make sure the log file is in a valid directory
    
    if (!&valid_directory($CONFIG{'log_filename'})) {
        &error("$CONFIG{'log_filename'} is in a restricted directory.");
    }
    
    # If they wish to use unique log id's, open the log file, read it in, 
    # increment it, and store it in the log_uid config variable so they can 
    # use it in templates.
    
    if ($CONFIG{'log_uid'}) {

        # Make sure the log uid file is in a valid directory
        
        if (!&valid_directory($CONFIG{'log_uid'})) {
            &error("$CONFIG{'log_uid'} is in a restricted directory.");
        }
        
        # Save the name of the log uid file so we can replace it in 
        # %CONFIG with the actual uid.
    
        $log_uid_file = $CONFIG{'log_uid'};
        $CONFIG{'log_uid'} = '';
    
        # Lock the log uid file so we can overwrite it.
        
        if (&lock($log_uid_file, $LOCK_DIR, $MAX_WAIT)) {
            &error($Error_Message); 
        }
        
        # Open the log uid file, and if we can't, then create it.
        
        if (open(LOG_UID, $log_uid_file)) {
            $previous_uid = <LOG_UID>;
            chop($previous_uid) if ($previous_uid =~ /\n$/);
            $CONFIG{'log_uid'} = ++$previous_uid;
            close(LOG_UID);
            
            # Update the log uid file
            
            open(LOG_UID, ">$log_uid_file") 
              || &error("Can't update $log_uid_file ($!).");
            print LOG_UID "$CONFIG{'log_uid'}";
        }
        else { 
            open(LOG_UID, ">$log_uid_file") 
              || &error("Can't create $log_uid_file ($!).");
            print LOG_UID 1;
            $CONFIG{'log_uid'} = 1;
        }
        
        # Close and unlock the file
        
        close(LOG_UID);
        &unlock($log_uid_file, $LOCK_DIR);
    }
     
    # Lock the log file and open it for appending.
        
    if (&lock($CONFIG{'log_filename'}, $LOCK_DIR, $MAX_WAIT)) {
        &error($Error_Message); 
    }
    open(LOG, ">>$CONFIG{'log_filename'}")
      || &error("Could not open $CONFIG{'log_filename'} ($!).");
    
    if ($CONFIG{'log_template'} && &valid_directory($CONFIG{'log_template'})) {
    
        # If they have a template for the logging routine, parse the template
    
        &parse_template($CONFIG{'log_template'}, *LOG)
            || &error("Could not open $CONFIG{'log_template ($!).'}");
    }
    else {
    
        # Otherwise, use the log_delimiter and log_fields to determine what 
        # fields to log and what separator to use.  Then write a new log entry. 
           
        @log_fields = split(/,/, $CONFIG{'log_fields'});
        $num_fields = @log_fields;

        if ($CONFIG{'log_delimiter'}) {
            $log_delimiter = $CONFIG{'log_delimiter'};
        }
        else {
            $log_delimiter = "\t";
        }

        # If they are using a unique user id, LOG that.
        
        if ($CONFIG{'log_uid'}) {
            print LOG "$CONFIG{'log_uid'}$log_delimiter";
        }

        # Log the rest of the fields that were in the @log_fields array 
        
        for ($field_num = 0; $field_num < $num_fields; $field_num++) {
            if ($CONFIG{$log_fields[$field_num]}) {
                print LOG $CONFIG{$log_fields[$field_num]};
            }
            else {
                print LOG $FORM{$log_fields[$field_num]};
            }
            print LOG $log_delimiter if ($field_num < $num_fields - 1);
        }
        print LOG "\n";
    }
    
    # Close and unlock the log file
       
    close(LOG);
    &unlock($CONFIG{'log_filename'}, $LOCK_DIR);
}


############################################################################
# Send back HTML response.  If redirection is used, redirect user to the   #
# URL.  If there is a template being used, parse it and send it to the user#
# or send out a generic response if neither of the above is defined.       #
############################################################################

if ($CONFIG{'redirect'}) {

    # Print Redirect Header.
    
    print "Location: $CONFIG{'redirect'}\n\n";
}
elsif ($CONFIG{'success_html_template'} 
       && &valid_directory($CONFIG{'success_html_template'})) {

    # Print Success HTML Header and the template.
    
    print "Content-type: text/html\n\n";
    if (!&parse_template($CONFIG{'success_html_template'}, *STDOUT)) {
        &error("Can't open $CONFIG{'success_html_template'} ($!).");
    }
}
else {

    # Print a Generic Success HTML Page.
    
    print <<HTML_END;
Content-type: text/html

<HTML>
    <HEAD>
        <TITLE>FormHandler Results</TITLE>
    </HEAD>
    <BODY BGCOLOR=#FFFFFF TEXT=#000000>
       <CENTER>
       <H1>FormHandler Results</H1>
       </CENTER>
       Thank you. Below is a summary of your submission.
       <P>
       <PRE>
$results
       </PRE>
    </BODY>
</HTML>
HTML_END
}
exit;


############################################################################
# Make sure file is in valid directory. (Local Subroutine)                 #
############################################################################

sub valid_directory {
    
    local ($filename) = $_[0];
    local ($allowed_path, $restricted_path);
    
    local($valid_dir) = 0;
    if ($ALLOWED_ATTACH_DIRS[0] =~ /^all$/i) { $valid_dir = 1 }
    else {
        foreach $allowed_path (@ALLOWED_ATTACH_DIRS) {
            $valid_dir = ($filename =~ /^$allowed_path/);
            last if $valid_dir;
        }
    }

    foreach $restricted_path (@RESTRICTED_ATTACH_DIRS) {
        $valid_dir = ($filename !~ /^$restricted_path/);
        last if !$valid_dir;
    }
    return $valid_dir;
}


############################################################################
# Print out the Error Messages and exit. (Local Subroutine)                #
############################################################################

sub error {

    # Localize the error variable.
    
    local($error) = $_[0];
    print "Content-type: text/html\n\n";

    # If the error is because of missing_required_fields, check for an 
    # error_template that was specified or print out a generic response.
    
    if ($error eq 'missing_required_fields') {
    
        # Prepare the error_fields config field so that users can use it 
        # in their templates.
        
        $CONFIG{'error_fields'} = "<UL>\n";
        foreach $missing_required_field (@missing_required_fields) {
            if ($ALT_NAME{$missing_required_field}) {
                $CONFIG{'error_fields'} .= "<LI>$ALT_NAME{$missing_required_field}\n";
            }
            else {
                $CONFIG{'error_fields'} .= "<LI>$missing_required_field\n";
            }
        }
        $CONFIG{'error_fields'} .= "</UL>";

        # If template, print out formatted template to user.
        
        if ($CONFIG{'error_html_template'} 
          && &valid_directory($CONFIG{'error_html_template'})) {
            if (!&parse_template($CONFIG{'error_html_template'}, *STDOUT)) {
                $error = "Can't open $CONFIG{'error_html_template'} ($!).";
            }
            else { exit }
        }
        
        # Otherwise print a generic response.
        
        else {
            print <<HTML_END;
<HTML>
   <HEAD>
      <TITLE>FormHandler Alert: Missing Required Fields</TITLE>
   </HEAD>
   <BODY BGCOLOR=#FFFFFF TEXT=#000000>
      <CENTER><H4>FormHandler Alert: Missing Required Fields</H4></CENTER>
      The following fields were not filled in when you submitted your form,
      but are required information.
      <P>
      <HR>
      <P>
      $CONFIG{'error_fields'}
      <BR>
      <HR>
      <P>
      Please use the <B>Back</B> button on your browser to return and
      complete the Form.
   </BODY>
</HTML>
HTML_END
        exit;
        }
    }
    
    # For any other errors, just print a title and heading which supplies 
    # the error.
    
    print <<HTML_END;
<HTML>
   <HEAD>
      <TITLE>$error</TITLE>
   </HEAD>
   <BODY BGCOLOR=#FFFFFF TEXT=#000000>
      <CENTER>
      <H4>$error</H4>
      </CENTER>
   </BODY>
</HTML>
HTML_END
    exit;
}
