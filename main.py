import os
import getpass
import json
import gradio as gr
from agents import GeneratorAgent, InterpreterAgent, ValidatorAgent

generator_sys_init = """You're a computer musicology expert, you mastered different music styles.
And you're going to provide chord progerssions according to the input music style, thanks."""

interpreter_sys_init = """You will be provided with unstructured chord progression data, and your task is to parse it into JSON format.
    The resopnse should contain JSON object only, no explaination.
    The resulting JSON object should be in this format:
    - The name(key) of the object is "progression", the value is a list contain measures.
    - Each measure should be an object.
    - Within the measures are the chord(s).
    Here's an example for a four-measure progression with one chord per measure:
    {{
        "progression": [
            {{
                "chords": ["Cmaj7"]
            }},
            {{
                "chords": ["F"]
            }},
            {{
                "chords": ["G"]
            }},
            {{
                "chords": ["C"]
            }}
        ]
    }}
    Here's an example for a four-measure progression with two chords per measure:
    {{
        "progression": [
            {{
                "chords": ["Cmaj7", "F"]
            }},
            {{
                "chords": ["G", "C"]
            }},
            {{
                "chords": ["G", "G"]
            }},
            {{
                "chords": ["C", "C"]
            }}
        ]
    }}
    Please follow the example."""

validator_sys_init = """You are a program that checks if a given JSON object fits the following requirements, and your task is to tell me true or false:
    - The name(key) of the object is "progression", the value is a list contain measures.
    - Each measure should be an object.
    - The key of each "measure" is "chords", and the value is a list contain chord name(s) and the list should not be empty.
    Here's an example for a correctly formated object:
    {{
        "progression": [
            {{
                "chords": ["Cmaj7"]
            }},
            {{
                "chords": ["F"]
            }},
            {{
                "chords": ["G"]
            }},
            {{
                "chords": ["C"]
            }}
        ]
    }}

    If the JSON object fits these requirements, respond with:
    {
        "validation": true,
        "errMsg": "Check OK."
    }
    Otherwise, respond with:
    {
        "validation": false,
        "errMsg": <replace with the error you find>
    }
    """


generator = GeneratorAgent("gpt-3.5-turbo-1106", generator_sys_init)
interpreter = InterpreterAgent("gpt-3.5-turbo-1106", interpreter_sys_init)
validator = ValidatorAgent("gpt-3.5-turbo-1106", validator_sys_init)

num_measures = 4
chords_per_measure = 1

def content_generation(input_content):
    # global content_history, num_measures, chords_per_measure
    # content_history = generator.content_history
    prompt_regulation_suffix = """
    . Generate chord progression follow the following requirements:
    Totally {num_measures} measures. As well as {chords_per_measure} chord(s) for one measure, for piano keyboard, chill, need some bassline.
    """.format(num_measures=num_measures, chords_per_measure=chords_per_measure)
    # Create prompt
    input_prompt = input_content + prompt_regulation_suffix

    response_g = generator(input_prompt)
    print("response generator:", response_g)
    # conetnt_object = json.loads(response)

    response_i = interpreter(response_g)
    print("response interpreter:", response_i)

    response_v = validator(response_i)
    print("response Validator:", response_v)

    conetnt_object = json.loads(response_i)

    return response_g, conetnt_object

def change_num_measures(n_measures):
    global num_measures
    num_measures = n_measures
    print(num_measures)


def change_chords_per_measure(n_chords):
    global chords_per_measure
    chords_per_measure = n_chords
    print(chords_per_measure)

def retry_chat():
    content = generator.retry_completion()
    return content

def undo_chat():
    generator.undo_completion()

def clear_chat():
    generator.clear_completion()

def main():
    if 'OPENAI_API_KEY' not in os.environ:
        os.environ['OPENAI_API_KEY'] = getpass.getpass('Please enter your API key: ')

    with gr.Blocks() as demo:
        with gr.Column():
            gr.Markdown(
            """
            # LLHarmonia AI Chord Generator.
            Generate any chord progression you wanted!!
            """
            )
            txt_1 = gr.Textbox(label="Prompt 1", placeholder="What is a chord progression?")
            txt_3 = gr.Textbox(value="", label="Response 1", lines=5)
            txt_4 = gr.JSON(label="Response 2")

            btn_1 = gr.Button(value="Ask")
            btn_1.click(content_generation, inputs=[txt_1], outputs=[txt_3, txt_4])

            with gr.Row():
                dd_1 = gr.Dropdown([2,3,4,5,6], label="Number of measures")
                dd_1.change(change_num_measures, dd_1)
                dd_2 = gr.Dropdown([1], label="Chords per measure")
                dd_2.change(change_chords_per_measure, dd_2)

            with gr.Row():
                btn_3 = gr.Button(value="🔁")
                btn_3.click(retry_chat, outputs=[txt_3])
                btn_4 = gr.Button(value="⬅️")
                btn_4.click(undo_chat)
                btn_5 = gr.ClearButton([txt_1, txt_3], value="🗑")
                btn_5.click(clear_chat)

    demo.launch(debug=True)

if __name__ == "__main__":
    main()
