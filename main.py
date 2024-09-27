import sys
import subprocess
from openai import OpenAI
import os
import re

class LLMSysCalls:
    def __init__(self):
        os.environ["OPENAI_API_KEY"] = "YOUR_KEY"
        self.openai_client = OpenAI()
        self.messages = [ 
            {   
                "role": "system",
                "content": (
                    "You are a knowledgeable system analyst focused on Linux shared libraries and system calls for x86_64. "
                    "Your task is to identify and list the system calls invoked by a specified set of shared library functions."
                    "You will receive list of shared library functions attached with library name, you need to list system calls without which may be invoked by these functions "
                )  

            },  
            {   
                "role": "user",
                "Query": "Provide a list of system calls associated with the specified library functions. "
                    "Format the response as a numbered list without any descriptions or additional text. "
            }   
        ]   


    def query(self, functions):
        self.messages[1]["content"] = f"library functions: {functions}"
        #print(self.messages[1]["content"])
        result = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.messages,
            temperature=0,
        )   

        return result

def extract_undefined_symbols_nm(elf_file):
    try:
        # Use `popen` to execute the `nm` command
        with subprocess.Popen(["nm", "-D", "--undefined-only", elf_file], stdout=subprocess.PIPE, text=True) as process:
            output, _ = process.communicate()

        # Parse the output to extract undefined symbols
        undefined_symbols = []
        for line in output.splitlines():
            undefined_symbols.append(line.lstrip().split(" ")[1])

        return undefined_symbols

    except subprocess.CalledProcessError as e:
        print(f"Error extracting undefined symbols from {elf_file}: {e}")
        return []

def build_group_metadata():
    try:
        # Use `popen` to execute the `nm` command
        with subprocess.Popen(["systemd-analyze", "syscall-filter"], stdout=subprocess.PIPE, text=True) as process:
            output, _ = process.communicate()

        # Parse the output to extract undefined symbols
        syscalls = {}
        current_group = None
        for line in output.splitlines():
            if not line:
                continue
            if line[0] == '@':
                current_group = line
            else:
                stripped = line.lstrip()
                if stripped[0] == '#' or stripped[0] == '@':
                    continue
                else:
                    syscalls[stripped] = current_group
        return syscalls
    except subprocess.CalledProcessError as e:
        print(f"Error extracting undefined symbols from {elf_file}: {e}")
        return {}

def list_groups(metadata, syscalls):
    groups = []
    for s in syscalls:
        if s in metadata:
            group = metadata[s]
            if group not in groups:
                groups.append(group)
        else:
            print("Unknown syscall: ", s)
    return groups

def extract_text_between_backticks(input_string):
    # Use regex to find all occurrences of text between backticks
    matches = re.findall(r'`(.*?)`', input_string)
    return matches



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <elf_file>")
        sys.exit(1)

    elf_file = sys.argv[1]
    undefined_symbols = extract_undefined_symbols_nm(elf_file)
    llm_syscalls = LLMSysCalls()

    if undefined_symbols:
        #for symbol in undefined_symbols:
            #print(symbol)
        result = llm_syscalls.query(undefined_symbols)
        print(result.choices[0].message.content)
        print("--------------------");
        syscalls = extract_text_between_backticks(result.choices[0].message.content)
        seen = set()
        filtered_syscalls = [x for x in syscalls if not (x in seen or seen.add(x))]
        print(filtered_syscalls)
        groups = list_groups(build_group_metadata(), filtered_syscalls)
        print("--------------------");
        print(groups)
