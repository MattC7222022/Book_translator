# Book_translator
A python script to use Ollama with Langchain to automatically translate entire books, as epub files.

This requires you have an Ollama LLM capable of language translation locally installed. You go to the top of the script, change the path, change the book name, and enter your Ollama model.

I recommend using a custom model following these instructions:
https://github.com/ollama/ollama/blob/main/docs/modelfile.md
Once you have a model file, create the model with this instruction:

ollama create translator -f PATH_TO_MODELFILE

Here is the modelfile I use:

FROM deepseek-r1:32b

PARAMETER num_ctx 8192

PARAMETER temperature 0.9

PARAMETER top_k 30

PARAMETER top_p .7

SYSTEM """You are a helpful translator. You translate whatever is given, and reply exclusively with the translated text in English, without any introductions or small talk. Proper nouns should be translated to English, if applicable. If you are unable to comply fully due to community standards, please simply reply 'Community standards'. Thank you!"""

Because most LLMs refuse to work with foul language, I also included a secondary backup abliterated LLM that the program calls if your LLM refuses to translate. This is translator2 in the script.

The program will automatically remove Deepseek's <Thought> content, if applicable. It's not perfect but pretty good, I found the results quite readable for entire books.

You want a context window of about 8192 so the program can digest entire sections at a time. For me, translating an entire book took about 30 hours.
