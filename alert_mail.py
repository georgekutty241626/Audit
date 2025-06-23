import smtplib
from email.message import EmailMessage
from google.cloud import storage


def send_email(sender, receiver, subject, df = None, df_message = None, attachment_path = None, path_message = None):
    """
    Definition : 
    sender (string) : sender_email_address
    receiver (list) : receiver_email_address. If receivers are more than one, then all addresses must be in a list.
    subject (string) : Subject of E-mail
    df (Dataframe) Optional : A python Dataframe
    df_message (string) Optional : Message corresponding to Dataframe, which is an parameter
    attachment_path (list of strings) Optional : GCS storage paths of the files
    path_message  (string) Optional :Message corresponding to  attachments
    returns (Boolean) : True in case of Success and False in case of Failure
    """

    try:
        msg = EmailMessage()
        if df is None:
            df = ''
        else:
            df = df.reset_index(drop=True)
            df = df.rename_axis('S.no', axis=1)
            df.index += 1
            df = df.to_html()
        if df_message == None:
            df_message = ''
        if path_message == None:
            path_message = ''
        
        HTMLFirst = """\
        <html>
        <head>
        <style>
        table {{
            width:auto;
            font-family:calibri;
        }}
        table, th, td {{
            border: 1px solid black;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 5px;
            text-align: left;
        }}
        th {{
        background-color: #4F81BD;
        }}
        </style>
        </head>
        <body style=\"font-family:calibri;\">
        <p>Hi Team,</p>
        <p>{0}</p>
        {1}
        <p>{2}</p>
        <p>If you have any questions, Please reach out to BIEIM OPS Team.<br><br>Thanks,<br>Southwire</p>
        </body>

        </html>
        """.format(df_message, df, path_message)
        msg.set_content(HTMLFirst, subtype='html')
        msg['subject'] = subject
        msg['From'] = sender
        msg['To'] = receiver


        if attachment_path != None:
            for path in attachment_path:
                client = storage.Client()
                bucket_name = path.split('/')[2]
                file_path = path.split('/',3)[-1]
                bucket = client.get_bucket(f'{bucket_name}')
                file_blob = bucket.get_blob(f'{file_path}')
                file_name = path.split('/')[-1]
                
                temp_file_path = f'/tmp/{file_name}'
                data =file_blob.download_to_filename(temp_file_path)

                with open(temp_file_path, 'rb') as f:
                    file_data = f.read()
                    file_name = f.name.split('/')[-1]
                msg.add_attachment(file_data, maintype = 'application', subtype = 'octet-stream', filename = file_name )

        with smtplib.SMTP("10.251.164.63" ,port=25) as server:
            server.ehlo()
            server.starttls()
            server.send_message(msg)
            print('Mail sent successfully!')
        return True
    except Exception as e:
        print(f'Exception : {e}')
        return False