import logging
from abc import ABC, abstractmethod

from agentless.repair.repair import construct_topn_file_context
from agentless.util.compress_file import get_skeleton
from agentless.util.postprocess_data import extract_code_blocks, extract_locs_for_files
from agentless.util.preprocess_data import (
    get_full_file_paths_and_classes_and_functions,
    get_repo_files,
    line_wrap_content,
    show_project_structure,
)


class FL(ABC):
    def __init__(self, instance_id, structure, problem_statement, **kwargs):
        self.structure = structure
        self.instance_id = instance_id
        self.problem_statement = problem_statement

    @abstractmethod
    def localize(self, top_n=1, mock=False) -> tuple[list, list, list, any]:
        pass


class LLMFL(FL):
    
    def __init__(self, instance_id, structure, problem_statement, **kwargs):
        super().__init__(instance_id, structure, problem_statement)
        self.max_tokens = 300

    def _parse_model_return_lines(self, content: str) -> list[str]:
        return content.strip().split("\n")

    def localize(self, top_n=1, mock=False) -> tuple[list, list, list, any]:

        found_files = []

        # lazy import, not sure if this is actually better?
        from agentless.util.api_requests import (
            create_chatgpt_config,
            num_tokens_from_messages,
            request_chatgpt_engine,
        )

        message = self.obtain_relevant_files_prompt.format(
            problem_statement=self.problem_statement,
            structure=show_project_structure(self.structure).strip(),
        ).strip()
        print(f"prompting with message:\n{message}")
        print("=" * 80)
        if mock:
            traj = {
                "prompt": message,
                "usage": {
                    "prompt_tokens": num_tokens_from_messages(
                        message, "gpt-4o-2024-05-13"
                    ),
                },
            }
            return [], {"raw_output_loc": ""}, traj

        config = create_chatgpt_config(
            message=message,
            max_tokens=self.max_tokens,
            temperature=0,
            batch_size=1,
            model="gpt-4o-2024-05-13",  # use gpt-4o for now.
        )
        ret = request_chatgpt_engine(config)
        raw_output = ret.choices[0].message.content
        traj = {
            "prompt": message,
            "response": raw_output,
            "usage": {
                "prompt_tokens": ret.usage.prompt_tokens,
                "completion_tokens": ret.usage.completion_tokens,
            },
        }
        model_found_files = self._parse_model_return_lines(raw_output)

        files, classes, functions = get_full_file_paths_and_classes_and_functions(
            self.structure
        )

        for file_content in files:
            file = file_content[0]
            if file in model_found_files:
                found_files.append(file)

        # sort based on order of appearance in model_found_files
        found_files = sorted(found_files, key=lambda x: model_found_files.index(x))

        print(raw_output)

        return (
            found_files,
            {"raw_output_files": raw_output},
            traj,
        )

    def localize_function_for_files(
        self, file_names, mock=False
    ) -> tuple[list, dict, dict]:
        from agentless.util.api_requests import (
            create_chatgpt_config,
            num_tokens_from_messages,
            request_chatgpt_engine,
        )

        files, classes, functions = get_full_file_paths_and_classes_and_functions(
            self.structure
        )

        max_num_files = len(file_names)
        while 1:
            # added small fix to prevent too many tokens
            contents = []
            for file_name in file_names[:max_num_files]:
                for file_content in files:
                    if file_content[0] == file_name:
                        content = "\n".join(file_content[1])
                        file_content = line_wrap_content(content)
                        contents.append(
                            self.file_content_template.format(
                                file_name=file_name, file_content=file_content
                            )
                        )
                        break
                else:
                    raise ValueError(f"File {file_name} does not exist.")

            file_contents = "".join(contents)
            if num_tokens_from_messages(file_contents, "gpt-4o-2024-05-13") < 128000:
                break
            else:
                max_num_files -= 1

        message = self.obtain_relevant_code_combine_top_n_prompt.format(
            problem_statement=self.problem_statement,
            file_contents=file_contents,
        ).strip()
        print(f"prompting with message:\n{message}")
        print("=" * 80)
        if mock:
            traj = {
                "prompt": message,
                "usage": {
                    "prompt_tokens": num_tokens_from_messages(
                        message, "gpt-4o-2024-05-13"
                    ),
                },
            }
            return [], {"raw_output_loc": ""}, traj

        config = create_chatgpt_config(
            message=message,
            max_tokens=self.max_tokens,
            temperature=0,
            batch_size=1,
            model="gpt-4o-2024-05-13",  # use gpt-4o for now.
        )
        ret = request_chatgpt_engine(config)
        raw_output = ret.choices[0].message.content
        traj = {
            "prompt": message,
            "response": raw_output,
            "usage": {
                "prompt_tokens": ret.usage.prompt_tokens,
                "completion_tokens": ret.usage.completion_tokens,
            },
        }

        model_found_locs = extract_code_blocks(raw_output)
        model_found_locs_separated = extract_locs_for_files(
            model_found_locs, file_names
        )

        print(raw_output)

        return model_found_locs_separated, {"raw_output_loc": raw_output}, traj

    def localize_function_from_compressed_files(self, file_names, mock=False):
        from agentless.util.api_requests import (
            create_chatgpt_config,
            num_tokens_from_messages,
            request_chatgpt_engine,
        )

        file_contents = get_repo_files(self.structure, file_names)
        compressed_file_contents = {
            fn: get_skeleton(code) for fn, code in file_contents.items()
        }
        contents = [
            self.file_content_in_block_template.format(file_name=fn, file_content=code)
            for fn, code in compressed_file_contents.items()
        ]
        file_contents = "".join(contents)
        template = (
            self.obtain_relevant_functions_and_vars_from_compressed_files_prompt_more
        )
        message = template.format(
            problem_statement=self.problem_statement, file_contents=file_contents
        )
        assert num_tokens_from_messages(message, "gpt-4o-2024-05-13") < 128000
        logging.info(f"prompting with message:\n{message}")
        logging.info("=" * 80)

        if mock:
            traj = {
                "prompt": message,
                "usage": {
                    "prompt_tokens": num_tokens_from_messages(
                        message, "gpt-4o-2024-05-13"
                    ),
                },
            }
            return [], {"raw_output_loc": ""}, traj

        config = create_chatgpt_config(
            message=message,
            max_tokens=self.max_tokens,
            temperature=0,
            batch_size=1,
            model="gpt-4o-2024-05-13",  # use gpt-4o for now.
        )
        ret = request_chatgpt_engine(config)
        raw_output = ret.choices[0].message.content
        traj = {
            "prompt": message,
            "response": raw_output,
            "usage": {
                "prompt_tokens": ret.usage.prompt_tokens,
                "completion_tokens": ret.usage.completion_tokens,
            },
        }

        model_found_locs = extract_code_blocks(raw_output)
        model_found_locs_separated = extract_locs_for_files(
            model_found_locs, file_names
        )

        logging.info(f"==== raw output ====")
        logging.info(raw_output)
        logging.info("=" * 80)
        logging.info(f"==== extracted locs ====")
        for loc in model_found_locs_separated:
            logging.info(loc)
        logging.info("=" * 80)

        print(raw_output)

        return model_found_locs_separated, {"raw_output_loc": raw_output}, traj

    def localize_line_from_coarse_function_locs(
        self,
        file_names,
        coarse_locs,
        context_window: int,
        add_space: bool,
        sticky_scroll: bool,
        no_line_number: bool,
        temperature: float = 0.0,
        num_samples: int = 1,
        mock=False,
    ):
        from agentless.util.api_requests import (
            create_chatgpt_config,
            num_tokens_from_messages,
            request_chatgpt_engine,
        )

        file_contents = get_repo_files(self.structure, file_names)
        topn_content, file_loc_intervals = construct_topn_file_context(
            coarse_locs,
            file_names,
            file_contents,
            self.structure,
            context_window=context_window,
            loc_interval=True,
            add_space=add_space,
            sticky_scroll=sticky_scroll,
            no_line_number=no_line_number,
        )
        if no_line_number:
            template = self.obtain_relevant_code_combine_top_n_no_line_number_prompt
        else:
            template = self.obtain_relevant_code_combine_top_n_prompt
        message = template.format(
            problem_statement=self.problem_statement, file_contents=topn_content
        )
        logging.info(f"prompting with message:\n{message}")
        logging.info("=" * 80)
        assert num_tokens_from_messages(message, "gpt-4o-2024-05-13") < 128000
        if mock:
            traj = {
                "prompt": message,
                "usage": {
                    "prompt_tokens": num_tokens_from_messages(
                        message, "gpt-4o-2024-05-13"
                    ),
                },
            }
            return [], {"raw_output_loc": ""}, traj
        config = create_chatgpt_config(
            message=message,
            max_tokens=self.max_tokens,
            temperature=temperature,
            batch_size=num_samples,
            model="gpt-4o-2024-05-13",  # use gpt-4o for now.
        )
        ret = request_chatgpt_engine(config)
        raw_outputs = [choice.message.content for choice in ret.choices]
        traj = {
            "prompt": message,
            "response": raw_outputs,
            "usage": {
                "prompt_tokens": ret.usage.prompt_tokens,
                "completion_tokens": ret.usage.completion_tokens,
            },
        }
        model_found_locs_separated_in_samples = []
        for raw_output in raw_outputs:
            model_found_locs = extract_code_blocks(raw_output)
            model_found_locs_separated = extract_locs_for_files(
                model_found_locs, file_names
            )
            model_found_locs_separated_in_samples.append(model_found_locs_separated)

            logging.info(f"==== raw output ====")
            logging.info(raw_output)
            logging.info("=" * 80)
            print(raw_output)
            print("=" * 80)
            logging.info(f"==== extracted locs ====")
            for loc in model_found_locs_separated:
                logging.info(loc)
            logging.info("=" * 80)
        logging.info("==== Input coarse_locs")
        coarse_info = ""
        for fn, found_locs in coarse_locs.items():
            coarse_info += f"### {fn}\n"
            if isinstance(found_locs, str):
                coarse_info += found_locs + "\n"
            else:
                coarse_info += "\n".join(found_locs) + "\n"
        logging.info("\n" + coarse_info)
        if len(model_found_locs_separated_in_samples) == 1:
            model_found_locs_separated_in_samples = (
                model_found_locs_separated_in_samples[0]
            )

        return (
            model_found_locs_separated_in_samples,
            {"raw_output_loc": raw_outputs},
            traj,
        )
