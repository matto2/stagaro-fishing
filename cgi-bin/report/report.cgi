#!/usr/bin/perl

# Name: Selena Sol's Guestbook
#
# Version: 3.0
#
# Last Modified: 08-01-96
#
# Copyright Info: This application was written by Selena Sol
#    (selena@eff.org, http://www.eff.org/~erict) having been inspired by
#    countless other Perl authors.  Feel free to copy, cite, reference,
#    sample, borrow, resell or plagiarize the contents.  However, if you
#    don't mind, please let me know where it goes so that I can at least
#    watch and take part in the development of the memes. Information
#    wants to be free, support public domain freware.  Donations are
#    appreciated and will be spent on further upgrades and other public
#    domain scripts.

#######################################################################
#                     Print Out the HTTP Header  .                    #
#######################################################################

# First, print out the HTTP header.  We'll output this quickly so that we
# will be able to do some of our debugging from the web and so that in
# the case of a bogged down server, we won't get timed-out.  Also, bypass
# the Perl buffer with the first line.

  $| = 1;
  print "Content-type: text/html\n\n";

#######################################################################
#                         Require Libraries                           #
#######################################################################

# First, get the customized information contained in the setup file. Then
# Use cgi-lib.pl to read the incoming form data.  cgi-lib.sol will be used
# to lock the guestbook while we manipulate it and mail-lib.pl will be
# used to send mail.

  require "./guestbook.setup";
  require "$cgi_lib_location";
  require "$cgi_sol_location";
  require "$mail_lib_location";

#######################################################################
#                        Gather Form Data.                            #
#######################################################################

# Use cgi-lib.pl to parse the incoming form data and tell cgi-lib to
# prepare that information in the associative array %form_data

  &ReadParse(*form_data);

#######################################################################
#                       Create Add Form                               #
#######################################################################

# Now determine what the client wants.  If $form_data{'action'} eq "add"
# (client clicked on a button somewhere) or (||) $ENV{'REQUEST_METHOD'}
# eq "post" (client is accessing this script for the first time as a
# link, not as a submit button) then it means that the client is asking
# to see the form to "add" an item to the guestbook.  We will use the
# subroutine add_form in the setup file to output the add form.

  if ($form_data{'action'} eq "add" || $ENV{'REQUEST_METHOD'} eq "GET")
    {
    &add_form_header;
    &output_add_form;
    exit;
    }

#######################################################################
#                       Get the Date                                  #
#######################################################################

# Use the get_date subroutine at the end of this script to get the
# current date and time so that we can use it in our output.

  $date = &get_date;

#######################################################################
#                    Modify Incoming Form Data                       #
#######################################################################

# Now check to see if we were asked to censor any particular words.
# First, create an array of form variables by accessing the "keys" of the
# associative array %form_data given to us by cgi-lib.pl.

   @form_variables = keys (%form_data);

# For every variable sent to us from the form, and for each word in our
# list of bad words, replace (=~ s/) any occurance, case insensitively
# (/gi) of the bad word ($word) with the word censored.
# $form_data{$variable} should be equal to what the client filled in in
# the input boxes...
#
# Further, if the admin has set allow_html to 0, (!= 1) it means that she
# does not want the users to be able to use HTML tags...so, delete them.

   foreach $variable (@form_variables)
     {
     foreach $word (@bad_words)
       {
       $form_data{$variable} =~ s/\b$word\b/censored/gi;
       }
     if ($allow_html != "yes")
       {
       $form_data{$variable} =~ s/<([^>]|\n)*>//g;
       }
     }

#######################################################################
#                   Check Required Fields for Data                    #
#######################################################################

# For every field that was defined in our list of required fields, check
# the form data to see if that variable has an empty value.  If so, jump to
# missing_required_field_data which is a subroutine at the end of this
# script passing as a parameter, the name of the field which was not filled
# out.

  foreach $field (@required_fields)
    {
    if ($form_data{$field} eq "" )
      {
      &missing_required_field_data($field);
      }
    }

#######################################################################
#                      Edit the Guestbook File                        #
#######################################################################

