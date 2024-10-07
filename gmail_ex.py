# Example usage for mod functions working with Gmail

import mod_email as mod
import creds

# Function that gets user information required for some choices later
def get_msg_info():
    info = {}
    print("Input email of sender")
    info['sender'] = input()
    print("Input recipient email")
    info['to'] = input()
    print("Input subject")
    info['subject'] = input()
    print ("Input message body")
    info['body'] = input()
    return info

gmail = creds.get_gmail_service() # Build Gmail service using creds.py

msg_list = [] # Hold each message built so they can be used for a draft or sent
msg_count = -1 # Track index of each message in msg_list
quit = False

# Loop until user decides to stop
while not quit:
    # Get user choice of action
    print("Make a selection\n"
        "(1) Create a message\n"
        "(2) Create a message with attachment\n"
        "(3) Create a draft\n"
        "(4) Send an email\n"
        "(5) Get an email\n"
        "(6) Read unread emails\n"
        "(7) Quit")
    choice = input()
    print()


    # Call mod_email function to make a message
    if choice == '1': 
        # Get required info from user
        info = get_msg_info()
        msg = mod.create_msg(info['sender'], info['to'], info['subject'], info['body'])
        # Increment msg_count and add message to end of msg_list
        msg_count += 1
        msg_list.append(msg)
        print("Message %d created\n" % msg_count)


    # Call mod_email function to make a message with an attachment
    elif choice == '2': 
        # Get required info from user
        info = get_msg_info()
        print("Input file name")
        file = input()
        msg = mod.create_msg_w_att(info['sender'], info['to'], info['subject'], info['body'], file)
        
        # Increment msg_count and add message to end of msg_list
        msg_count += 1
        msg_list.append(msg)
        print("Message %d created\n" % msg_count)


    # Call mod_email function to make a draft
    elif choice == '3':
        # Get required info from user
        print("Input number of message to make a draft")
        num = int(input())
        
        # Ensure number given is a valid index of msg_list
        if 0 <= num <= msg_count:
            mod.create_draft(gmail, 'me', msg_list[num])
            print("Draft created\n")
        else:
            print("Message number does not exist")


    # Call mod_email function to send an email
    elif choice == '4': 
        # Get required info from user
        print("Input number of the message to send")    
        num = int(input())
        
        # Ensure number given is a valid index of msg_list
        if 0 <= num <= msg_count:
            if mod.send_email(gmail, 'me', msg_list[num]):
                print("Email sent\n")
        else:
            print("Message number does not exist")


    # Call mod_email function to get an email from message ID
    elif choice == '5': 
        print("Input message ID of email to get")
        id = input()
        mod.get_email(gmail, 'me', id)


    # Call mod_email function to read unread emails
    elif choice == '6': 
        mod.read_unread_emails(gmail, 'me')

    # End program
    elif choice == '7': 
        quit = True

    # Handle invalid user input
    else: 
        print("Invalid input\n")

