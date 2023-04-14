import json
import pandas as pd
from tqdm import tqdm
import json
import openai
import re
import string


def field_answer(page_path, data_path, saved_output_path, prompt_csv_data):
    
    with open(page_path) as file:
        page_data = json.load(file)
        
    with open(data_path) as file_2:
        data = json.load(file_2)
        
    fields_pages = {}
    
    for field in page_data:
        fields_pages[field] = list(set([page['page no.'] for page in page_data[field]]))
        
    prompt_df = pd.read_csv(prompt_csv_data)
    prompt_df = prompt_df[prompt_df['FOUND']=='Y']
    
    mismatch_dict = {
    }
    
    openai.api_key = ""
    
    out_dict = {}
    
    for key in tqdm(prompt_df['KEY'].values.tolist()):
        key_out = []

        if key in list(mismatch_dict.keys()):
            key_alt = mismatch_dict[key]
        else:
            key_alt = key

        for page_num in fields_pages[key_alt]:
            content_str = ' '.join(data[page_num-1]['content'])

            key_prompt = json.loads(prompt_df[prompt_df['KEY']==key]['PROMPT_DICT'].iloc[0])

            # Generate an answer using gpt-3.5-turbo
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": key_prompt['SYSTEM']},
                    {"role": "user", "content":f"""
                    Content: {content_str}
                    Conclusion: {key_prompt['USER']}"""}
                ],
                temperature=0.5,
                max_tokens=10,
            )

            # Extract the generated answer from the API response
            answer = response.choices[0].message.content.strip()

            key_out.append({"Page":page_num,"Question": key_prompt['USER'], "Answer": answer})

        out_dict[key] = key_out
        
    out_2_dict = {}

    for key in out_dict.keys():
        ans = set([i['Answer'].strip('.') for i in out_dict[key]])
        if len(ans) > 1:
            try:
                ans.remove('N/A')
            except:
                pass
        out_2_dict[key] = list(ans)
        
    with open(saved_output_path, "w", encoding="utf8") as output_file:
        json.dump(out_2_dict, output_file, indent=4)
        

page_path = ""
data_path = ""
saved_output_path = ""
prompt_csv_data = ""

field_answer(page_path, data_path, saved_output_path, prompt_csv_data)