# First open the guestbook html file.  Then, read each of the lines in
# the guestbook file into an array called @LINES Then close the
# guestbook file.  Finally, set the variable $SIZE equal to the number of
# elements in the array (which is conveniently, the same number of lines in
# the guestbook file)

  open (FILE,"$guestbookreal") || &CgiDie ("I am sorry, but I was not
	able to find the HTML guestbook file defined by the variable
	guestbookreal in the setup file.  The current value I have is
	$guestbookreal.  please make sure the path and permissions are
	correct. (read)");

  @LINES=<FILE>;
  close(FILE);

  $SIZE=@LINES;

# Now open up the guestbook file again, but this time open it for
# writing...in fact we will overwrite the existing guestbook file with new
# data (>).  Howevre, we will lock the file so that no other instances of
# this script can manipulate the guestbook at the same time we are writing
# to it.

  &GetFileLock ("$guestbookreal.lock");
  open (GUEST,">$guestbookreal") || &CgiDie ("I am sorry, but I was not
        able to find the HTML guestbook file defined by the variable
        guestbookreal in the setup file.  The current value I have is
        $guestbookreal.  please make sure the path and permissions are
        correct. (write)");

# Now we are going to go through our @LINES array adding lines "back" to
# out guestbook file one by one, inserting the new entry along the way.
# For every line in the guestbook file (remember that $SIZE = number of
# lines) we'll assign the value of the line ($LINES[$i]) to the variable $_
# We'll start with the first line in the array ($i=0) and we'll end when
# we have gone through all of the lines ($i<=$SIZE) counting by one ($i++).
# We reference the array in the standard form $arrayname[$element_number]

  for ($i=0;$i<=$SIZE;$i++)
    {
    $_=$LINES[$i];

# Now, if the line happens to be <!--begin--> we know that we are going to
# need to add a new entry.  Thus, btw, it is essential that your
# guestbook.html have that line, all on its own somewhere in the body when
# you initialize your guestbook.

    if (/<!--begin-->/)
      {

# Let's add the entry.  First print <!--begin--> again so that we will be
# able to find the top of the guestbook again the next time.

      print GUEST "<!--begin-->\n";

# Now print out the guest's address if they submitted the values.

      if ( $form_data{'city'} )
        {
        print GUEST "<B>Location:</B> $form_data{'city'},";
        }

      if ( $form_data{'state'} )
        {
        print GUEST " $form_data{'state'}";
        }

      if ( $form_data{'country'} )
        {
        print GUEST " $form_data{'country'}<BR>\n";
        }
      else
       {
       print GUEST "<br>";
       }

# Finally, print up the date and the comments.

      print GUEST "<B>Date:</B> $date<BR>\n";

      print GUEST "<b>Current Report: </B><BLOCKQUOTE>$form_data{'report'}";
      print GUEST "</BLOCKQUOTE><HR>\n\n";
      }

# If the line was not <!--begin--> however, we should make sure to print
# up the line so that we retain all of the HTML that was in the guestbook
# before we added the entry.  Thus, the very long for loop will go
# through each line...it will print the header...and get all the way down
# through whatever HTML you've written until it gets to the guestbook
# entries which begin with a <!--begin-->.  It will then print the new
# entry and then print out all the old entries as well...When it gets to
# the end of the file, it's over.

    else
      {
      print GUEST $_;
     }
   }

# Close up the guestbook and release the lock file.

  close (GUEST);
  &ReleaseFileLock ("$guestbookreal.lock");

#######################################################################
#                  Send Email Note to the Admin                      #
#######################################################################

# Now prepare to email a note to the admin.  Rename $form_data{'email'}
# to $email_of_sender, and split up that email into its two components,
# the username and the email server.  Thus in selena@foobar.com, selena
# becomes username and eff.org becomes server.  We are going to need
# these values later when we send our email.

    $email_of_guest = "$form_data{'email'}";

# Now, if the admin has set the $mail to yes (admin wants to be mailed when
# someone enters a guestbook entry), then let's begin creating an email body.
# We'll store the body in the variable $email_body and we will
# continually append this variable by using .=

  if ($mail eq "yes")
    {

    $email_body .= "You have a new entry in your guestbook:\n\n";
    $email_body .= "------------------------------------------------------\n";
    $email_body .= "Name: $form_data{'realname'}\n";

# If the guest actually submitted values, write them too.

    if ($form_data{'email'} ne "")
      {
      $email_body .="Email: <$form_data{'email'}>\n";
      }

    if ($form_data{'url'} ne "")
      {
      $email_body .="URL: <$form_data{'url'}>\n";
      }

    if ($form_data{'city'} ne "")
      {
      $email_body .= "Location: $form_data{'city'},";
      }

   if ($form_data{'state'} ne "")
      {
      $email_body .= " $form_data{'state'}";
      }

   if ($form_data{'country'} ne "")
      {
      $email_body .= " $form_data{'country'}\n";
      }

# Finish off the message body...

   $email_body .= "Time: $date\n\n";
   $email_body .= "Comments: $form_data{'comments'}\n";

   $email_body .= "------------------------------------------------------\n";

# Use the send_mail subroutine in the mail-lib.pl library file to send
# the email to the admin.  This routine takes 6 parameters, who is sending
# the mail, the server of the sender, who it is being sent to and their
# server, the subject and the body.

   &send_mail("$email_of_guest", "$recipient",
              "$email_subject", "$email_body");
   }

#######################################################################
#                  Send Thank You Email to the Guest                  #
#######################################################################

# Now, if the admin has set $remote_mail equal to yes and (&&) the guest has
# actually submitted an email, we should email the guest a thank you note
# also.  The process is identical to the one above.

  if ($remote_mail eq "yes" && $form_data{'email'} ne "")
    {
    $email_body = "";
    $email_body .= "$thank_you_email_text";
    $email_body .= "\n";
    $email_body .= "    By the way, you wrote...\n\n";
    $email_body .= "    Name: $form_data{'realname'}\n";

    if ($form_data{'email'} ne "")
      {
      $email_body .="    Email: <$form_data{'email'}>\n";
      }

    if ($form_data{'url'} ne "")
      {
      $email_body .="    URL: <$form_data{'url'}>\n";
      }

    if ($form_data{'city'} ne "")
      {
      $email_body .= "    Location: $form_data{'city'},";
      }

   if ($form_data{'state'} ne "")
      {
      $email_body .= " $form_data{'state'}";
      }

   if ($form_data{'country'} ne "")
      {
      $email_body .= " $form_data{'country'}\n";
      }

   $email_body .= "    Time: $date\n\n";
   $email_body .= "    Comments: $form_data{'comments'}\n";

# Send off the email!

   &send_mail("$recipient", "$email_of_guest",
              "$email_subject", "$email_body");
    }

#######################################################################
#                   Send back an HTML Thank you to Guest              #
#######################################################################

# Now send the guest a thank you note on the web and provide her with a
# way to get back to where she was before.

  &thank_you_html_header;

# Print out a copy of their submissions.

  if ($form_data{'url'} ne "")
    {
    print "<B>Name:</B>";
    print "<A HREF = \"$form_data{'url'}\">$form_data{'realname'}</A><BR>";
    }
  else
    {
    print "<B>Name:</B> $form_data{'realname'}<BR>";
    }

  if ( $form_data{'email'} )
    {
    if ($linkmail eq "yes")
      {
      print "<B>Email:</B> (<a href=\"mailto:$form_data{'email'}\">";
      print "$form_data{'email'}</a>)<BR>";
      }
    else
      {
      print "<B>Email:</B> ($form_data{'email'})<BR>";
      }
   }

   print "<B>Location:</B> ";

   if ( $form_data{'city'} )
     {
     print "$form_data{'city'},";
     }

   if ( $form_data{'state'} )
     {
     print " $form_data{'state'}";
     }

   if ( $form_data{'country'} ){
      print " $form_data{'country'}";
   }

   print qq!
   <BR>
   <B>Time:</B> $date
   <P>
   <B>Current Report: </B> $form_data{'report'}<BR>\n
   </BLOCKQUOTE>
   <A HREF = "$guestbookurl">Back to the Reports Page</A>
   - You MAY need to reload or refresh the page when you get there to see your
   entry.
   </BODY></HTML>!;
   exit;

# Begin the subroutines...

#######################################################################
#                 missing_required_field_data subroutine              #
#######################################################################

  sub missing_required_field_data
    {

# Assign the passed $variable parameter to the local variable $field

    local($field) = @_;

# Now send the user an informative error message so that they can enter
# the correct amount of information.

  &missing_required_field_note;

# Now reprint out the add form with the subroutine output_add_form at the
# end of this script.  Then exit.

    &output_add_form;
    exit;
    }

#######################################################################
#                            get_date                                 #
#######################################################################

  sub get_date
    {

   @days = ('Sunday','Monday','Tuesday','Wednesday','Thursday',
            'Friday','Saturday');
   @months = ('January','February','March','April','May','June','July',
              'August','September','October','November','December');

# Use the localtime command to get the current time, splitting it into
# variables.

   ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);

# Format the variables and assign them to the final $date variable.

   if ($hour < 10) { $hour = "0$hour"; }
   if ($min < 10) { $min = "0$min"; }
   if ($sec < 10) { $sec = "0$sec"; }

   $date = "$days[$wday], $months[$mon] $mday, 2024 at $hour\:$min\:$sec";
   }
