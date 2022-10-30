import app
import config
import pandas as pd
def main():
    contact_list = ["Archive","AWM testing"]*5
    # contact_list= read_excel()
    messages = [
        {"text": r"testing 123",
        "image": r"/Users/siddhant/Documents/Misc/Palak/AWM/largeimage2.jpg"
        },
        {
            "text" : r"testing testing 321"
        }
        ]
    app.send_messages(contact_list=contact_list, messages=messages, options=config.options)

def read_excel():
    contacts = pd.read_excel('./LIONS PHONE NUMBER.xlsx')
    return contacts['number'].values.tolist()

if __name__ == '__main__':
    main()
 