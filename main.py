import streamlit as st
import pandas as pd
import joblib
import re
import io
import base64

# Function to clean and extract words from a text file
def extract_words_from_txt(uploaded_file):
    text = uploaded_file.read().decode('utf-8')
    cleaned_text = re.sub(r'[^a-zA-Z\s]', '', text).lower()
    words = cleaned_text.split()
    return words, text

# Function to compare words from the text file with column names in the Excel file
def compare_and_update_excel(txt_words, full_text, input_excel, output_excel):
    df = pd.read_excel(input_excel)
    word_columns = df.columns[1:-6]
    word_counts = {word: 0 for word in word_columns}

    for word in txt_words:
        if word in word_counts:
            word_counts[word] += 1

    email_length = len(full_text)
    word_count = len(txt_words)

    word_counts.update({'email_length': email_length, 
                        'word_count': word_count})

    new_row = pd.DataFrame([word_counts])
    df = pd.concat([df, new_row], ignore_index=True)

    df.fillna(0, inplace=True)

    df.to_excel(output_excel, index=False)

# Function to load the spam classification model and make predictions
def load_and_predict_model(input_excel, output_excel):
    model = joblib.load('spam_classification_model.joblib')
    df = pd.read_excel(input_excel)
    predictions = model.predict(df)
    df['is_spam'] = predictions

    df.to_excel(output_excel, index=False)

# File upload for the text file
st.sidebar.header('Upload Text File')
txt_file = st.sidebar.file_uploader('Upload a Text File', type=['txt'])

if txt_file is not None:
    st.sidebar.text('Text File Uploaded Successfully!')
    txt_words, full_text = extract_words_from_txt(txt_file)

    # Button to process the text file and update Excel
    if st.sidebar.button('Process Text File'):
        st.sidebar.text('Processing Text File...')

        input_excel_file = 'updated_file.xlsx'
        output_excel_file = 'updated_with_predictions.xlsx'

        compare_and_update_excel(txt_words, full_text, input_excel_file, output_excel_file)
        load_and_predict_model(output_excel_file, output_excel_file)

        st.sidebar.text('Processing Completed!')

        # Provide a download link for the updated Excel file
        st.sidebar.text('Download Updated Excel File:')
        with open(output_excel_file, 'rb') as excel_file:
            excel_data = excel_file.read()
            base64_encoded = base64.b64encode(excel_data).decode()
            st.sidebar.markdown(f"[Download {output_excel_file}](data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64_encoded})")

# Main content area
st.write("## Email Processing and Spam Classification")

if 'output_excel_file' in locals():
    st.write("### Predicted Emails:")
    df = pd.read_excel(output_excel_file)
    st.dataframe(df)

    st.write("### Spam Classification:")
    st.write("1: Spam Emails")
    st.write("0: Not Spam Emails")
    st.write(df[['is_spam']])

st.sidebar.text('The File Preview is showen in the Right Side')
